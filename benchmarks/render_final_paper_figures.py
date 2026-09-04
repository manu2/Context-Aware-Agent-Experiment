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
    task_only = [a for _, a, _ in pairs if a["correct"]]
    aware128 = [d for _, _, d in pairs]
    sweep_prefix = {
        "claude-opus-5": "opus96_rep",
        "gpt-5.6-sol": "gpt96_rep",
        "gemini-3.7-flash": "gemini96_rep",
    }[model]
    return [("Task-only", task_only, BLIND), ("128 MB contract", aware128, AWARE128), ("96 MB contract", read_96(model, sweep_prefix), AWARE96)]


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
    items = [(232, "Task-only", BLIND), (355, "128 MB contract", AWARE128), (514, "96 MB contract", AWARE96)]
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


def draw_square(c, x: float, y: float, size: float, color: colors.Color) -> None:
    c.setFillColor(color)
    c.rect(x - size, y - size, 2 * size, 2 * size, fill=1, stroke=0)


def draw_figure1_condition_cohorts(c):
    """Draw Figure 1 on an existing canvas without implying matched generations."""
    base(
        c,
        336,
        "Execution-contract disclosure shifts observed memory distributions",
        "Each condition cohort is indexed to its model configuration's task-only mean (100%). Lower values indicate lower observed process MaxRSS.",
    )
    left, right, bottom, top = 50, 704, 65, 244
    panel_w = (right - left - 42) / 3
    maximum = 180
    ticks = (0, 45, 90, 135, 180)
    for panel, (model, label, prefix) in enumerate(MODELS):
        x0 = left + panel * (panel_w + 21)
        x1 = x0 + panel_w
        c.setStrokeColor(colors.HexColor("#94a3b8"))
        c.rect(x0, bottom, panel_w, top - bottom, stroke=1, fill=0)
        for tick in ticks:
            y = bottom + (top - bottom) * tick / maximum
            c.setStrokeColor(GRID)
            c.line(x0, y, x1, y)
            if panel == 0:
                c.setFillColor(SLATE)
                c.setFont("Helvetica", 7)
                c.drawRightString(x0 - 5, y - 2, f"{tick:g}%")
        records = pair_records(model, prefix)
        task_only = [a for _, a, _ in records if a["correct"]]
        baseline_mean = sum(value["maxrss_mb"] for value in task_only) / len(task_only)
        threshold_percent = 100 * 128 / baseline_mean
        threshold_y = bottom + (top - bottom) * threshold_percent / maximum
        c.setStrokeColor(colors.HexColor("#475569"))
        c.setDash(3, 2)
        c.line(x0, threshold_y, x1, threshold_y)
        c.setDash()
        c.setFillColor(SLATE)
        c.setFont("Helvetica", 6.5)
        c.drawRightString(x1 - 3, threshold_y + 3, "128 MiB")
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString((x0 + x1) / 2, top + 8, label)

        condition_groups = [
            ("Task-only", task_only, BLIND, "circle"),
            ("128 MB + 10 s contract", [d for _, _, d in records], AWARE128, "square"),
        ]
        for group_index, (condition, values, color, marker) in enumerate(condition_groups):
            x = x0 + 45 + group_index * (panel_w - 90)
            for point_index, value in enumerate(values):
                jitter = (point_index - (len(values) - 1) / 2) * 6
                relative = 100 * value["maxrss_mb"] / baseline_mean
                y = bottom + (top - bottom) * relative / maximum
                if marker == "circle":
                    c.setFillColor(color)
                    c.circle(x + jitter, y, 3.2, fill=1, stroke=0)
                else:
                    draw_square(c, x + jitter, y, 3.1, color)
            mean_value = sum(value["maxrss_mb"] for value in values) / len(values)
            mean_y = bottom + (top - bottom) * (100 * mean_value / baseline_mean) / maximum
            c.setStrokeColor(colors.black)
            c.setLineWidth(1.1)
            c.line(x - 15, mean_y, x + 15, mean_y)
            c.setFillColor(colors.white)
            c.setStrokeColor(colors.black)
            if marker == "circle":
                c.circle(x, mean_y, 3.6, fill=1, stroke=1)
            else:
                c.rect(x - 3.6, mean_y - 3.6, 7.2, 7.2, fill=1, stroke=1)
            c.setFillColor(SLATE)
            c.setFont("Helvetica", 6.8)
            c.drawCentredString(x, bottom - 13, condition)
            c.drawCentredString(x, bottom - 22, f"n={len(values)}")
        if model == "claude-opus-5":
            c.setFillColor(colors.HexColor("#7f1d1d"))
            c.setFont("Helvetica", 6.3)
            c.drawCentredString((x0 + x1) / 2, bottom + 5, "† one task-only runtime failure; no MaxRSS point")

    c.setFillColor(BLIND)
    c.circle(241, 29, 3.2, fill=1, stroke=0)
    c.setFillColor(SLATE)
    c.setFont("Helvetica", 8)
    c.drawString(248, 26, "Task-only raw observation")
    draw_square(c, 412, 29, 3.1, AWARE128)
    c.setFillColor(SLATE)
    c.drawString(419, 26, "Contract-disclosed raw observation")
    c.setStrokeColor(colors.black)
    c.line(575, 29, 602, 29)
    c.setFillColor(SLATE)
    c.drawString(608, 26, "cohort mean")
    c.saveState()
    c.translate(16, (bottom + top) / 2)
    c.rotate(90)
    c.setFillColor(SLATE)
    c.setFont("Helvetica", 8)
    c.drawCentredString(0, 0, "Observed process MaxRSS (% of task-only mean)")
    c.restoreState()
    c.setFillColor(SLATE)
    c.setFont("Helvetica", 7.5)
    c.drawString(43, 13, "Dashed line: model-specific 128 MiB observed threshold. Points are independent generations; no connecting lines imply matched samples.")


