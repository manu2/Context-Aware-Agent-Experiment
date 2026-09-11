"""Target inspection boundary used by concrete substrate adapters."""

from dataclasses import dataclass
from typing import Protocol

from .models import RawSubstrateEvidence


class SubstrateTargetAdapter(Protocol):
    def inspect(self) -> RawSubstrateEvidence: ...


@dataclass(frozen=True)
class StaticEvidenceAdapter:
    """Fixture/replay adapter; empirical adapters must collect host evidence."""

    evidence: RawSubstrateEvidence

    def inspect(self) -> RawSubstrateEvidence:
        self.evidence.validate()
        return self.evidence
