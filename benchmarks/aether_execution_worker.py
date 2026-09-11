#!/usr/bin/env python3
"""Linux worker: run one program in a fresh cgroup v2 and return JSON evidence."""

from __future__ import annotations

import base64
import json
import os
import pwd
import resource
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import time
import uuid


MAX_OUTPUT_BYTES = 1024 * 1024


def limit_output_files() -> None:
    resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_OUTPUT_BYTES, MAX_OUTPUT_BYTES))


def read_counts(path: Path) -> dict[str, int]:
    if not path.exists():
        return {}
    result = {}
    for line in path.read_text().splitlines():
        key, value = line.split()
        result[key] = int(value)
    return result


def read_cpu(path: Path) -> dict[str, int]:
    return read_counts(path)


def main() -> int:
    request = json.loads(base64.urlsafe_b64decode(sys.argv[1]).decode("utf-8"))
    contract = request["contract"]
    run_id = "aether-" + uuid.uuid4().hex[:12]
    cgroup = Path("/sys/fs/cgroup/aether-experiments") / run_id
    parent = cgroup.parent
    worker_started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="aether-run-") as temp:
        program = Path(temp) / "program.py"
        program.write_text(request["program"], encoding="utf-8")
        for name, source in request.get("assets", {}).items():
            if Path(name).name != name or not source.startswith("/opt/aether-data/"):
                raise ValueError("invalid asset mapping")
            source_path = Path(source)
            if not source_path.is_file():
                raise FileNotFoundError(source)
            (Path(temp) / name).symlink_to(source_path)
        subprocess.run(["sudo", "mkdir", "-p", str(parent)], check=True)
        # A fresh child receives controllers only when they are delegated by its
        # parent. This setup is idempotent on the dedicated worker.
        subprocess.run(
            ["sudo", "sh", "-c", f"echo '+memory +cpu +pids' > {shlex.quote(str(parent / 'cgroup.subtree_control'))}"],
            check=True,
        )
        subprocess.run(["sudo", "mkdir", str(cgroup)], check=True)
        try:
            subprocess.run(["sudo", "sh", "-c", f"echo {int(contract['memory_max_bytes'])} > {shlex.quote(str(cgroup / 'memory.max'))}"], check=True)
            subprocess.run(["sudo", "sh", "-c", f"echo 0 > {shlex.quote(str(cgroup / 'memory.swap.max'))}"], check=True)
            subprocess.run(["sudo", "sh", "-c", f"echo 1 > {shlex.quote(str(cgroup / 'memory.oom.group'))}"], check=True)
            subprocess.run(["sudo", "sh", "-c", f"echo 64 > {shlex.quote(str(cgroup / 'pids.max'))}"], check=True)
            quota = max(1, int(float(contract["cpu_quota_cores"]) * 100000))
            subprocess.run(["sudo", "sh", "-c", f"echo '{quota} 100000' > {shlex.quote(str(cgroup / 'cpu.max'))}"], check=True)
            events_before = read_counts(cgroup / "memory.events")
            python_executable = request.get("python_executable", "python3")
            if python_executable not in {"python3", "/opt/aether-runtime/bin/python"}:
                raise ValueError("unapproved Python executable")
            runner = pwd.getpwnam("aether-runner")
            unprivileged_command = (
                f"cd {shlex.quote(temp)} && "
                f"exec {shlex.quote(python_executable)} {shlex.quote(str(program))}"
            )
            child_script = (
                f"echo $$ > {shlex.quote(str(cgroup / 'cgroup.procs'))}; "
                "exec unshare --net -- "
                f"setpriv --reuid={runner.pw_uid} --regid={runner.pw_gid} --clear-groups --no-new-privs "
                f"sh -c {shlex.quote(unprivileged_command)}"
            )
            started = time.monotonic()
            stdout_path, stderr_path = Path(temp) / "stdout.log", Path(temp) / "stderr.log"
            with stdout_path.open("w+b") as stdout_file, stderr_path.open("w+b") as stderr_file:
                subprocess.run(["sudo", "chown", "-R", f"{runner.pw_uid}:{runner.pw_gid}", temp], check=True)
                try:
                    completed = subprocess.run(
                        ["sudo", "sh", "-c", child_script], stdout=stdout_file, stderr=stderr_file,
                        timeout=float(contract["wall_time_limit_seconds"]), cwd="/",
                        env={"PATH": os.environ.get("PATH", ""), "PYTHONHASHSEED": "0",
                             "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
                             "MKL_NUM_THREADS": "1", "VECLIB_MAXIMUM_THREADS": "1"},
                        preexec_fn=limit_output_files,
                    )
                    exit_code, timed_out = completed.returncode, False
                except subprocess.TimeoutExpired:
                    subprocess.run(["sudo", "sh", "-c", f"cat {shlex.quote(str(cgroup / 'cgroup.procs'))} | xargs -r kill -KILL"], check=False)
                    exit_code, timed_out = 124, True
                stdout_file.flush()
                stderr_file.flush()
                stdout_size, stderr_size = os.fstat(stdout_file.fileno()).st_size, os.fstat(stderr_file.fileno()).st_size
                stdout_file.seek(0)
                stderr_file.seek(0)
                stdout = stdout_file.read().decode("utf-8", errors="replace")
                stderr = stderr_file.read().decode("utf-8", errors="replace")
            program_time = time.monotonic() - started
            events_after = read_counts(cgroup / "memory.events")
            peak_text = (cgroup / "memory.peak").read_text().strip()
            peak = int(peak_text) if peak_text and peak_text != "max" else None
            cpu_stat = read_cpu(cgroup / "cpu.stat")
            oom = events_after.get("oom_kill", 0) > events_before.get("oom_kill", 0)
            result = {
                "backend": "gcp-cgroupv2/v0.1", "platform": os.uname().sysname + " " + os.uname().release,
                "exit_code": exit_code, "timed_out": timed_out, "oom_killed": oom,
                "stdout": stdout, "stderr": stderr, "program_time_seconds": program_time,
                "stdout_truncated": stdout_size >= MAX_OUTPUT_BYTES,
                "stderr_truncated": stderr_size >= MAX_OUTPUT_BYTES,
                "worker_time_seconds": time.monotonic() - worker_started,
                "memory_peak_bytes": peak, "memory_events_before": events_before,
                "memory_events_after": events_after, "cpu_stat": cpu_stat,
                "psi_memory": Path("/proc/pressure/memory").read_text() if Path("/proc/pressure/memory").exists() else None,
                "psi_cpu": Path("/proc/pressure/cpu").read_text() if Path("/proc/pressure/cpu").exists() else None,
            }
            print(json.dumps(result, sort_keys=True))
        finally:
            subprocess.run(["sudo", "chown", "-R", f"{os.getuid()}:{os.getgid()}", temp], check=False,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["sudo", "rmdir", str(cgroup)], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
