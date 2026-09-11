#!/usr/bin/env python3
"""Fail-closed checks for the anonymous AAMAS 2027 submission package."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
import re
from pathlib import Path
import subprocess
import sys
import zipfile


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "paper/aamas2027"
OFFICIAL_HASHES = {
    "aamas.cls": "e88c8e3e5fd1e39f93a2a4fa5b664e125b67487996b4236668206acf5c70ca7e",
    "ACM-Reference-Format.bst": "8ec002c927068bfc5b3cfe71b66aa4767b9e485530ac3c67ba5c064df4c2e6ac",
    "by.pdf": "19b7b19350bb937afead8e45e4ad006187e14803bef783902dbd88e370fc9917",
}
IDENTITY_PATTERNS = {
    "author name": re.compile(r"\bManu\s+Agrawal\b", re.I),
    "personal email": re.compile(r"manuagrawal|@gmail\.com", re.I),
    "public repository identity": re.compile(r"manu2|Context-Aware-Agent-Experiment", re.I),
    "local user path": re.compile(r"/Users/[^/\s]+|file://", re.I),
}
ANALYSIS = ROOT / "experiments/09_aamas_contract_bridge/analysis/confirmatory_analysis.json"
FIGURES = (
    PACKAGE / "figures/primary_suitability.pdf",
    PACKAGE / "figures/effect_by_task_environment.pdf",
)


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def source_issues(release: bool) -> list[str]:
    issues: list[str] = []
    main = (PACKAGE / "main.tex").read_text()
    if r"\documentclass[sigconf,anonymous]{aamas}" not in main:
        issues.append("main.tex does not use the anonymous official class")
    if r"\author{Anonymous Author(s)}" not in main:
        issues.append("anonymous author block is missing")
    if r"\submissionType{Research Paper Track}" not in main:
        issues.append("Research Paper Track declaration is missing")
    for filename, expected in OFFICIAL_HASHES.items():
        path = PACKAGE / filename
        if not path.exists() or digest(path) != expected:
            issues.append(f"official template asset changed or missing: {filename}")

    scanned = [PACKAGE / "main.tex", PACKAGE / "references.bib"]
    for path in scanned:
        text = path.read_text(errors="replace")
        for label, pattern in IDENTITY_PATTERNS.items():
            if pattern.search(text):
                issues.append(f"{label} appears in {path.name}")

    if release:
        if "CONFIRMATORY RESULT PENDING" in main or "\\resultpending" in main:
            issues.append("confirmatory result placeholder remains")
        if r"\acmSubmissionID{PENDING}" in main:
            issues.append("OpenReview submission ID is still PENDING")
        if re.search(r"\b(?:TODO|TBD)\b", main, re.I):
            issues.append("TODO/TBD marker remains in main.tex")
    return issues


def evidence_issues() -> list[str]:
    """Reject manuscript packages that drift from the frozen evidence summary."""
    issues: list[str] = []
    if not ANALYSIS.exists():
        return [f"confirmatory analysis missing: {ANALYSIS.relative_to(ROOT)}"]
    payload = json.loads(ANALYSIS.read_text())
    if payload.get("schema_version") != "aamas-confirmatory-analysis/v1.0":
        issues.append("unexpected confirmatory analysis schema")
    if payload.get("trajectory_count") != 288:
        issues.append("confirmatory matrix is not the frozen 288 trajectories")
    overall = {row["condition"]: row for row in payload["binary_breakdowns"]["overall"]}
    expected = {
        "P": (64, 72, 128, 469368),
        "R": (14, 33, 178, 595702),
        "G": (27, 43, 165, 671074),
    }
    for condition, values in expected.items():
        row = overall.get(condition, {})
        observed = (
            row.get("first_pass_suitable"), row.get("final_suitable"),
            row.get("provider_calls"), row.get("provider_tokens"),
        )
        if observed != values:
            issues.append(f"frozen {condition} summary changed: {observed}")
    primary = payload.get("primary_analysis", {})
    if primary.get("observed") != {
        "P_minus_G": 0.3854166666666667,
        "P_minus_R": 0.5208333333333334,
    }:
        issues.append("co-primary risk differences changed")
    manuscript = re.sub(r"\s+", " ", (PACKAGE / "main.tex").read_text())
    required_claims = (
        "proactive disclosure produced 64/96 (66.7\\%) first-pass suitable",
        "compared with 14/96 (14.6\\%) under reactive feedback and 27/96",
        "Proactive (P) & 64/96 & 72/96 & 128 & 469k & \\$4.30",
        "Reactive (R) & 14/96 & 33/96 & 178 & 596k & \\$4.53",
        "Generic (G) & 27/96 & 43/96 & 165 & 671k & \\$4.43",
    )
    for claim in required_claims:
        if claim not in manuscript:
            issues.append(f"manuscript evidence claim missing or changed: {claim}")
    for figure in FIGURES:
        if not figure.exists() or not figure.read_bytes().startswith(b"%PDF"):
            issues.append(f"vector figure missing or invalid: {figure.relative_to(ROOT)}")
    return issues


def pdf_issues(pdf: Path, release: bool) -> list[str]:
    issues: list[str] = []
    if not pdf.exists():
        return [f"compiled PDF missing: {pdf}"]
    info = subprocess.run(["pdfinfo", str(pdf)], check=True, capture_output=True, text=True).stdout
    match = re.search(r"^Pages:\s+(\d+)$", info, re.M)
    if not match:
        issues.append("could not determine PDF page count")
        return issues
    pages = int(match.group(1))
    reference_page = None
    for page in range(1, pages + 1):
        text = subprocess.run(
            ["pdftotext", "-f", str(page), "-l", str(page), str(pdf), "-"],
            check=True, capture_output=True, text=True,
        ).stdout
        for label, pattern in IDENTITY_PATTERNS.items():
            if pattern.search(text):
                issues.append(f"{label} appears in PDF page {page}")
        if reference_page is None and re.search(r"^REFERENCES\s*$", text, re.M | re.I):
            reference_page = page
    if reference_page is None:
        issues.append("REFERENCES heading not found in compiled PDF")
    elif reference_page > 9:
        issues.append(f"references begin on page {reference_page}; content exceeds eight pages")
    if release:
        metadata = info.lower()
        for token in ("manu", "agrawal", "gmail", "manu2"):
            if token in metadata:
                issues.append(f"identifying token appears in PDF metadata: {token}")
    fonts = subprocess.run(
        ["pdffonts", str(pdf)], check=True, capture_output=True, text=True,
    ).stdout
    for line in fonts.splitlines()[2:]:
        match = re.search(r"\s+(yes|no)\s+(yes|no)\s+(yes|no)\s+\d+\s+\d+\s*$", line)
        if match and match.group(1) != "yes":
            issues.append(f"unembedded PDF font: {line.split()[0]}")
    return issues


def supplement_issues(require: bool = False) -> list[str]:
    issues: list[str] = []
    archives = sorted(PACKAGE.glob("*.zip"))
    if require and not archives:
        return ["anonymous supplementary ZIP is missing"]
    for path in archives:
        if path.stat().st_size > 25 * 1024 * 1024:
            issues.append(f"supplement exceeds 25 MiB: {path.name}")
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            required = {
                "manifest.json",
                "paper/aamas2027/SUPPLEMENT_README.md",
                "paper/aamas2027/AI_ASSISTANCE_DISCLOSURE.md",
                "experiments/09_aamas_contract_bridge/analysis/confirmatory_analysis.json",
                "docs/28_aamas_confirmatory_results.md",
            }
            for name in sorted(required - set(names)):
                issues.append(f"required supplement member missing: {name}")
            if any(name.endswith("_provider_response.json") for name in names):
                issues.append("provider transport envelope appears in supplement")
            for member in archive.infolist():
                name = member.filename
                if name.startswith("/") or ".." in Path(name).parts:
                    issues.append(f"unsafe supplement path: {name}")
                if member.file_size <= 4 * 1024 * 1024:
                    data = archive.read(member)
                    text = data.decode("utf-8", errors="ignore")
                    for label, pattern in IDENTITY_PATTERNS.items():
                        if pattern.search(text):
                            issues.append(f"{label} appears in supplement member {name}")
            if "manifest.json" in names:
                try:
                    manifest = json.loads(archive.read("manifest.json"))
                except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                    issues.append(f"invalid supplement manifest: {exc}")
                else:
                    if manifest.get("schema_version") != "aamas-anonymous-supplement/v1.0":
                        issues.append("unexpected supplement manifest schema")
                    if manifest.get("trajectory_count") != 288:
                        issues.append("supplement manifest does not declare 288 effective trajectories")
                    if manifest.get("archived_trajectory_slots") != 320:
                        issues.append("supplement manifest does not declare 320 archived trajectory slots")
                    rows = manifest.get("files", [])
                    listed = {row.get("path") for row in rows}
                    actual = set(names) - {"manifest.json"}
                    if listed != actual:
                        issues.append("supplement manifest member set does not match archive")
                    for row in rows:
                        name = row.get("path")
                        if name in actual:
                            data = archive.read(name)
                            if row.get("bytes") != len(data) or row.get("packaged_sha256") != sha256(data).hexdigest():
                                issues.append(f"supplement digest mismatch: {name}")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", action="store_true", help="reject all placeholders and require final metadata")
    parser.add_argument("--pdf", type=Path, help="compiled PDF to inspect")
    args = parser.parse_args()
    issues = source_issues(args.release) + evidence_issues() + supplement_issues(require=args.release)
    if args.pdf:
        issues.extend(pdf_issues(args.pdf.resolve(), args.release))
    for issue in issues:
        print(f"FAIL: {issue}")
    if issues:
        return 1
    print("AAMAS submission package checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
