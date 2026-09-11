"""One production-shaped generation-to-archive trajectory."""

from __future__ import annotations

from dataclasses import asdict
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
) -> Path:
    started = monotonic()
    recorder = TrajectoryRecorder(archive_root, trajectory_id)
    contract = ContractCompiler().compile(evidence)
    prompt = ContractRenderer().render(task, condition, contract)
    recorder.event("contract_compiled", {"evidence": evidence.to_dict(), "contract": contract.to_dict()})
    recorder.artifact("prompt.txt", prompt)
    generation = generation_backend.generate(prompt)
    recorder.event("generation", {"backend": generation.backend, "model": generation.model,
                                    "request_metadata": generation.request_metadata})
    recorder.artifact("raw_response.txt", generation.raw_response)
    recorder.artifact("program.py", generation.extracted_program)
    observation = execution_backend.run(generation.extracted_program, contract)
    recorder.event("execution", observation.to_dict())
    score = score_execution(observation, contract, correctness_oracle)
    recorder.event("score", score)
    decision = AgentLoop().decide(attempt=1, suitable=score["suitable"])
    recorder.event("agent_loop_decision", {"stop": decision.stop, "reason": decision.reason})
    return recorder.finalize({
        "schema_version": "trajectory-summary/v0.1",
        "trajectory_id": trajectory_id,
        "condition": condition,
        "development_only": generation.request_metadata.get("development_only", False),
        "generation": {"backend": generation.backend, "model": generation.model},
        "execution": observation.to_dict(),
        "score": score,
        "agent_loop_decision": {"stop": decision.stop, "reason": decision.reason},
        "end_to_end_time_seconds": monotonic() - started,
    })
