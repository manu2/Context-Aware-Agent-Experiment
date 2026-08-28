#!/usr/bin/env python3
"""Render the final manuscript figures from archived metadata; no API calls."""

from __future__ import annotations

import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from benchmarks.render_fresh_cohort_figures import MODELS, PALETTE, pair_records, read_96


OUTPUT = ROOT / "paper/figures"
WIDTH = 720
BLIND = PALETTE["blind"]
AWARE128 = PALETTE["aware128"]
AWARE96 = PALETTE["aware96"]
SLATE = colors.HexColor("#475569")
GRID = colors.HexColor("#e2e8f0")


def groups(model: str, prefix: str):
    pairs = pair_records(model, prefix)
    blind = [a for _, a, _ in pairs if a["correct"]]
    aware128 = [d for _, _, d in pairs]
    sweep_prefix = {
        "claude-opus-5": "opus96_rep",
        "gpt-5.6-sol": "gpt96_rep",
        "gemini-3.7-flash": "gemini96_rep",
    }[model]
    return [("Blind", blind, BLIND), ("128 MB", aware128, AWARE128), ("96 MB", read_96(model, sweep_prefix), AWARE96)]


def base(c, height: int, title: str, subtitle: str):
    c.setFillColor(colors.white)
    c.rect(0, 0, WIDTH, height, fill=1, stroke=0)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(42, height - 27, title)
    c.setFillColor(SLATE)
    c.setFont("Helvetica", 8.5)
    c.drawString(42, height - 42, subtitle)


def legend(c, y: float):
    items = [(253, "Blind", BLIND), (363, "128 MB-aware", AWARE128), (514, "96 MB-aware", AWARE96)]
    for x, label, color in items:
        c.setFillColor(color)
        c.circle(x, y, 3.5, fill=1, stroke=0)
        c.setFillColor(SLATE)
        c.setFont("Helvetica", 8)
        c.drawString(x + 7, y - 3, label)


def grid(c, x0, x1, y0, y1, ticks, maximum, *, labels=True):
    c.setStrokeColor(colors.HexColor("#94a3b8"))
    c.rect(x0, y0, x1 - x0, y1 - y0, stroke=1, fill=0)
    for tick in ticks:
        y = y0 + (y1 - y0) * tick / maximum
        c.setStrokeColor(GRID)
        c.line(x0, y, x1, y)
        if labels:
            c.setFillColor(SLATE)
            c.setFont("Helvetica", 7)
            c.drawRightString(x0 - 5, y - 2, f"{tick:g}%")


def figure1_paired_relative():
    path = OUTPUT / "figure_1_paired_relative.pdf"
    c = canvas.Canvas(str(path), pagesize=(WIDTH, 336))
    base(c, 336, "Execution-context disclosure changes memory use within paired generations", "Each executable pair is indexed to its own blind result (blind = 100%). Lower values indicate less observed MaxRSS.")
    left, right, bottom, top = 50, 704, 57, 252
    panel_w = (right - left - 36) / 3
    maximum, ticks = 160, (0, 50, 100, 150)
    for panel, (model, label, prefix) in enumerate(MODELS):
        x0 = left + panel * (panel_w + 18)
        x1 = x0 + panel_w
        grid(c, x0, x1, bottom, top, ticks, maximum, labels=panel == 0)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString((x0 + x1) / 2, top + 8, label)
        if model == "claude-opus-5":
            c.setFillColor(colors.HexColor("#991b1b")); c.setFont("Helvetica", 6.5)
            c.drawCentredString((x0 + x1) / 2, top - 10, "† blind rep04: runtime failure; no paired MaxRSS value")
        y100 = bottom + (top - bottom) * 100 / maximum
        c.setStrokeColor(colors.HexColor("#64748b")); c.setDash(2, 2); c.line(x0, y100, x1, y100); c.setDash()
        for idx, (trial, blind, aware) in enumerate(pair_records(model, prefix)):
            x_blind = x0 + 38 + idx * ((panel_w - 76) / 4)
            x_aware = x_blind + 19
            if not blind["correct"]:
                continue
            relative = 100 * aware["maxrss_mb"] / blind["maxrss_mb"]
            y_blind = y100
            y_aware = bottom + (top-bottom) * relative / maximum
            c.setStrokeColor(colors.HexColor("#94a3b8")); c.setLineWidth(1.1); c.line(x_blind, y_blind, x_aware, y_aware)
            c.setFillColor(BLIND); c.circle(x_blind, y_blind, 3.3, fill=1, stroke=0)
            c.setFillColor(AWARE128); c.circle(x_aware, y_aware, 3.3, fill=1, stroke=0)
        c.setFillColor(SLATE); c.setFont("Helvetica", 7)
        c.drawCentredString(x0 + 55, bottom - 14, "blind")
        c.drawCentredString(x1 - 55, bottom - 14, "128 MB-aware")
    c.setFillColor(SLATE); c.setFont("Helvetica", 8)
    c.drawString(43, 21, "Executable pairs: Claude 4/4 lower; GPT 4/5 lower; Gemini 5/5 lower. † Claude rep04_A failed under pinned Python 3.9.6.")
    c.saveState(); c.translate(16, (bottom + top) / 2); c.rotate(90)
    c.setFillColor(SLATE); c.setFont("Helvetica", 8); c.drawCentredString(0, 0, "Observed MaxRSS (% of paired blind result)")
    c.restoreState()
    c.save()


