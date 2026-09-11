"""Deterministic projection of target evidence into model-visible contracts."""

from .models import ExecutionContract, RawSubstrateEvidence, content_hash


class ContractCompiler:
    def compile(self, evidence: RawSubstrateEvidence) -> ExecutionContract:
        evidence.validate()
        contract = ExecutionContract(
            schema_version="execution-contract/v0.1",
            target_id=evidence.target_id,
            memory_max_bytes=evidence.memory_max_bytes,
            cpu_quota_cores=evidence.cpu_quota_cores,
            wall_time_limit_seconds=evidence.wall_time_limit_seconds,
            runtime=evidence.runtime,
            packages=tuple(sorted(evidence.packages)),
            evidence_hash=content_hash(evidence.to_dict()),
        )
        contract.validate()
        return contract
