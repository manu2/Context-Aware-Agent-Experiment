#!/usr/bin/env python3
"""Build the deterministic anonymous AAMAS supplementary artifact."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re
import zipfile


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "paper/aamas2027"
OUTPUT = PACKAGE / "aamas2027_anonymous_supplement.zip"
FIXED_TIME = (2026, 9, 12, 0, 0, 0)

EXACT_FILES = (
    "requirements.txt",
    "LICENSE",
    "paper/aamas2027/SUPPLEMENT_README.md",
    "paper/aamas2027/AI_ASSISTANCE_DISCLOSURE.md",
    "docs/20_aamas_strategy_codebook.md",
    "docs/22_aamas_e4_protocol_freeze.md",
    "docs/23_aamas_e5_infrastructure_interruption.md",
    "docs/24_aamas_gemini_confirmatory_gate.md",
    "docs/25_aamas_claude_confirmatory_gate.md",
    "docs/26_aamas_confirmatory_completion_gate.md",
    "docs/27_aamas_gpt_infrastructure_interruption.md",
    "docs/28_aamas_confirmatory_results.md",
)

TREE_ROOTS = (
    "src/aether_contract_bridge",
    "experiments/09_aamas_contract_bridge/protocol",
    "experiments/09_aamas_contract_bridge/fixtures",
    "experiments/09_aamas_contract_bridge/calibration",
    "experiments/09_aamas_contract_bridge/analysis",
)

BENCHMARK_PATTERNS = (
    "benchmarks/aether_execution_worker.py",
    "benchmarks/analyze_aamas_confirmatory.py",
    "benchmarks/audit_aamas_provider_cohort.py",
    "benchmarks/generate_aamas_figures.py",
    "benchmarks/run_aamas_*.py",
    "benchmarks/validate_aamas_e4_freeze.py",
)

TRAJECTORY_PATTERNS = (
    "prompt.txt",
    "attempt_*_prompt.txt",
    "attempt_*_raw_response.txt",
    "attempt_*_program.py",
    "attempt_*_strategy.json",
    "events.jsonl",
    "summary.json",
    "trajectory_manifest.json",
)

FORBIDDEN = {
    "author identity": re.compile(r"\bManu\s+Agrawal\b|manuagrawal|@gmail\.com", re.I),
    "public repository identity": re.compile(r"\bmanu2\b|Context-Aware-Agent-Experiment", re.I),
    "local path": re.compile(r"/Users/[^/\s]+|file://", re.I),
    "API credential": re.compile(
        r"(?:AIza[0-9A-Za-z_-]{30,}|sk-[A-Za-z0-9_-]{20,}|sk-ant-[A-Za-z0-9_-]{20,})"
    ),
}


def selected_files() -> list[Path]:
    files: set[Path] = {ROOT / relative for relative in EXACT_FILES}
    for root in TREE_ROOTS:
        files.update(path for path in (ROOT / root).rglob("*") if path.is_file())
    for pattern in BENCHMARK_PATTERNS:
        files.update(path for path in ROOT.glob(pattern) if path.is_file())
    files.add(ROOT / "tests/test_contract_bridge.py")
    confirmatory = ROOT / "experiments/09_aamas_contract_bridge/confirmatory"
    for pattern in TRAJECTORY_PATTERNS:
        files.update(path for path in confirmatory.rglob(pattern) if path.is_file())
    return sorted(files, key=lambda path: path.relative_to(ROOT).as_posix())


def archive_bytes(path: Path) -> tuple[bytes, bytes, bool]:
    raw = path.read_bytes()
    data = raw
    if b"\x00" not in data:
        data = data.replace(b"/Users/manuagrawal", b"/home/aether-runner")
        data = data.replace(b"manuagrawal", b"aether-runner")
    return raw, data, data != raw


def check_anonymous(name: str, data: bytes) -> None:
    text = data.decode("utf-8", errors="ignore")
    for label, pattern in FORBIDDEN.items():
        if pattern.search(text):
            raise ValueError(f"{label} appears in {name}")


def write_member(archive: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, FIXED_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    archive.writestr(info, data, compresslevel=9)


def main() -> int:
    files = selected_files()
    missing = [str(path.relative_to(ROOT)) for path in files if not path.exists()]
    if missing:
        raise FileNotFoundError(f"supplement inputs missing: {missing}")

    members: list[tuple[str, bytes]] = []
    manifest_files = []
    for path in files:
        name = path.relative_to(ROOT).as_posix()
        raw, data, anonymized = archive_bytes(path)
        check_anonymous(name, data)
        members.append((name, data))
        manifest_files.append({
            "path": name,
            "bytes": len(data),
            "source_sha256": sha256(raw).hexdigest(),
            "packaged_sha256": sha256(data).hexdigest(),
            "anonymization": "local worker identifier normalized" if anonymized else None,
        })

    analysis = json.loads(
        (ROOT / "experiments/09_aamas_contract_bridge/analysis/confirmatory_analysis.json").read_text()
    )
    trajectory_count = analysis.get("trajectory_count")
    if trajectory_count != 288:
        raise ValueError(f"unexpected effective trajectory count: {trajectory_count}")
    archived_slots = sum(
        1 for name, _ in members
        if name.startswith("experiments/09_aamas_contract_bridge/confirmatory/")
        and name.endswith("/summary.json")
    )
    if archived_slots != 320:
        raise ValueError(f"unexpected archived trajectory-slot count: {archived_slots}")

    manifest = {
        "schema_version": "aamas-anonymous-supplement/v1.0",
        "trajectory_count": trajectory_count,
        "archived_trajectory_slots": archived_slots,
        "files": manifest_files,
    }
    manifest_data = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    check_anonymous("manifest.json", manifest_data)

    OUTPUT.unlink(missing_ok=True)
    with zipfile.ZipFile(OUTPUT, "w") as archive:
        for name, data in members:
            write_member(archive, name, data)
        write_member(archive, "manifest.json", manifest_data)

    if OUTPUT.stat().st_size > 25 * 1024 * 1024:
        raise ValueError(f"supplement exceeds 25 MiB: {OUTPUT.stat().st_size}")
    print(json.dumps({"path": str(OUTPUT), "members": len(members) + 1,
                      "bytes": OUTPUT.stat().st_size,
                      "sha256": sha256(OUTPUT.read_bytes()).hexdigest()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