def figure1_condition_cohorts():
    path = OUTPUT / "figure_1_condition_cohorts.pdf"
    c = canvas.Canvas(str(path), pagesize=(WIDTH, 336))
    draw_figure1_condition_cohorts(c)
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
    axis_label = "Observed MaxRSS (% of task-only mean)" if metric == "maxrss_mb" else "Wall time (% of task-only mean)"
    c.saveState(); c.translate(16, (bottom + top) / 2); c.rotate(90)
    c.setFillColor(SLATE); c.setFont("Helvetica", 8); c.drawCentredString(0, 0, axis_label)
    c.restoreState()
    c.setFillColor(SLATE); c.setFont("Helvetica", 7.6)
    c.drawString(43, 13, "Each observation is indexed to its configured model's executable task-only mean. The 96 MB samples are independently generated condition-level observations.")
    c.save()


def draw_figure2_combined_resource_time(c):
    """Draw Figure 2 on an existing canvas as two aligned distribution rows."""
    height = 530
    base(c, height, "Execution-context disclosure shifts resource and execution-time distributions", "Each model configuration's executable task-only mean is indexed to 100%; lower values indicate lower observed use or time.")
    left, right = 50, 704
    panel_w = (right - left - 36) / 3
    rows = [
        ("maxrss_mb", "Observed MaxRSS (% of task-only mean)", 292, 448),
        ("wall_sec", "Wall time (% of task-only mean)", 81, 237),
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
    c.drawString(43, 261, "Contract fit (correct + observed MaxRSS within disclosed RAM): 128 MB contract: Claude 5/5, GPT 5/5, Gemini 2/5; 96 MB contract: Claude 4/5, GPT 5/5, Gemini 3/5.")
    legend(c, 50)
    c.setFillColor(SLATE); c.setFont("Helvetica", 7.6)
    c.drawString(43, 31, "Every retained executable observation is visible. The 96 MB samples are independently generated condition-level observations.")


def figure2_combined_resource_time():
    path = OUTPUT / "figure_2_resource_time_distributions.pdf"
    c = canvas.Canvas(str(path), pagesize=(WIDTH, 530))
    draw_figure2_combined_resource_time(c)
    c.save()


def draw_figure_s1_raw_memory(c):
    """Draw Appendix Figure A1 on an existing canvas."""
    base(c, 336, "Observed memory distributions in native units", "Every retained executable result is shown. Each panel uses its own native MiB scale; dashed lines show the 96 and 128 MiB reference boundaries.")
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
        c.setFillColor(colors.black); c.setFont("Helvetica-Bold", 8.5); c.drawCentredString((x0+x1)/2, top+8, f"{label} (0-{maximum:g} MiB)")
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
    c.setFillColor(SLATE); c.setFont("Helvetica", 8); c.drawCentredString(0, 0, "Observed MaxRSS (MiB)")
    c.restoreState()
    c.setFillColor(SLATE); c.setFont("Helvetica",7.6)
    c.drawString(43, 13, "Native panel scales differ by model configuration; Figure 2 provides the aligned within-configuration effect view.")


def figure_s1_raw_memory():
    path = OUTPUT / "appendix_figure_a1_raw_memory.pdf"
    c = canvas.Canvas(str(path), pagesize=(WIDTH, 336))
    draw_figure_s1_raw_memory(c)
    c.save()


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    figure1_condition_cohorts()
    figure2_combined_resource_time()
    figure_s1_raw_memory()
    for name in (
        "figure_1_condition_cohorts.pdf",
        "figure_2_resource_time_distributions.pdf",
        "appendix_figure_a1_raw_memory.pdf",
    ):
        print(OUTPUT / name)


if __name__ == "__main__":
    main()
