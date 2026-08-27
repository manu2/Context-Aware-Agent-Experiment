#!/usr/bin/env python3
"""Render publication figures directly from archived fresh-cohort metadata.

Uses ReportLab rather than a plotting framework so a clean environment needs only
the bundled PDF runtime. The resulting PDFs are vector figures suitable for a
LaTeX manuscript. No model calls or raw-artifact modifications occur.
"""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
DIRECT = ROOT / "experiments/06_replication/raw"
SWEEP = ROOT / "experiments/08_96mb_cgroup_pilot/raw"
OUTPUT = ROOT / "paper/figures"
WIDTH, HEIGHT = 720, 320
MODELS = [
    ("claude-opus-5", "Claude Opus 5", "opus_rep"),
    ("gpt-5.6-sol", "GPT-5.6-Sol", "gpt_rep"),
    ("gemini-3.7-flash", "Gemini 3.7 Flash", "gemini_rep"),
]
PALETTE = {"blind": colors.HexColor("#9a3412"), "aware128": colors.HexColor("#0369a1"), "aware96": colors.HexColor("#047857")}


def profile(directory: Path, filename: str) -> dict:
    data = json.loads((directory / filename).read_text())
    return data["profile"]


def pair_records(model: str, prefix: str) -> list[tuple[str, dict, dict]]:
    start = 2 if model == "claude-opus-5" else 1
    records = []
    for number in range(start, 6 if model == "claude-opus-5" else 6):
        if model == "claude-opus-5" and number == 6:
            continue
        trial = f"{prefix}{number:02d}"
        a = profile(DIRECT / model / f"{trial}_A", "metadata.json")
        d = profile(DIRECT / model / f"{trial}_D", "metadata.json")
        records.append((trial, a, d))
    if model == "claude-opus-5":
        trial = "opus_rep06"
        records.append((trial, profile(DIRECT / model / f"{trial}_A", "metadata.json"), profile(DIRECT / model / f"{trial}_D", "metadata.json")))
    return records


def header(c: canvas.Canvas, title: str, subtitle: str) -> None:
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(colors.black)
    c.drawString(42, HEIGHT - 28, title)
    c.setFont("Helvetica", 8.5)
    c.setFillColor(colors.HexColor("#444444"))
    c.drawString(42, HEIGHT - 42, subtitle)


def paired_rss() -> None:
    path = OUTPUT / "fresh_128mb_paired_maxrss.pdf"
    c = canvas.Canvas(str(path), pagesize=(WIDTH, HEIGHT))
    c.setFillColor(colors.white); c.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
    header(c, "Fresh 128 MB cohort: paired observed MaxRSS", "Every executable A/D pair is shown; values are local macOS process MaxRSS, not cgroup survival.")
    left, right, bottom, top = 48, 704, 47, 244
    panel_w = (right - left - 36) / 3
    maximum = 720
    for panel, (model, label, prefix) in enumerate(MODELS):
        x0 = left + panel * (panel_w + 18)
        x1 = x0 + panel_w
        c.setStrokeColor(colors.HexColor("#999999")); c.rect(x0, bottom, panel_w, top - bottom, stroke=1, fill=0)
        c.setFont("Helvetica-Bold", 9); c.setFillColor(colors.black); c.drawCentredString((x0 + x1) / 2, top + 8, label)
        for tick in (0, 128, 256, 512, 720):
            y = bottom + (top - bottom) * tick / maximum
            c.setStrokeColor(colors.HexColor("#e5e7eb")); c.line(x0, y, x1, y)
            if panel == 0:
                c.setFont("Helvetica", 7); c.setFillColor(colors.HexColor("#444444")); c.drawRightString(x0 - 5, y - 2, str(tick))
        threshold = bottom + (top - bottom) * 128 / maximum
        c.setStrokeColor(colors.HexColor("#334155")); c.setDash(3, 2); c.line(x0, threshold, x1, threshold); c.setDash()
        c.setFont("Helvetica", 7); c.setFillColor(colors.HexColor("#334155")); c.drawRightString(x1 - 3, threshold + 3, "128")
        for index, (trial, a, d) in enumerate(pair_records(model, prefix)):
            xa = x0 + 42 + index * ((panel_w - 84) / 4)
            xd = xa + 22
            if not a["correct"]:
                c.setFillColor(colors.HexColor("#991b1b")); c.setFont("Helvetica", 7)
                c.drawCentredString(xa, bottom + 5, "failed")
                yd = bottom + (top - bottom) * d["maxrss_mb"] / maximum
                c.setFillColor(PALETTE["aware128"]); c.circle(xd, yd, 3, fill=1, stroke=0)
                continue
            ya = bottom + (top - bottom) * a["maxrss_mb"] / maximum
            yd = bottom + (top - bottom) * d["maxrss_mb"] / maximum
            c.setStrokeColor(colors.HexColor("#64748b")); c.setLineWidth(1); c.line(xa, ya, xd, yd)
            c.setFillColor(PALETTE["blind"]); c.circle(xa, ya, 3, fill=1, stroke=0)
            c.setFillColor(PALETTE["aware128"]); c.circle(xd, yd, 3, fill=1, stroke=0)
        c.setFont("Helvetica", 7); c.setFillColor(colors.HexColor("#444444")); c.drawCentredString(x0 + 56, bottom - 14, "blind")
        c.drawCentredString(x1 - 56, bottom - 14, "128 MB-aware")
    c.setFont("Helvetica", 8); c.setFillColor(colors.HexColor("#444444")); c.drawString(44, 18, "Pairs: Claude 4/4 executable lower; GPT 4/5 lower; Gemini 5/5 lower. Claude rep04 blind is retained as a runtime failure.")
    c.save()


