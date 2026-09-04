#!/usr/bin/env python3
"""Render the current Markdown manuscript as a review-quality PDF.

The manuscript remains the canonical source.  This renderer deliberately keeps the
layout simple, generates a separate review PDF, and preserves all earlier PDFs.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    Flowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "paper_draft.md"
OUTPUT = ROOT / "output/pdf/substrate_aware_ai_agents_v7_arxiv.pdf"
PAGE_WIDTH, PAGE_HEIGHT = letter
SANS = "AetherSans"
SANS_BOLD = "AetherSansBold"
SANS_ITALIC = "AetherSansItalic"
SANS_BOLD_ITALIC = "AetherSansBoldItalic"
MONO = "AetherMono"
FIGURE_WIDTH = 6.7 * inch

# Draw the archived figure definitions directly onto the manuscript canvas. This
# preserves vectors at every zoom level rather than embedding a PNG preview.
sys.path.insert(0, str(ROOT))
from benchmarks import render_final_paper_figures as figure_renderer

FIGURE_DRAWERS = {
    "figure_1_condition_cohorts.pdf": (
        figure_renderer.draw_figure1_condition_cohorts,
        figure_renderer.WIDTH,
        336,
    ),
    "figure_2_resource_time_distributions.pdf": (
        figure_renderer.draw_figure2_combined_resource_time,
        figure_renderer.WIDTH,
        530,
    ),
    "appendix_figure_a1_raw_memory.pdf": (
        figure_renderer.draw_figure_s1_raw_memory,
        figure_renderer.WIDTH,
        336,
    ),
}


def register_embedded_fonts() -> None:
    """Use embedded TrueType fonts so the standalone arXiv PDF is portable."""
    font_dir = Path("/System/Library/Fonts/Supplemental")
    fonts = {
        SANS: font_dir / "Arial.ttf",
        SANS_BOLD: font_dir / "Arial Bold.ttf",
        SANS_ITALIC: font_dir / "Arial Italic.ttf",
        SANS_BOLD_ITALIC: font_dir / "Arial Bold Italic.ttf",
        MONO: font_dir / "Courier New.ttf",
    }
    for name, path in fonts.items():
        if not path.is_file():
            raise FileNotFoundError(f"Required PDF font is unavailable: {path}")
        pdfmetrics.registerFont(TTFont(name, str(path)))
    pdfmetrics.registerFontFamily(
        SANS,
        normal=SANS,
        bold=SANS_BOLD,
        italic=SANS_ITALIC,
        boldItalic=SANS_BOLD_ITALIC,
    )


class EmbeddedFontCanvas(Canvas):
    """Start every page with an embedded font rather than ReportLab Helvetica."""

    def __init__(self, *args, **kwargs):
        # DocTemplate supplies Helvetica explicitly unless this is overridden.
        kwargs["initialFontName"] = SANS
        kwargs["initialFontSize"] = 12
        kwargs["initialLeading"] = 14.4
        super().__init__(*args, **kwargs)


def clean(text: str) -> str:
    """Translate the small Markdown subset used by the manuscript to ReportLab XML."""
    text = text.strip()
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"!\[[^]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(rf"`([^`]+)`", rf"<font name='{MONO}'>\1</font>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", text)
    return text.replace("--", "-")


class FigureCanvas:
    """Forward figure drawing calls while keeping all manuscript fonts embedded."""

    _FONT_MAP = {"Helvetica": SANS, "Helvetica-Bold": SANS_BOLD}

    def __init__(self, canvas: Canvas):
        self._canvas = canvas

    def setFont(self, name, *args, **kwargs):
        return self._canvas.setFont(self._FONT_MAP.get(name, name), *args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._canvas, name)


class VectorFigure(Flowable):
    """A native-vector figure flowable with its source aspect ratio intact."""

    def __init__(self, drawer, source_width: float, source_height: float):
        super().__init__()
        self.drawer = drawer
        self.source_width = source_width
        self.source_height = source_height
        self.width = FIGURE_WIDTH
        self.height = FIGURE_WIDTH * source_height / source_width

    def wrap(self, available_width, available_height):
        return self.width, self.height

    def draw(self):
        scale = self.width / self.source_width
        self.canv.saveState()
        self.canv.scale(scale, scale)
        self.drawer(FigureCanvas(self.canv))
        self.canv.restoreState()


def footer(canvas, doc):
    canvas.saveState()
    # PDF pages are formally transparent by default; make the review copy render
    # consistently in Preview, Poppler, and browser viewers.
    canvas.setFillColor(colors.white)
    canvas.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
    canvas.setStrokeColor(colors.HexColor("#cbd5e1"))
    canvas.line(doc.leftMargin, 0.52 * inch, PAGE_WIDTH - doc.rightMargin, 0.52 * inch)
    canvas.setFillColor(colors.HexColor("#475569"))
    canvas.setFont(SANS, 8)
    canvas.drawString(doc.leftMargin, 0.35 * inch, "Substrate-Aware AI Agents")
    canvas.drawRightString(PAGE_WIDTH - doc.rightMargin, 0.35 * inch, str(doc.page))
    canvas.restoreState()


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    register_embedded_fonts()
    styles = getSampleStyleSheet()
    title = ParagraphStyle("Title", parent=styles["Title"], fontName=SANS_BOLD, fontSize=20, leading=24, alignment=TA_CENTER, spaceAfter=12)
    author = ParagraphStyle("Author", parent=styles["Normal"], fontName=SANS, fontSize=11, leading=15, alignment=TA_CENTER)
    abstract_head = ParagraphStyle("AbstractHead", parent=styles["Heading2"], fontName=SANS_BOLD, fontSize=12, leading=15, spaceBefore=14, spaceAfter=5)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontName=SANS_BOLD, fontSize=13, leading=16, spaceBefore=16, spaceAfter=7, keepWithNext=True)
    h3 = ParagraphStyle("H3", parent=styles["Heading3"], fontName=SANS_BOLD, fontSize=11, leading=13, spaceBefore=11, spaceAfter=5, keepWithNext=True)
    body = ParagraphStyle("Body", parent=styles["BodyText"], fontName=SANS, fontSize=9.2, leading=13, alignment=TA_JUSTIFY, spaceAfter=6, allowWidows=0, allowOrphans=0)
    caption = ParagraphStyle("Caption", parent=body, fontSize=8.1, leading=10.5, alignment=TA_JUSTIFY, leftIndent=10, rightIndent=10, textColor=colors.HexColor("#334155"))
    code = ParagraphStyle("Code", parent=body, fontName=MONO, fontSize=7.6, leading=9.5, backColor=colors.HexColor("#f1f5f9"), borderColor=colors.HexColor("#cbd5e1"), borderWidth=0.4, borderPadding=6, leftIndent=8, rightIndent=8)
    bullet = ParagraphStyle("Bullet", parent=body, leftIndent=16, firstLineIndent=-9)
    cell = ParagraphStyle("Cell", parent=body, fontSize=7.0, leading=8.4, spaceAfter=0)
    header_cell = ParagraphStyle("HeaderCell", parent=cell, fontName=SANS_BOLD, textColor=colors.white)

    story = []
    lines = SOURCE.read_text().splitlines()
    i = 0
    in_references = False
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if i == 0 and line.startswith("# "):
            story.append(Paragraph(clean(line[2:]), title))
            i += 1
            continue
        if line == "**Manu Agrawal**":
            story.append(Paragraph("<b>Manu Agrawal</b>", author))
            i += 1
            continue
        if line == "*Independent Researcher*":
            story.append(Paragraph("<i>Independent Researcher</i>", author))
            i += 1
            continue
        if line == "manuagrawal2013@gmail.com":
            story.append(Paragraph("manuagrawal2013@gmail.com", author))
            story.append(Spacer(1, 6))
            i += 1
            continue
        if line.startswith("## "):
            heading = line[3:]
            if heading == "Appendix A. Absolute resource profiles":
                story.append(PageBreak())
            style = abstract_head if heading == "Abstract" else h2
            story.append(Paragraph(clean(heading), style))
            in_references = heading == "References"
            i += 1
            continue
        if line.startswith("### "):
            story.append(Paragraph(clean(line[4:]), h3))
            i += 1
            continue
        if line.startswith("!["):
            match = re.search(r"\]\(([^)]+)\)", line)
            if not match:
                raise ValueError(f"Unable to parse figure: {line}")
            figure_name = Path(match.group(1)).name
            try:
                drawer, source_width, source_height = FIGURE_DRAWERS[figure_name]
            except KeyError as exc:
                raise ValueError(f"No vector drawer registered for figure: {figure_name}") from exc
            story.append(
                KeepTogether(
                    [Spacer(1, 5), VectorFigure(drawer, source_width, source_height), Spacer(1, 3)]
                )
            )
            i += 1
            continue
        if line.startswith("```"):
            block = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                block.append(lines[i].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
                i += 1
            story.append(Paragraph("<br/>".join(block), code))
            i += 1
            continue
        if line.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].startswith("|"):
                if not re.match(r"^\|[-:| ]+\|$", lines[i]):
                    table_lines.append([cell.strip() for cell in lines[i].strip("|").split("|")])
                i += 1
            cells = [[Paragraph(clean(value), header_cell if row_index == 0 else cell) for value in row] for row_index, row in enumerate(table_lines)]
            col_count = len(cells[0])
            widths = [1.15 * inch, 1.25 * inch, 0.8 * inch, 0.8 * inch, 0.8 * inch, 0.7 * inch, 1.3 * inch] if col_count == 7 else [6.8 * inch / col_count] * col_count
            table = Table(cells, colWidths=widths, repeatRows=1, hAlign="CENTER")
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, -1), SANS),
                ("FONTNAME", (0, 0), (-1, 0), SANS_BOLD),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]))
            story.append(KeepTogether([Spacer(1, 4), table, Spacer(1, 5)]))
            continue
        if line.startswith("- "):
            bullet_lines = [line[2:].strip()]
            i += 1
            while i < len(lines) and lines[i].strip() and lines[i].startswith(("  ", "\t")):
                bullet_lines.append(lines[i].strip())
                i += 1
            story.append(Paragraph("\u2022 " + clean(" ".join(bullet_lines)), bullet))
            continue
        paragraph_lines = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(("#", "|", "![", "```", "- ")):
            paragraph_lines.append(lines[i])
            i += 1
        text = " ".join(part.strip() for part in paragraph_lines)
        story.append(Paragraph(clean(text), caption if text.startswith("**Figure") or text.startswith("**Table") else body))

    document = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        rightMargin=0.55 * inch,
        leftMargin=0.55 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.72 * inch,
        title="Substrate-Aware AI Agents: Execution Context as a First-Class Input",
        author="Manu Agrawal",
    )
    document.build(
        story,
        onFirstPage=footer,
        onLaterPages=footer,
        canvasmaker=EmbeddedFontCanvas,
    )
    print(OUTPUT)


if __name__ == "__main__":
    main()
