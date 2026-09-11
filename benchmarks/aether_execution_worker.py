#!/usr/bin/env python3
"""Linux worker: run one program in a fresh cgroup v2 and return JSON evidence."""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import time
import uuid


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
        subprocess.run(["sudo", "mkdir", "-p", str(parent)], check=True)
        # A fresh child receives controllers only when they are delegated by its
        # parent. This setup is idempotent on the dedicated worker.
        subprocess.run(
            ["sudo", "sh", "-c", f"echo '+memory +cpu' > {shlex.quote(str(parent / 'cgroup.subtree_control'))}"],
            check=True,
        )
        subprocess.run(["sudo", "mkdir", str(cgroup)], check=True)
        try:
            subprocess.run(["sudo", "sh", "-c", f"echo {int(contract['memory_max_bytes'])} > {shlex.quote(str(cgroup / 'memory.max'))}"], check=True)
            subprocess.run(["sudo", "sh", "-c", f"echo 0 > {shlex.quote(str(cgroup / 'memory.swap.max'))}"], check=True)
            quota = max(1, int(float(contract["cpu_quota_cores"]) * 100000))
            subprocess.run(["sudo", "sh", "-c", f"echo '{quota} 100000' > {shlex.quote(str(cgroup / 'cpu.max'))}"], check=True)
            events_before = read_counts(cgroup / "memory.events")
            child_script = f"echo $$ > {shlex.quote(str(cgroup / 'cgroup.procs'))}; exec python3 {shlex.quote(str(program))}"
            started = time.monotonic()
            try:
                completed = subprocess.run(
                    ["sudo", "sh", "-c", child_script], capture_output=True, text=True,
                    timeout=float(contract["wall_time_limit_seconds"]), cwd=temp,
                    env={"PATH": os.environ.get("PATH", ""), "PYTHONHASHSEED": "0",
                         "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
                         "MKL_NUM_THREADS": "1", "VECLIB_MAXIMUM_THREADS": "1"},
                )
                exit_code, timed_out = completed.returncode, False
                stdout, stderr = completed.stdout, completed.stderr
            except subprocess.TimeoutExpired as exc:
                subprocess.run(["sudo", "sh", "-c", f"cat {shlex.quote(str(cgroup / 'cgroup.procs'))} | xargs -r kill -KILL"], check=False)
                exit_code, timed_out = 124, True
                stdout = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
                stderr = exc.stderr.decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "")
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
                "worker_time_seconds": time.monotonic() - worker_started,
                "memory_peak_bytes": peak, "memory_events_before": events_before,
                "memory_events_after": events_after, "cpu_stat": cpu_stat,
                "psi_memory": Path("/proc/pressure/memory").read_text() if Path("/proc/pressure/memory").exists() else None,
                "psi_cpu": Path("/proc/pressure/cpu").read_text() if Path("/proc/pressure/cpu").exists() else None,
            }
            print(json.dumps(result, sort_keys=True))
        finally:
            subprocess.run(["sudo", "rmdir", str(cgroup)], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