def read_96(model: str, prefix: str) -> list[dict]:
    ids = [1, 2, 4, 6, 7] if model == "claude-opus-5" else [1, 2, 3, 4, 5]
    return [profile(SWEEP / model / f"{prefix}{number:02d}_D", "local_observed_rss_profile.json") for number in ids]


def condition_distributions() -> None:
    path = OUTPUT / "fresh_boundary_sensitivity_maxrss.pdf"
    c = canvas.Canvas(str(path), pagesize=(WIDTH, HEIGHT))
    c.setFillColor(colors.white); c.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
    header(c, "Condition-level boundary sensitivity: observed MaxRSS", "Blind and 128 MB samples are reference distributions; 96 MB samples are independently generated, not matched triples.")
    left, right, bottom, top = 48, 704, 47, 244
    panel_w = (right - left - 36) / 3
    maximum = 720
    for panel, (model, label, prefix) in enumerate(MODELS):
        x0 = left + panel * (panel_w + 18); x1 = x0 + panel_w
        c.setStrokeColor(colors.HexColor("#999999")); c.rect(x0, bottom, panel_w, top - bottom, stroke=1, fill=0)
        c.setFillColor(colors.black); c.setFont("Helvetica-Bold", 9); c.drawCentredString((x0+x1)/2, top+8, label)
        for tick in (0, 96, 128, 256, 512, 720):
            y = bottom + (top-bottom) * tick / maximum
            c.setStrokeColor(colors.HexColor("#e5e7eb")); c.line(x0, y, x1, y)
            if panel == 0:
                c.setFillColor(colors.HexColor("#444444")); c.setFont("Helvetica", 7); c.drawRightString(x0-5, y-2, str(tick))
        for threshold, label_text in ((96, "96"), (128, "128")):
            y = bottom + (top-bottom) * threshold / maximum
            c.setStrokeColor(colors.HexColor("#334155")); c.setDash(3,2); c.line(x0,y,x1,y); c.setDash()
            c.setFillColor(colors.HexColor("#334155")); c.setFont("Helvetica",7); c.drawRightString(x1-3,y+3,label_text)
        paired = pair_records(model, prefix)
        blind = [a for _, a, _ in paired if a["correct"]]
        aware128 = [d for _, _, d in paired]
        sweep_prefix = "opus96_rep" if model == "claude-opus-5" else ("gpt96_rep" if model == "gpt-5.6-sol" else "gemini96_rep")
        groups = [("blind", blind, PALETTE["blind"]), ("128", aware128, PALETTE["aware128"]), ("96", read_96(model, sweep_prefix), PALETTE["aware96"])]
        for group_index, (short, values, color) in enumerate(groups):
            x = x0 + 42 + group_index * ((panel_w - 84) / 2)
            for point_index, value in enumerate(values):
                jitter = (point_index - (len(values)-1)/2) * 5
                y = bottom + (top-bottom) * value["maxrss_mb"] / maximum
                c.setFillColor(color); c.circle(x+jitter, y, 3, fill=1, stroke=0)
            c.setFillColor(colors.HexColor("#444444")); c.setFont("Helvetica",7); c.drawCentredString(x,bottom-14,short)
    c.setFont("Helvetica",8); c.setFillColor(colors.HexColor("#444444")); c.drawString(44,18,"Every retained executable result is visible. Threshold lines denote observed-RSS classifications, not OS-enforced admissions.")
    c.save()


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    paired_rss()
    condition_distributions()
    for path in sorted(OUTPUT.glob("fresh_*.pdf")):
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
