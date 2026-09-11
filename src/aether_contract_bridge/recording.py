"""Append-only event and immutable summary writer."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from .models import canonical_json


class TrajectoryRecorder:
    def __init__(self, root: Path, trajectory_id: str) -> None:
        self.directory = root / trajectory_id
        self.directory.mkdir(parents=True, exist_ok=False)
        self._events = self.directory / "events.jsonl"

    def event(self, kind: str, payload: dict[str, Any]) -> None:
        record = {"kind": kind, "payload": payload}
        with self._events.open("a", encoding="utf-8") as handle:
            handle.write(canonical_json(record) + "\n")

    def artifact(self, name: str, content: str) -> dict[str, Any]:
        path = self.directory / name
        path.write_text(content, encoding="utf-8")
        digest = sha256(content.encode("utf-8")).hexdigest()
        return {"path": name, "sha256": digest, "bytes": len(content.encode("utf-8"))}

    def finalize(self, summary: dict[str, Any]) -> Path:
        path = self.directory / "summary.json"
        path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return path
