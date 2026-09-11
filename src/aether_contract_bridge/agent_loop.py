"""Frozen two-attempt stopping policy."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentLoopDecision:
    stop: bool
    reason: str


class AgentLoop:
    maximum_attempts = 2

    def decide(self, attempt: int, suitable: bool) -> AgentLoopDecision:
        if suitable:
            return AgentLoopDecision(True, "verified_suitable")
        if attempt >= self.maximum_attempts:
            return AgentLoopDecision(True, "attempt_limit")
        return AgentLoopDecision(False, "authentic_execution_feedback_required")
