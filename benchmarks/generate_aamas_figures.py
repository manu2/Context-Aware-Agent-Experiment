#!/usr/bin/env python3
"""Generate vector publication figures from the confirmatory analysis JSON."""

from __future__ import annotations

import json
import math
from pathlib import Path

import reportlab
from reportlab.lib.colors import Color, HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "experiments/09_aamas_contract_bridge/analysis/confirmatory_analysis.json"
SECONDARY = ROOT / "experiments/09_aamas_contract_bridge/analysis/aamas_secondary_analysis.json"
OUTPUT = ROOT / "paper/aamas2027/figures"
COLORS = {"P": HexColor("#0072B2"), "R": HexColor("#D55E00"), "G": HexColor("#666666")}
FONT_DIR = Path(reportlab.__file__).resolve().parent / "fonts"
REGULAR_FONT = "FigureVera"
BOLD_FONT = "FigureVeraBold"

pdfmetrics.registerFont(TTFont(REGULAR_FONT, FONT_DIR / "Vera.ttf"))
pdfmetrics.registerFont(TTFont(BOLD_FONT, FONT_DIR / "VeraBd.ttf"))


def text(c: canvas.Canvas, x: float, y: float, value: str, size: float = 8,
         bold: bool = False, center: bool = False, color=HexColor("#18243A")) -> None:
    font = BOLD_FONT if bold else REGULAR_FONT
    c.setFont(font, size)
    c.setFillColor(color)
    if center:
        x -= stringWidth(value, font, size) / 2
    c.drawString(x, y, value)


def primary_figure(payload: dict) -> None:
    width, height = 735, 205
    c = canvas.Canvas(
        str(OUTPUT / "primary_suitability.pdf"), pagesize=(width, height),
        pageCompression=1, initialFontName=REGULAR_FONT, invariant=1,
    )
    overall = {r["condition"]: r for r in payload["binary_breakdowns"]["overall"]}
    models = {}
    for row in payload["binary_breakdowns"]["model"]:
        models.setdefault(row["model"], {})[row["condition"]] = row
    panels = [
        ("All configurations", overall),
        ("Claude Sonnet 5", models["claude-sonnet-5"]),
        ("GPT-5.6 Sol", models["gpt-5.6-sol"]),
        ("Gemini 3.8 Flash", models["gemini-3.8-flash"]),
    ]
    text(c, width / 2, 188, "Exact pre-execution contracts improve first-pass operational suitability",
         12, True, True)
    left, right, bottom, top, gap = 48, 12, 42, 161, 12
    panel_w = (width - left - right - gap * 3) / 4
    for panel_index, (title, rows) in enumerate(panels):
        x0 = left + panel_index * (panel_w + gap)
        text(c, x0 + panel_w / 2, 169, title, 8.5, True, True)
        for tick in (0, 25, 50, 75, 100):
            y = bottom + (top - bottom) * tick / 100
            c.setStrokeColor(HexColor("#D8DEE7")); c.setLineWidth(0.5)
            c.line(x0, y, x0 + panel_w, y)
            if panel_index == 0:
                text(c, x0 - 27, y - 2.5, f"{tick}%", 6.5, color=HexColor("#526075"))
        for condition_index, condition in enumerate("PRG"):
            row = rows[condition]
            x = x0 + panel_w * (condition_index + 1) / 4
            value = 100 * row["first_pass_rate"]
            low, high = [100 * v for v in row["first_pass_wilson_95"]]
            y, yl, yh = [bottom + (top - bottom) * v / 100 for v in (value, low, high)]
            c.setStrokeColor(COLORS[condition]); c.setLineWidth(1.2)
            c.line(x, yl, x, yh); c.line(x - 3, yl, x + 3, yl); c.line(x - 3, yh, x + 3, yh)
            c.setFillColor(COLORS[condition]); c.circle(x, y, 3.5, fill=1, stroke=0)
            text(c, x, min(yh + 4, top + 1), f"{row['first_pass_suitable']}/{row['n']}",
                 6.5, True, True, COLORS[condition])
            text(c, x, 29, condition, 7.5, True, True)
    c.save()


