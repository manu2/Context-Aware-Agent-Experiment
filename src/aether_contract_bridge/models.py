"""Versioned records used by every development and empirical trajectory."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from hashlib import sha256
import json
from typing import Any


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def content_hash(value: Any) -> str:
    return "sha256:" + sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class RawSubstrateEvidence:
    schema_version: str
    target_id: str
    observed_at_utc: str
    source: str
    memory_max_bytes: int
    cpu_quota_cores: float
    wall_time_limit_seconds: float
    runtime: str
    packages: tuple[str, ...] = ()
    unavailable_fields: tuple[str, ...] = ()

    def validate(self) -> None:
        if self.schema_version != "raw-substrate-evidence/v0.1":
            raise ValueError("unsupported evidence schema")
        if not self.target_id or not self.source:
            raise ValueError("target_id and source are required")
        if self.memory_max_bytes <= 0 or self.cpu_quota_cores <= 0 or self.wall_time_limit_seconds <= 0:
            raise ValueError("resource limits must be positive")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExecutionContract:
    schema_version: str
    target_id: str
    memory_max_bytes: int
    cpu_quota_cores: float
    wall_time_limit_seconds: float
    runtime: str
    packages: tuple[str, ...]
    evidence_hash: str

    def validate(self) -> None:
        if self.schema_version != "execution-contract/v0.1":
            raise ValueError("unsupported contract schema")
        if not self.evidence_hash.startswith("sha256:"):
            raise ValueError("contract provenance hash is required")
        if self.memory_max_bytes <= 0 or self.cpu_quota_cores <= 0 or self.wall_time_limit_seconds <= 0:
            raise ValueError("resource limits must be positive")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GenerationRecord:
    backend: str
    model: str
    raw_response: str
    extracted_program: str
    request_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutionObservation:
    backend: str
    platform: str
    exit_code: int
    timed_out: bool
    oom_killed: bool
    stdout: str
    stderr: str
    program_time_seconds: float
    worker_time_seconds: float
    memory_peak_bytes: int | None
    memory_events_before: dict[str, int] = field(default_factory=dict)
    memory_events_after: dict[str, int] = field(default_factory=dict)
    cpu_stat: dict[str, int] = field(default_factory=dict)
    psi_memory: str | None = None
    psi_cpu: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
