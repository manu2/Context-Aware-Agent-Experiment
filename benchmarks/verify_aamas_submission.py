#!/usr/bin/env python3
"""Fail-closed checks for the anonymous AAMAS 2027 submission package."""

from __future__ import annotations

import argparse
from hashlib import sha256
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
    return issues


def supplement_issues() -> list[str]:
    issues: list[str] = []
    for path in PACKAGE.glob("*.zip"):
        if path.stat().st_size > 25 * 1024 * 1024:
            issues.append(f"supplement exceeds 25 MiB: {path.name}")
        with zipfile.ZipFile(path) as archive:
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
    return issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", action="store_true", help="reject all placeholders and require final metadata")
    parser.add_argument("--pdf", type=Path, help="compiled PDF to inspect")
    args = parser.parse_args()
    issues = source_issues(args.release) + supplement_issues()
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