def regime_figure(payload: dict) -> None:
    width, height = 470, 190
    c = canvas.Canvas(
        str(OUTPUT / "effect_by_task_environment.pdf"), pagesize=(width, height),
        pageCompression=1, initialFontName=REGULAR_FONT, invariant=1,
    )
    rows = payload["binary_breakdowns"]["family_environment"]
    indexed = {(r["family"], r["environment"], r["condition"]): r for r in rows}
    regimes = [
        ("ETL", "memory-tight", "etl", "memory_tight"),
        ("Numerical", "memory-tight", "numerical", "memory_tight"),
        ("Numerical", "latency-tight", "numerical", "latency_tight"),
        ("ETL", "latency-tight", "etl", "latency_tight"),
    ]
    text(c, width / 2, 171, "First-pass advantage by task–environment regime", 11.5, True, True)
    x0, y0, cell_w, cell_h = 94, 51, 88, 43
    for column, (family_label, env_label, family, env) in enumerate(regimes):
        text(c, x0 + column * cell_w + cell_w / 2, 35, family_label, 7.5, True, True)
        text(c, x0 + column * cell_w + cell_w / 2, 24, env_label, 7, center=True)
        for row_index, comparison in enumerate(("R", "G")):
            value = 100 * (indexed[(family, env, "P")]["first_pass_rate"] - indexed[(family, env, comparison)]["first_pass_rate"])
            intensity = min(max(value / 85, 0), 1)
            base, dark = (235, 244, 250), (0, 82, 145)
            rgb = tuple((base[i] + (dark[i] - base[i]) * intensity) / 255 for i in range(3))
            y = y0 + (1 - row_index) * cell_h
            c.setFillColor(Color(*rgb)); c.rect(x0 + column * cell_w, y, cell_w, cell_h, fill=1, stroke=0)
            label_color = white if value >= 45 else HexColor("#152238")
            text(c, x0 + column * cell_w + cell_w / 2, y + 17,
                 f"{value:+.1f} pp", 9, True, True, label_color)
    text(c, 14, y0 + cell_h + 17, "P minus R", 8, True)
    text(c, 14, y0 + 17, "P minus G", 8, True)
    c.save()


def rounded_box(c: canvas.Canvas, x: float, y: float, w: float, h: float,
                label: str, fill: str, subtitle: str | None = None) -> None:
    c.setFillColor(HexColor(fill)); c.setStrokeColor(HexColor("#8A98AA")); c.setLineWidth(0.8)
    c.roundRect(x, y, w, h, 5, fill=1, stroke=1)
    text(c, x + w / 2, y + h / 2 + (4 if subtitle else -2), label, 8.2, True, True)
    if subtitle:
        text(c, x + w / 2, y + h / 2 - 9, subtitle, 6.2, center=True, color=HexColor("#526075"))


def arrow(c: canvas.Canvas, x1: float, y1: float, x2: float, y2: float,
          color: str = "#607086") -> None:
    c.setStrokeColor(HexColor(color)); c.setFillColor(HexColor(color)); c.setLineWidth(1.1)
    c.line(x1, y1, x2, y2)
    angle = math.atan2(y2 - y1, x2 - x1)
    for offset in (-0.55, 0.55):
        c.line(x2, y2, x2 - 6 * math.cos(angle + offset), y2 - 6 * math.sin(angle + offset))


