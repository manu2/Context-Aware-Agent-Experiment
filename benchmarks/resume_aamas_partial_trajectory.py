#!/usr/bin/env python3
"""Resume one trajectory interrupted by a provider error between attempts.

This recovery path is deliberately narrow: attempt 1 must already be fully
archived, the model-generated repair prompt must exist, and no attempt-2 model
response may exist. The interrupted summary is preserved before completion.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aether_contract_bridge.agent_loop import AgentLoop
from aether_contract_bridge.execution import SSHLinuxExecutionBackend
from aether_contract_bridge.models import RawSubstrateEvidence, canonical_json
from aether_contract_bridge.provider import BudgetLedger, ProviderRequestError, load_dotenv
from aether_contract_bridge.scoring import score_execution
from aether_contract_bridge.strategy import classify_strategy

from run_aamas_e2_canary import generation_backend, oracle_for


BASE = ROOT / "experiments/09_aamas_contract_bridge"
PROTOCOL = BASE / "protocol"
CONFIRMATORY = BASE / "confirmatory"


def _write_artifact(directory: Path, name: str, content: str) -> None:
    (directory / name).write_text(content, encoding="utf-8")


def _append_event(directory: Path, kind: str, payload: dict) -> None:
    with (directory / "events.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(canonical_json({"kind": kind, "payload": payload}) + "\n")


def validate_interruption(directory: Path, manifest: dict) -> tuple[dict, dict, dict]:
    summary = json.loads((directory / "summary.json").read_text())
    snapshot = json.loads((directory / "trajectory_manifest.json").read_text())
    if summary.get("trajectory_id") != directory.name:
        raise RuntimeError("trajectory id does not match its archive directory")
    if summary.get("status") != "failed" or summary.get("error_type") != "ProviderRequestError":
        raise RuntimeError("trajectory is not a provider-interrupted failure")
    if "503" not in summary.get("error", ""):
        raise RuntimeError("only the observed HTTP 503 interruption is eligible")
    if len(summary.get("attempts", [])) != 1:
        raise RuntimeError("exactly one fully archived attempt is required")
    if summary["attempts"][0].get("decision", {}).get("stop") is not False:
        raise RuntimeError("attempt 1 did not authorize an execution-feedback repair")
    if snapshot.get("study_manifest") != manifest:
        raise RuntimeError("trajectory snapshot does not match the frozen manifest")
    if not (directory / "attempt_2_prompt.txt").is_file():
        raise RuntimeError("archived attempt-2 repair prompt is missing")
    forbidden = list(directory.glob("attempt_2_program.py")) + list(directory.glob("attempt_2_provider_response.json"))
    if forbidden:
        raise RuntimeError("attempt 2 already has generated provider artifacts")
    entry = snapshot["execution_entry"]
    if len(entry) != 4:
        raise RuntimeError("expected a four-field confirmatory execution entry")
    return summary, snapshot, {"family": entry[0], "instance": entry[1], "environment": entry[2], "condition": entry[3]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--trajectory", required=True)
    args = parser.parse_args()
    if Path(args.manifest).name != args.manifest or Path(args.trajectory).name != args.trajectory:
        parser.error("manifest and trajectory must be bare names")

    load_dotenv(ROOT / ".env")
    manifest = json.loads((PROTOCOL / args.manifest).read_text())
    directory = CONFIRMATORY / args.trajectory
    summary, snapshot, entry = validate_interruption(directory, manifest)

    task_files = manifest["task_files"]
    task_key = f"{entry['family']}_{entry['instance']}"
    spec = json.loads((PROTOCOL / "tasks" / task_files[task_key]).read_text())
    envelope = spec["environments"][entry["environment"]]
    evidence = RawSubstrateEvidence(
        schema_version="raw-substrate-evidence/v0.1",
        target_id=f"gcp-canary-{entry['family']}-{entry['environment']}",
        observed_at_utc=datetime.now(timezone.utc).isoformat(),
        source="frozen-canary-contract",
        memory_max_bytes=envelope["memory_mib"] * 1024 * 1024,
        cpu_quota_cores=envelope["cpu_cores"],
        wall_time_limit_seconds=envelope["wall_seconds"],
        runtime="CPython 3.11.2",
        packages=("numpy==2.0.2", "pandas==2.2.3"),
    )
    ledger = BudgetLedger(
        CONFIRMATORY / manifest["budget_ledger_file"],
        hard_cap_usd=manifest["budget_usd"],
        max_calls=manifest["maximum_provider_calls"],
    )
    generation = generation_backend(manifest, ledger)
    execution = SSHLinuxExecutionBackend(
        host=args.host,
        user="manuagrawal",
        identity_file=Path.home() / ".ssh/google_compute_engine",
        worker_local_path=ROOT / "benchmarks/aether_execution_worker.py",
        assets={spec["asset"]["name"]: f"/opt/aether-data/{spec['asset']['name']}"},
    )
    execution.deploy()

    interrupted_path = directory / "infrastructure_interruption_summary.json"
    if not interrupted_path.exists():
        interrupted_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    prompt = (directory / "attempt_2_prompt.txt").read_text()
    started = monotonic()
    try:
        result = generation.generate(prompt)
        _append_event(directory, "generation", {"attempt": 2, "backend": result.backend,
                      "model": result.model, "request_metadata": result.request_metadata,
                      "infrastructure_resume": True})
        _write_artifact(directory, "attempt_2_raw_response.txt", result.raw_response)
        if result.raw_provider_payload is not None:
            _write_artifact(directory, "attempt_2_provider_response.json", result.raw_provider_payload)
        _write_artifact(directory, "attempt_2_program.py", result.extracted_program)
        strategy = classify_strategy(entry["family"], result.extracted_program).to_dict()
        _write_artifact(directory, "attempt_2_strategy.json", json.dumps(strategy, indent=2, sort_keys=True) + "\n")
        _append_event(directory, "strategy_classified", {"attempt": 2, **strategy})
        observation = execution.run(result.extracted_program, evidence)
        _append_event(directory, "execution", {"attempt": 2, **observation.to_dict()})
        score = score_execution(observation, evidence_to_contract(evidence), oracle_for(entry["family"], spec))
        _append_event(directory, "score", {"attempt": 2, **score})
        decision = AgentLoop().decide(attempt=2, suitable=score["suitable"])
        decision_dict = {"stop": decision.stop, "reason": decision.reason}
        _append_event(directory, "agent_loop_decision", {"attempt": 2, **decision_dict})
        attempt = {
            "attempt": 2,
            "generation": {"backend": result.backend, "model": result.model,
                           "request_metadata": result.request_metadata},
            "execution": observation.to_dict(), "score": score,
            "strategy": strategy, "decision": decision_dict,
        }
        attempts = summary["attempts"] + [attempt]
        completed = {
            "schema_version": "trajectory-summary/v0.1",
            "trajectory_id": directory.name,
            "condition": entry["condition"],
            "status": "complete",
            "development_only": result.request_metadata.get("development_only", False),
            "model": result.model,
            "attempts": attempts,
            "first_pass_suitable": attempts[0]["score"]["suitable"],
            "final_suitable": score["suitable"],
            "attempt_count": 2,
            "execution": observation.to_dict(),
            "score": score,
            "agent_loop_decision": decision_dict,
            "end_to_end_time_seconds": summary.get("end_to_end_time_seconds", 0.0) + monotonic() - started,
            "infrastructure_resume": {
                "reason": "provider HTTP 503 between attempts",
                "interrupted_summary": interrupted_path.name,
                "repair_prompt_sha256": sha256(prompt.encode()).hexdigest(),
            },
        }
        (directory / "summary.json").write_text(json.dumps(completed, indent=2, sort_keys=True) + "\n")
    except ProviderRequestError as exc:
        _append_event(directory, "trajectory_resume_failure", {"error_type": type(exc).__name__, "error": str(exc)})
        raise
    print(json.dumps({"trajectory_id": directory.name, "status": "complete",
                      "first_pass_suitable": completed["first_pass_suitable"],
                      "final_suitable": completed["final_suitable"]}, indent=2))
    return 0


def evidence_to_contract(evidence: RawSubstrateEvidence):
    # Keep compilation identical to the original trajectory path.
    from aether_contract_bridge.compiler import ContractCompiler
    return ContractCompiler().compile(evidence)


if __name__ == "__main__":
    raise SystemExit(main())
