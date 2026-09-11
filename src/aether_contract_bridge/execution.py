"""Execution backend interfaces and the dedicated GCP Linux implementation."""

from __future__ import annotations

import base64
from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
from typing import Protocol

from .models import ExecutionContract, ExecutionObservation


class ExecutionBackend(Protocol):
    def run(self, program: str, contract: ExecutionContract) -> ExecutionObservation: ...


@dataclass
class GCloudLinuxExecutionBackend:
    project: str
    zone: str
    instance: str
    worker_local_path: Path
    worker_remote_path: str = "/home/manuagrawal/aether_execution_worker.py"

    def deploy(self) -> None:
        subprocess.run(
            ["gcloud", "compute", "scp", str(self.worker_local_path),
             f"{self.instance}:{self.worker_remote_path}", "--project", self.project,
             "--zone", self.zone, "--quiet"],
            check=True,
        )

    def run(self, program: str, contract: ExecutionContract) -> ExecutionObservation:
        contract.validate()
        request = {"program": program, "contract": contract.to_dict()}
        encoded = base64.urlsafe_b64encode(json.dumps(request).encode("utf-8")).decode("ascii")
        command = f"python3 {self.worker_remote_path} {encoded}"
        completed = subprocess.run(
            ["gcloud", "compute", "ssh", self.instance, "--project", self.project,
             "--zone", self.zone, "--quiet", "--command", command],
            check=False, capture_output=True, text=True,
        )
        if completed.returncode != 0:
            raise RuntimeError(f"remote worker transport failed: {completed.stderr.strip()}")
        payload = json.loads(completed.stdout)
        return ExecutionObservation(**payload)


@dataclass
class SSHLinuxExecutionBackend:
    """Direct SSH transport for the dedicated worker; avoids per-run cloud API calls."""

    host: str
    user: str
    identity_file: Path
    worker_local_path: Path
    worker_remote_path: str = "/home/manuagrawal/aether_execution_worker.py"
    remote_python: str = "/opt/aether-runtime/bin/python"
    assets: dict[str, str] | None = None

    def _ssh_options(self) -> list[str]:
        return ["-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes",
                "-o", "ConnectTimeout=15", "-i", str(self.identity_file)]

    def deploy(self) -> None:
        subprocess.run(
            ["scp", *self._ssh_options(), str(self.worker_local_path),
             f"{self.user}@{self.host}:{self.worker_remote_path}"], check=True,
        )

    def run(self, program: str, contract: ExecutionContract) -> ExecutionObservation:
        contract.validate()
        request = {
            "program": program,
            "contract": contract.to_dict(),
            "python_executable": self.remote_python,
            "assets": self.assets or {},
        }
        encoded = base64.urlsafe_b64encode(json.dumps(request).encode("utf-8")).decode("ascii")
        completed = subprocess.run(
            ["ssh", *self._ssh_options(), f"{self.user}@{self.host}",
             f"python3 {self.worker_remote_path} {encoded}"],
            check=False, capture_output=True, text=True,
        )
        if completed.returncode != 0:
            raise RuntimeError(f"remote worker transport failed: {completed.stderr.strip()}")
        return ExecutionObservation(**json.loads(completed.stdout))
