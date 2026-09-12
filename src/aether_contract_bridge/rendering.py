"""Frozen condition renderer; only the declared treatment differs."""

from .models import ExecutionContract


class ContractRenderer:
    CONDITIONS = {"P", "R", "G", "L"}

    @staticmethod
    def contract_block(contract: ExecutionContract, heading: str = "TARGET EXECUTION CONTRACT") -> str:
        """Render the versioned contract identically wherever it is disclosed."""
        contract.validate()
        mib = contract.memory_max_bytes / (1024 * 1024)
        packages = ", ".join(contract.packages) if contract.packages else "standard library only"
        return (
            f"{heading}\n"
            f"- Peak process memory limit: {mib:g} MiB\n"
            f"- Program wall-time limit: {contract.wall_time_limit_seconds:g} seconds\n"
            f"- CPU quota: {contract.cpu_quota_cores:g} cores\n"
            f"- Runtime: {contract.runtime}\n"
            f"- Available packages: {packages}\n"
            "Select an implementation suited to this operating envelope."
        )

    def render(self, task: str, condition: str, contract: ExecutionContract) -> str:
        contract.validate()
        if condition not in self.CONDITIONS:
            raise ValueError(f"unknown condition: {condition}")
        if condition == "P":
            treatment = "\n\n" + self.contract_block(contract)
        elif condition == "G":
            treatment = (
                "\n\nGenerate an efficient implementation. Balance memory use and execution time, "
                "and avoid unnecessary materialization or work."
            )
        else:  # R and L are identical before the first execution.
            treatment = ""
        return task.rstrip() + treatment + "\n\nReturn only one complete Python program."
