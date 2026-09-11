#!/usr/bin/env python3
"""Generate vector publication figures from the confirmatory analysis JSON."""

from __future__ import annotations

import json
from pathlib import Path

import reportlab
from reportlab.lib.colors import Color, HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "experiments/09_aamas_contract_bridge/analysis/confirmatory_analysis.json"
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
        pageCompression=1, initialFontName=REGULAR_FONT,
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
        pageCompression=1, initialFontName=REGULAR_FONT,
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


def main() -> int:
    payload = json.loads(ANALYSIS.read_text())
    if payload.get("trajectory_count") != 288:
        raise RuntimeError("refusing to plot an incomplete confirmatory matrix")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    primary_figure(payload)
    regime_figure(payload)
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
