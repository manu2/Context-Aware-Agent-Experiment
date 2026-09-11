"""Frozen condition renderer; only the declared treatment differs."""

from .models import ExecutionContract


class ContractRenderer:
    CONDITIONS = {"P", "R", "G"}

    def render(self, task: str, condition: str, contract: ExecutionContract) -> str:
        contract.validate()
        if condition not in self.CONDITIONS:
            raise ValueError(f"unknown condition: {condition}")
        if condition == "P":
            mib = contract.memory_max_bytes / (1024 * 1024)
            packages = ", ".join(contract.packages) if contract.packages else "standard library only"
            treatment = (
                "\n\nTARGET EXECUTION CONTRACT\n"
                f"- Peak process memory limit: {mib:g} MiB\n"
                f"- Program wall-time limit: {contract.wall_time_limit_seconds:g} seconds\n"
                f"- CPU quota: {contract.cpu_quota_cores:g} cores\n"
                f"- Runtime: {contract.runtime}\n"
                f"- Available packages: {packages}\n"
                "Select an implementation suited to this operating envelope."
            )
        elif condition == "G":
            treatment = (
                "\n\nGenerate an efficient implementation. Balance memory use and execution time, "
                "and avoid unnecessary materialization or work."
            )
        else:
            treatment = ""
        return task.rstrip() + treatment + "\n\nReturn only one complete Python program."