def condition_distribution(metric: str, filename: str, title: str, subtitle: str):
    path = OUTPUT / filename
    c = canvas.Canvas(str(path), pagesize=(WIDTH, 336))
    base(c, 336, title, subtitle)
    left, right, bottom, top = 50, 704, 57, 252
    panel_w = (right - left - 36) / 3
    maximum, ticks = 160, (0, 50, 100, 150)
    for panel, (model, label, prefix) in enumerate(MODELS):
        x0 = left + panel * (panel_w + 18)
        x1 = x0 + panel_w
        grid(c, x0, x1, bottom, top, ticks, maximum, labels=panel == 0)
        c.setFillColor(colors.black); c.setFont("Helvetica-Bold", 9)
        c.drawCentredString((x0 + x1) / 2, top + 8, label)
        model_groups = groups(model, prefix)
        baseline = sum(v[metric] for v in model_groups[0][1]) / len(model_groups[0][1])
        y100 = bottom + (top-bottom) * 100 / maximum
        c.setStrokeColor(colors.HexColor("#64748b")); c.setDash(2, 2); c.line(x0, y100, x1, y100); c.setDash()
        for group_idx, (short, rows, color) in enumerate(model_groups):
            x = x0 + 42 + group_idx * ((panel_w - 84) / 2)
            for point_idx, record in enumerate(rows):
                jitter = (point_idx - (len(rows)-1)/2) * 5
                relative = 100 * record[metric] / baseline
                y = bottom + (top-bottom) * relative / maximum
                c.setFillColor(color); c.circle(x + jitter, y, 3.1, fill=1, stroke=0)
            c.setFillColor(SLATE); c.setFont("Helvetica", 7)
            c.drawCentredString(x, bottom - 14, short)
    legend(c, 29)
    axis_label = "Observed MaxRSS (% of blind-reference mean)" if metric == "maxrss_mb" else "Wall time (% of blind-reference mean)"
    c.saveState(); c.translate(16, (bottom + top) / 2); c.rotate(90)
    c.setFillColor(SLATE); c.setFont("Helvetica", 8); c.drawCentredString(0, 0, axis_label)
    c.restoreState()
    c.setFillColor(SLATE); c.setFont("Helvetica", 7.6)
    c.drawString(43, 13, "Each observation is indexed to its configured model's executable blind-reference mean. The 96 MB samples are independently generated condition-level observations.")
    c.save()


def figure2_combined_resource_time():
    """Two aligned distribution rows, designed as one compact main figure."""
    path = OUTPUT / "figure_2_resource_time_distributions.pdf"
    height = 530
    c = canvas.Canvas(str(path), pagesize=(WIDTH, height))
    base(c, height, "Execution-context disclosure shifts resource and execution-time distributions", "Each model configuration's executable blind-reference mean is indexed to 100%; lower values indicate lower observed use or time.")
    left, right = 50, 704
    panel_w = (right - left - 36) / 3
    rows = [
        ("maxrss_mb", "Observed MaxRSS (% of blind-reference mean)", 292, 448),
        ("wall_sec", "Wall time (% of blind-reference mean)", 81, 237),
    ]
    maximum, ticks = 160, (0, 50, 100, 150)
    for key, axis_label, bottom, top in rows:
        c.saveState(); c.translate(16, (bottom + top) / 2); c.rotate(90)
        c.setFillColor(SLATE); c.setFont("Helvetica", 8); c.drawCentredString(0, 0, axis_label)
        c.restoreState()
        for panel, (model, label, prefix) in enumerate(MODELS):
            x0 = left + panel * (panel_w + 18)
            x1 = x0 + panel_w
            grid(c, x0, x1, bottom, top, ticks, maximum, labels=panel == 0)
            c.setFillColor(colors.black); c.setFont("Helvetica-Bold", 9)
            c.drawCentredString((x0 + x1) / 2, top + 8, label)
            model_groups = groups(model, prefix)
            baseline = sum(v[key] for v in model_groups[0][1]) / len(model_groups[0][1])
            y100 = bottom + (top-bottom) * 100 / maximum
            c.setStrokeColor(colors.HexColor("#64748b")); c.setDash(2, 2); c.line(x0, y100, x1, y100); c.setDash()
            for group_idx, (short, rows, color) in enumerate(model_groups):
                x = x0 + 42 + group_idx * ((panel_w - 84) / 2)
                for point_idx, record in enumerate(rows):
                    jitter = (point_idx - (len(rows)-1)/2) * 5
                    y = bottom + (top-bottom) * (100 * record[key] / baseline) / maximum
                    c.setFillColor(color); c.circle(x + jitter, y, 3.1, fill=1, stroke=0)
                c.setFillColor(SLATE); c.setFont("Helvetica", 7)
                c.drawCentredString(x, bottom - 14, short)
    c.setFillColor(SLATE); c.setFont("Helvetica", 7.5)
    c.drawString(43, 261, "Contract fit (correct + observed MaxRSS within disclosed RAM): 128 MB-aware: Claude 5/5, GPT 5/5, Gemini 2/5; 96 MB-aware: Claude 4/5, GPT 5/5, Gemini 3/5.")
    legend(c, 50)
    c.setFillColor(SLATE); c.setFont("Helvetica", 7.6)
    c.drawString(43, 31, "Every retained executable observation is visible. The 96 MB samples are independently generated condition-level observations.")
    c.save()


