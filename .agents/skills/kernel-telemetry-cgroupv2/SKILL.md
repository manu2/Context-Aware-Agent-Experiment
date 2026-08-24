---
name: kernel-telemetry-cgroupv2
description: >-
  Linux kernel telemetry, cgroup v2 resource control, and execution sandbox enforcement.
  Use when configuring systemd-run MemoryMax/MemorySwapMax, reading cgroup memory.events/cpu.stat,
  auditing unprivileged user slice controller delegation, and capturing OS pressure stall information (PSI).
---

# Linux Kernel Telemetry & cgroup v2 Sandbox Specification

This skill details how to configure, monitor, and enforce OS-level hardware sandboxing for AI agent execution harnesses using Linux `cgroup v2`.

---

## 1. cgroup v2 Memory Enforcement

### 1.1 Enforcement Flags (`systemd-run`)
To create a strict, deterministic memory ceiling:
```bash
systemd-run --scope --unit=<unit_name> -q \
    -p MemoryMax=128M \
    -p MemorySwapMax=0 \
    python3 script.py
```
- `MemoryMax=128M`: Hard memory ceiling. Exceeding this forces kernel cgroup OOM killer to terminate processes in the scope unit (`SIGKILL` Exit 137).
- `MemorySwapMax=0`: Disables swap usage entirely, preventing memory-heavy allocations from swapping to disk and masking memory bottlenecks.

### 1.2 User Slice Delegation Audit
In Ubuntu 24.04 LTS:
- Systemd user delegation allows non-root users to invoke `systemd-run --user`.
- Test user delegation: `systemd-run --user --scope -p MemoryMax=128M -p MemorySwapMax=0 python3 -c "data=bytearray(150*1024*1024)"`
- If return code is `137` or `-9`, unprivileged delegation is active.
- If return code is non-137 or fails with bus connection errors, fall back to `sudo systemd-run`.

---

## 2. Real-Time Kernel Telemetry Signals

### 2.1 `memory.events.local` & `memory.events`
Located at `/sys/fs/cgroup/<unit>/memory.events`:
- `low`: Process breached `MemoryLow` threshold (soft threshold).
- `high`: Process breached `MemoryHigh` threshold (proactive warning signal before OOM kill!).
- `max`: Process reached `MemoryMax` limit.
- `oom`: Kernel triggered Out-Of-Memory subsystem.
- `oom_kill`: Process killed by SIGKILL Exit 137.

### 2.2 Pressure Stall Information (PSI)
Located at `/sys/fs/cgroup/<unit>/memory.pressure` and `/sys/fs/cgroup/<unit>/cpu.pressure`:
- Tracks percentage of wall-clock time tasks were stalled waiting for RAM or CPU allocation.
- High `some` or `full` memory pressure signals impending OOM thrashing.
