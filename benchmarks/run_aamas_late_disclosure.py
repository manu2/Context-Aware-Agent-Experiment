#!/usr/bin/env python3
"""Run matched recovery branches from archived R first-attempt failures."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "benchmarks"))

from aether_contract_bridge.execution import SSHLinuxExecutionBackend
from aether_contract_bridge.models import ExecutionContract, ExecutionObservation, canonical_json
from aether_contract_bridge.pipeline import recovery_prompt
from aether_contract_bridge.provider import BudgetLedger, ProviderRequestError, load_dotenv
from aether_contract_bridge.recording import TrajectoryRecorder
from aether_contract_bridge.rendering import ContractRenderer
from aether_contract_bridge.scoring import score_execution
from aether_contract_bridge.strategy import classify_strategy
from run_aamas_e2_canary import generation_backend, oracle_for


def _sha256(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def load_source(source_root: Path, source_id: str) -> dict:
    directory = source_root / source_id
    summary = json.loads((directory / "summary.json").read_text())
    snapshot = json.loads((directory / "trajectory_manifest.json").read_text())
    events = [json.loads(line) for line in (directory / "events.jsonl").read_text().splitlines()]
    contract_dict = next(event for event in events if event["kind"] == "contract_compiled")["payload"]["contract"]
    contract = ExecutionContract(**{**contract_dict, "packages": tuple(contract_dict["packages"])})
    observation = ExecutionObservation(**summary["attempts"][0]["execution"])
    original_prompt = (directory / "prompt.txt").read_text()
    if summary.get("condition") != "R":
        raise ValueError(f"{source_id}: source condition is not R")
    if summary.get("first_pass_suitable") is not False:
        raise ValueError(f"{source_id}: first attempt is not an archived failure")
    if "TARGET EXECUTION CONTRACT" in original_prompt:
        raise ValueError(f"{source_id}: reactive source unexpectedly discloses the contract")
    task_spec = snapshot["task_spec"]
    family, instance, environment, condition = snapshot["execution_entry"]
    if condition != "R":
        raise ValueError(f"{source_id}: manifest condition is not R")
    return {
        "directory": directory, "summary": summary, "snapshot": snapshot,
        "contract": contract, "observation": observation, "original_prompt": original_prompt,
        "task_spec": task_spec, "family": family, "instance": instance, "environment": environment,
    }


def branch_prompt(source: dict, branch: str) -> str:
    if branch == "R_replay":
        return recovery_prompt(source["original_prompt"], source["observation"])
    if branch == "L":
        return recovery_prompt(
            source["original_prompt"], source["observation"], contract=source["contract"]
        )
    raise ValueError(f"unknown recovery branch: {branch}")


def validate_manifest(manifest: dict, source_root: Path) -> list[tuple[str, str, dict, str]]:
    order = manifest["execution_order"]
    if manifest.get("schema_version") != "aamas-late-disclosure/v1.0":
        raise ValueError("unsupported late-disclosure manifest schema")
    if manifest.get("status") != "frozen_before_calls":
        raise ValueError("manifest must be frozen_before_calls")
    if len(order) != len({tuple(entry) for entry in order}):
        raise ValueError("duplicate source/branch entry")
    prepared = []
    cache = {}
    for source_id, branch in order:
        source = cache.setdefault(source_id, load_source(source_root, source_id))
        prompt = branch_prompt(source, branch)
        prepared.append((source_id, branch, source, prompt))
    if len(order) > manifest["maximum_provider_calls"]:
        raise ValueError("execution order exceeds provider call cap")
    return prepared


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, help="JSON filename in the frozen protocol directory")
    parser.add_argument("--host", default=os.environ.get("AETHER_WORKER_HOST"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if Path(args.manifest).name != args.manifest or not args.manifest.endswith(".json"):
        parser.error("--manifest must be a JSON filename without directories")

    protocol_root = ROOT / "experiments/09_aamas_contract_bridge/protocol"
    manifest = json.loads((protocol_root / args.manifest).read_text())
    source_root = ROOT / "experiments/09_aamas_contract_bridge" / manifest["source_archive_subdir"]
    output_root = ROOT / "experiments/09_aamas_contract_bridge" / manifest["archive_subdir"]
    prepared = validate_manifest(manifest, source_root)
    dry_report = {
        "entries": len(prepared),
        "sources": len({entry[0] for entry in prepared}),
        "branches": sorted({entry[1] for entry in prepared}),
        "prompt_hashes": [
            {"source": source_id, "branch": branch, "sha256": _sha256(prompt)}
            for source_id, branch, _, prompt in prepared
        ],
    }
    if args.dry_run:
        print(json.dumps(dry_report, indent=2, sort_keys=True))
        return 0
    if not args.host:
        parser.error("--host or AETHER_WORKER_HOST is required for execution")

    load_dotenv(ROOT / ".env")
    output_root.mkdir(parents=True, exist_ok=True)
    ledger = BudgetLedger(
        output_root / manifest["budget_ledger_file"],
        hard_cap_usd=manifest["budget_usd"], max_calls=manifest["maximum_provider_calls"],
    )
    generation = generation_backend(manifest, ledger)
    execution = SSHLinuxExecutionBackend(
        host=args.host, user=manifest.get("worker_user", "manuagrawal"),
        identity_file=Path.home() / ".ssh/google_compute_engine",
        worker_local_path=ROOT / "benchmarks/aether_execution_worker.py",
        host_key_alias=manifest.get("worker_host_key_alias"),
        known_hosts_file=(Path.home() / ".ssh/google_compute_known_hosts")
        if manifest.get("worker_host_key_alias") else None,
    )
    execution.deploy()
    attempted = []
    prefix = manifest["run_id_prefix"]
    for index, (source_id, branch, source, prompt) in enumerate(prepared, 1):
        trajectory_id = f"{prefix}-{index:03d}-{branch}"
        directory = output_root / trajectory_id
        if directory.exists():
            attempted.append({"trajectory_id": trajectory_id, "status": "already_archived"})
            continue
        task_spec = source["task_spec"]
        asset_name = task_spec["asset"]["name"]
        execution.assets = {asset_name: f"/opt/aether-data/{asset_name}"}
        recorder = TrajectoryRecorder(output_root, trajectory_id)
        branch_manifest = {
            "study_manifest": manifest, "execution_index": index,
            "source_trajectory_id": source_id, "branch": branch,
            "source_first_attempt_execution_sha256": _sha256(canonical_json(source["observation"].to_dict())),
            "source_first_attempt_program_sha256": _sha256((source["directory"] / "attempt_1_program.py").read_text()),
            "task_spec": task_spec,
        }
        recorder.artifact("trajectory_manifest.json", json.dumps(branch_manifest, indent=2, sort_keys=True) + "\n")
        recorder.artifact("prompt.txt", prompt)
        recorder.event("matched_recovery_branch", {
            "source_trajectory_id": source_id, "branch": branch,
            "source_observation": source["observation"].to_dict(),
            "contract": source["contract"].to_dict(),
        })
        try:
            generated = generation.generate(prompt)
            recorder.event("generation", {"backend": generated.backend, "model": generated.model,
                                            "request_metadata": generated.request_metadata})
            recorder.artifact("raw_response.txt", generated.raw_response)
            if generated.raw_provider_payload is not None:
                recorder.artifact("provider_response.json", generated.raw_provider_payload)
            recorder.artifact("program.py", generated.extracted_program)
            strategy = classify_strategy(source["family"], generated.extracted_program).to_dict()
            recorder.artifact("strategy.json", json.dumps(strategy, indent=2, sort_keys=True) + "\n")
            observation = execution.run(generated.extracted_program, source["contract"])
            score = score_execution(observation, source["contract"], oracle_for(source["family"], task_spec))
            recorder.event("execution", observation.to_dict())
            recorder.event("score", score)
            summary = {
                "schema_version": "aamas-late-disclosure-summary/v1.0",
                "trajectory_id": trajectory_id, "source_trajectory_id": source_id,
                "branch": branch, "model": generated.model, "status": "complete",
                "family": source["family"], "instance": source["instance"],
                "environment": source["environment"], "execution": observation.to_dict(),
                "score": score, "strategy": strategy,
                "generation": {"backend": generated.backend, "request_metadata": generated.request_metadata},
            }
            recorder.finalize(summary)
            attempted.append({"trajectory_id": trajectory_id, "status": "complete", "suitable": score["suitable"]})
        except ProviderRequestError as exc:
            recorder.event("provider_failure", {"status_code": exc.status_code, "error": str(exc)})
            recorder.finalize({"schema_version": "aamas-late-disclosure-summary/v1.0",
                               "trajectory_id": trajectory_id, "source_trajectory_id": source_id,
                               "branch": branch, "status": "provider_failure", "error": str(exc)})
            attempted.append({"trajectory_id": trajectory_id, "status": "provider_failure", "error": str(exc)})
            break
    summaries = [json.loads(path.read_text()) for path in sorted(output_root.glob(prefix + "-*/summary.json"))]
    report = {
        "schema_version": "aamas-late-disclosure-report/v1.0",
        "updated_at_utc": datetime.now(timezone.utc).isoformat(), "attempted_this_invocation": attempted,
        "complete": sum(row.get("status") == "complete" for row in summaries),
        "suitable_by_branch": {
            branch: sum(row.get("status") == "complete" and row.get("branch") == branch and row["score"]["suitable"]
                        for row in summaries)
            for branch in ("R_replay", "L")
        },
        "summaries": summaries,
    }
    (output_root / f"{prefix}_report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: report[key] for key in ("complete", "suitable_by_branch")}, indent=2))
    return 0 if report["complete"] == len(prepared) else 1


if __name__ == "__main__":
    raise SystemExit(main())
