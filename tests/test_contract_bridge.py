from __future__ import annotations

import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aether_contract_bridge.compiler import ContractCompiler
from aether_contract_bridge.agent_loop import AgentLoop
from aether_contract_bridge.generation import ImportedResponseBackend, extract_python
from aether_contract_bridge.models import RawSubstrateEvidence
from aether_contract_bridge.rendering import ContractRenderer


def evidence() -> RawSubstrateEvidence:
    return RawSubstrateEvidence(
        schema_version="raw-substrate-evidence/v0.1", target_id="fixture-linux",
        observed_at_utc="2026-09-11T00:00:00Z", source="fixture",
        memory_max_bytes=128 * 1024 * 1024, cpu_quota_cores=1,
        wall_time_limit_seconds=10, runtime="CPython 3.11",
        packages=("numpy==2.0.2",),
    )


class ContractBridgeTests(unittest.TestCase):
    def test_compilation_is_deterministic(self):
        compiler = ContractCompiler()
        self.assertEqual(compiler.compile(evidence()), compiler.compile(evidence()))

    def test_conditions_have_only_declared_difference(self):
        contract = ContractCompiler().compile(evidence())
        renderer = ContractRenderer()
        p = renderer.render("Compute X.", "P", contract)
        r = renderer.render("Compute X.", "R", contract)
        g = renderer.render("Compute X.", "G", contract)
        self.assertIn("128 MiB", p)
        self.assertNotIn("128 MiB", r)
        self.assertIn("Balance memory use", g)

    def test_imported_backend_preserves_raw_response(self):
        raw = "```python\nprint('OK')\n```"
        record = ImportedResponseBackend(raw).generate("ignored")
        self.assertEqual(record.raw_response, raw)
        self.assertEqual(record.extracted_program, "print('OK')\n")
        self.assertTrue(record.request_metadata["development_only"])

    def test_empty_response_fails_closed(self):
        with self.assertRaises(ValueError):
            extract_python("   ")

    def test_agent_loop_stops_or_requests_one_repair(self):
        loop = AgentLoop()
        self.assertFalse(loop.decide(1, False).stop)
        self.assertTrue(loop.decide(1, True).stop)
        self.assertTrue(loop.decide(2, False).stop)


if __name__ == "__main__":
    unittest.main()
