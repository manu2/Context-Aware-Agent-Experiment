"""Task-independent operational scoring plus task oracle hook."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .models import ExecutionContract, ExecutionObservation


def score_execution(
    observation: ExecutionObservation,
    contract: ExecutionContract,
    correctness_oracle: Callable[[str], bool],
) -> dict[str, Any]:
    correct = observation.exit_code == 0 and correctness_oracle(observation.stdout)
    within_memory = observation.memory_peak_bytes is not None and observation.memory_peak_bytes <= contract.memory_max_bytes
    within_time = observation.program_time_seconds <= contract.wall_time_limit_seconds
    suitable = correct and within_memory and within_time and not observation.oom_killed and not observation.timed_out
    return {
        "correct": correct,
        "within_memory": within_memory,
        "within_time": within_time,
        "suitable": suitable,
        "memory_exceedance_bytes": None if observation.memory_peak_bytes is None else max(0, observation.memory_peak_bytes - contract.memory_max_bytes),
    }
