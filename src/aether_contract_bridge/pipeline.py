"""One production-shaped generation-to-archive trajectory."""

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
from time import monotonic
from typing import Callable

from .compiler import ContractCompiler
from .agent_loop import AgentLoop
from .execution import ExecutionBackend
from .generation import GenerationBackend
from .models import RawSubstrateEvidence
from .recording import TrajectoryRecorder
from .rendering import ContractRenderer
from .scoring import score_execution


def run_trajectory(
    *, trajectory_id: str, task: str, condition: str,
    evidence: RawSubstrateEvidence, generation_backend: GenerationBackend,
    execution_backend: ExecutionBackend, archive_root: Path,
    correctness_oracle: Callable[[str], bool],
    protocol_snapshot: dict | None = None,
    strategy_classifier: Callable[[str], dict] | None = None,
) -> Path:
    started = monotonic()
    recorder = TrajectoryRecorder(archive_root, trajectory_id)
    if protocol_snapshot is not None:
        recorder.artifact(
            "trajectory_manifest.json",
            json.dumps(protocol_snapshot, indent=2, sort_keys=True) + "\n",
        )
    contract = ContractCompiler().compile(evidence)
    prompt = ContractRenderer().render(task, condition, contract)
    recorder.event("contract_compiled", {"evidence": evidence.to_dict(), "contract": contract.to_dict()})
    recorder.artifact("prompt.txt", prompt)
    attempts = []
    active_prompt = prompt
    development_only = False
    model = "unknown"
    try:
        for attempt in (1, 2):
            generation = generation_backend.generate(active_prompt)
            model = generation.model
            development_only = generation.request_metadata.get("development_only", False)
            recorder.event("generation", {"attempt": attempt, "backend": generation.backend,
                                            "model": model, "request_metadata": generation.request_metadata})
            recorder.artifact(f"attempt_{attempt}_raw_response.txt", generation.raw_response)
            if generation.raw_provider_payload is not None:
                recorder.artifact(f"attempt_{attempt}_provider_response.json", generation.raw_provider_payload)
            recorder.artifact(f"attempt_{attempt}_program.py", generation.extracted_program)
            strategy = strategy_classifier(generation.extracted_program) if strategy_classifier else None
            if strategy is not None:
                recorder.artifact(f"attempt_{attempt}_strategy.json",
                                  json.dumps(strategy, indent=2, sort_keys=True) + "\n")
                recorder.event("strategy_classified", {"attempt": attempt, **strategy})
            observation = execution_backend.run(generation.extracted_program, contract)
            recorder.event("execution", {"attempt": attempt, **observation.to_dict()})
            score = score_execution(observation, contract, correctness_oracle)
            recorder.event("score", {"attempt": attempt, **score})
            decision = AgentLoop().decide(attempt=attempt, suitable=score["suitable"])
            recorder.event("agent_loop_decision", {"attempt": attempt, "stop": decision.stop,
                                                     "reason": decision.reason})
            attempts.append({"attempt": attempt, "generation": {"backend": generation.backend, "model": model,
                                                                  "request_metadata": generation.request_metadata},
                             "execution": observation.to_dict(), "score": score,
                             "strategy": strategy,
                             "decision": {"stop": decision.stop, "reason": decision.reason}})
            if decision.stop:
                break
            active_prompt = _recovery_prompt(prompt, observation)
            recorder.artifact("attempt_2_prompt.txt", active_prompt)
    except Exception as exc:
        recorder.event("trajectory_failure", {"error_type": type(exc).__name__, "error": str(exc)})
        recorder.finalize({"schema_version": "trajectory-summary/v0.1", "trajectory_id": trajectory_id,
                           "condition": condition, "status": "failed", "attempts": attempts,
                           "error_type": type(exc).__name__, "error": str(exc),
                           "end_to_end_time_seconds": monotonic() - started})
        raise
    final = attempts[-1]
    return recorder.finalize({
        "schema_version": "trajectory-summary/v0.1", "trajectory_id": trajectory_id,
        "condition": condition, "status": "complete", "development_only": development_only,
        "model": model, "attempts": attempts, "first_pass_suitable": attempts[0]["score"]["suitable"],
        "final_suitable": final["score"]["suitable"], "attempt_count": len(attempts),
        "execution": final["execution"], "score": final["score"],
        "agent_loop_decision": final["decision"], "end_to_end_time_seconds": monotonic() - started,
    })


def _recovery_prompt(original_prompt: str, observation) -> str:
    stderr = observation.stderr[-2000:]
    stdout = observation.stdout[-2000:]
    return (
        original_prompt.rstrip()
        + "\n\nAUTHENTIC FIRST EXECUTION OBSERVATION\n"
        + f"- Exit code: {observation.exit_code}\n"
        + f"- Timed out: {str(observation.timed_out).lower()}\n"
        + f"- Kernel OOM kill observed: {str(observation.oom_killed).lower()}\n"
        + f"- Stdout (tail): {stdout!r}\n"
        + f"- Stderr (tail): {stderr!r}\n"
        + "Revise the implementation using this execution evidence. Return only one complete Python program.\n"
    )