def figure_s1_raw_memory():
    path = OUTPUT / "appendix_figure_a1_raw_memory.pdf"
    c = canvas.Canvas(str(path), pagesize=(WIDTH, 336))
    base(c, 336, "Observed memory distributions in native units", "Every retained executable result is shown. Each panel uses its own native MB scale; dashed lines show the 96 and 128 MB reference boundaries.")
    left, right, bottom, top = 50, 704, 57, 252
    panel_w = (right - left - 84) / 3
    for panel, (model, label, prefix) in enumerate(MODELS):
        x0 = left + panel * (panel_w + 42)
        x1 = x0 + panel_w
        model_groups = groups(model, prefix)
        maximum = max(v["maxrss_mb"] for _, rows, _ in model_groups for v in rows) * 1.12
        # clean, rounded panel-specific maximum
        maximum = 100 * int((maximum + 99) // 100)
        ticks = [round(maximum * frac) for frac in (0, .25, .5, .75, 1)]
        c.setStrokeColor(colors.HexColor("#94a3b8")); c.rect(x0, bottom, panel_w, top-bottom, stroke=1, fill=0)
        c.setFillColor(colors.black); c.setFont("Helvetica-Bold", 8.5); c.drawCentredString((x0+x1)/2, top+8, f"{label} (0-{maximum:g} MB)")
        for tick in ticks:
            y = bottom + (top-bottom) * tick / maximum
            c.setStrokeColor(GRID); c.line(x0, y, x1, y)
            c.setFillColor(SLATE); c.setFont("Helvetica", 7); c.drawRightString(x0-5, y-2, f"{tick:g}")
        for threshold, tlabel in ((96, "96"), (128, "128")):
            y = bottom + (top-bottom) * threshold / maximum
            c.setStrokeColor(colors.HexColor("#64748b")); c.setDash(2, 2); c.line(x0, y, x1, y); c.setDash()
            c.setFillColor(SLATE); c.setFont("Helvetica", 6.5); c.drawRightString(x1-3, y+3, tlabel)
        for group_idx, (short, rows, color) in enumerate(model_groups):
            x = x0 + 42 + group_idx * ((panel_w - 84) / 2)
            for point_idx, record in enumerate(rows):
                jitter = (point_idx - (len(rows)-1)/2)*5
                y = bottom + (top-bottom) * record["maxrss_mb"] / maximum
                c.setFillColor(color); c.circle(x+jitter, y, 3.1, fill=1, stroke=0)
            c.setFillColor(SLATE); c.setFont("Helvetica",7); c.drawCentredString(x, bottom-14, short)
    legend(c, 29)
    c.saveState(); c.translate(16, (bottom + top) / 2); c.rotate(90)
    c.setFillColor(SLATE); c.setFont("Helvetica", 8); c.drawCentredString(0, 0, "Observed MaxRSS (MB)")
    c.restoreState()
    c.setFillColor(SLATE); c.setFont("Helvetica",7.6)
    c.drawString(43, 13, "Native panel scales differ by model configuration; Fig. 2 provides the aligned within-configuration effect view.")
    c.save()


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    figure1_paired_relative()
    figure2_combined_resource_time()
    figure_s1_raw_memory()
    for name in (
        "figure_1_paired_relative.pdf",
        "figure_2_resource_time_distributions.pdf",
        "appendix_figure_a1_raw_memory.pdf",
    ):
        print(OUTPUT / name)


if __name__ == "__main__":
    main()
