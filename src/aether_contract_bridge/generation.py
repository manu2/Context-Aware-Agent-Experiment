"""Generation interfaces and permanent replay/import backend."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Protocol

from .models import GenerationRecord


class GenerationBackend(Protocol):
    def generate(self, prompt: str) -> GenerationRecord: ...


def extract_python(response: str) -> str:
    blocks = re.findall(r"```(?:python)?\s*\n(.*?)```", response, flags=re.DOTALL | re.IGNORECASE)
    program = blocks[0] if blocks else response
    program = program.strip()
    if not program:
        raise ValueError("provider response contained no program")
    return program + "\n"


@dataclass
class ImportedResponseBackend:
    response: str
    source_label: str = "development_fixture"

    def generate(self, prompt: str) -> GenerationRecord:
        return GenerationRecord(
            backend="imported-response/v0.1",
            model="imported-development-only",
            raw_response=self.response,
            extracted_program=extract_python(self.response),
            request_metadata={"development_only": True, "source_label": self.source_label},
        )