def architecture_figure() -> None:
    width, height = 735, 215
    c = canvas.Canvas(str(OUTPUT / "contract_bridge_architecture.pdf"), pagesize=(width, height),
                      pageCompression=1, initialFontName=REGULAR_FONT, invariant=1)
    text(c, width / 2, 197, "Execution Contract Bridge: persistent target state across planning and recovery",
         11.5, True, True)
    rounded_box(c, 18, 117, 105, 42, "Target substrate", "#EEF3F8", "limits + runtime")
    rounded_box(c, 151, 117, 105, 42, "Target adapter", "#EEF3F8", "inspect + normalize")
    rounded_box(c, 284, 117, 118, 42, "Typed contract C", "#DCEFFC", "RAM, CPU, deadline")
    rounded_box(c, 430, 117, 116, 42, "Context renderer", "#DCEFFC", "controls visibility")
    rounded_box(c, 574, 117, 142, 42, "Agent plan selection", "#E7F5EA", "generate program A1")
    for x1, x2 in ((123,151),(256,284),(402,430),(546,574)):
        arrow(c, x1, 138, x2 - 4, 138)

    rounded_box(c, 574, 39, 142, 42, "Verified execution", "#FFF0E8", "cgroup + oracle")
    rounded_box(c, 396, 39, 142, 42, "Observation O1", "#FFF0E8", "result + failure signal")
    rounded_box(c, 218, 39, 142, 42, "Bounded recovery", "#E7F5EA", "generate program A2")
    arrow(c, 645, 117, 645, 85)
    arrow(c, 574, 60, 542, 60)
    arrow(c, 396, 60, 364, 60)
    c.setStrokeColor(HexColor("#607086")); c.setLineWidth(1.1)
    c.line(289, 81, 289, 101); c.line(289, 101, 645, 101)
    arrow(c, 645, 101, 645, 85)
    text(c, 493, 106, "execute recovery action", 6.4, center=True, color=HexColor("#526075"))

    c.setStrokeColor(COLORS["P"]); c.setLineWidth(2.2); c.line(405, 170, 570, 170)
    arrow(c, 570, 170, 570, 151, "#0072B2")
    text(c, 487, 177, "P: disclose C before A1", 7.2, True, True, COLORS["P"])
    c.setStrokeColor(HexColor("#009E73")); c.setLineWidth(2.2); c.line(343, 117, 343, 85)
    arrow(c, 343, 85, 343, 81, "#009E73")
    text(c, 335, 91, "L: add C to O1 before A2", 7.2, True, False, HexColor("#007A5A"))
    text(c, 18, 12, "R receives O1 without C; G receives a generic efficiency instruction without target values.",
         6.8, color=HexColor("#526075"))
    c.save()


def recovery_figure(secondary: dict) -> None:
    late = secondary["late_disclosure"]
    width, height = 470, 205
    c = canvas.Canvas(str(OUTPUT / "matched_recovery.pdf"), pagesize=(width, height),
                      pageCompression=1, initialFontName=REGULAR_FONT, invariant=1)
    text(c, width / 2, 187, "Exact contract state transforms recovery on identical failures",
         11.2, True, True)
    text(c, width / 2, 173, "82 archived R first-attempt failures; same program and authentic observation",
         7.1, center=True, color=HexColor("#526075"))
    left, bottom, top, bar_w = 88, 43, 151, 70
    values = (("Symptoms only", late["archived_R_symptom_only_recovered"], COLORS["R"]),
              ("+ exact contract", late["late_contract_recovered"], HexColor("#009E73")))
    for i, (label, value, color) in enumerate(values):
        x = left + i * 165
        h = (top - bottom) * value / 82
        c.setFillColor(color); c.roundRect(x, bottom, bar_w, h, 3, fill=1, stroke=0)
        text(c, x + bar_w / 2, bottom + h + 8, f"{value}/82", 11, True, True, color)
        text(c, x + bar_w / 2, 27, label, 7.5, True, True)
    c.setStrokeColor(HexColor("#B9C4D1")); c.setLineWidth(0.7); c.line(57, bottom, 393, bottom)
    text(c, 404, 133, "35", 14, True, True, HexColor("#009E73"))
    text(c, 404, 120, "improved", 6.7, center=True, color=HexColor("#526075"))
    text(c, 404, 86, "1", 14, True, True, COLORS["R"])
    text(c, 404, 73, "regressed", 6.7, center=True, color=HexColor("#526075"))
    text(c, width / 2, 8, "Exact two-sided McNemar p = 1.08e-9", 6.8, True, True,
         color=HexColor("#526075"))
    c.save()


def main() -> int:
    payload = json.loads(ANALYSIS.read_text())
    secondary = json.loads(SECONDARY.read_text())
    if payload.get("trajectory_count") != 288:
        raise RuntimeError("refusing to plot an incomplete confirmatory matrix")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    primary_figure(payload)
    regime_figure(payload)
    architecture_figure()
    recovery_figure(secondary)
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
