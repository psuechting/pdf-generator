"""Shared PDF drawing helpers for templates: boxed sections, spacers, rules.

Uses ReportLab canvas. All units in points.
"""

from typing import Optional

from reportlab.lib import colors
from reportlab.pdfgen import canvas

from config.branding import brand_blue, brand_dark, font_name, font_size_heading
from config.settings import default_margin

# Title bar height for boxed sections (points)
SECTION_TITLE_HEIGHT = 22.0


def boxed_section(
    c: canvas.Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
    title: Optional[str] = None,
) -> float:
    """Draw a bordered box with optional title bar (branded color).

    Args:
        c: ReportLab canvas.
        x: Left edge in points.
        y: Top edge in points (y decreases downward in ReportLab).
        width: Box width in points.
        height: Total box height (including title bar if present).
        title: Optional title text for the header bar.

    Returns:
        The y coordinate of the bottom of the box (for stacking below).
    """
    bottom_y = y - height

    # Outline
    c.setStrokeColor(brand_dark)
    c.setLineWidth(0.5)
    c.rect(x, bottom_y, width, height, stroke=1, fill=0)

    if title:
        # Title bar background
        title_bottom = y - SECTION_TITLE_HEIGHT
        c.setFillColor(brand_blue)
        c.rect(x, title_bottom, width, SECTION_TITLE_HEIGHT, stroke=0, fill=1)
        # Redraw left/top/right border so we don't lose the frame
        c.setStrokeColor(brand_dark)
        c.setLineWidth(0.5)
        c.line(x, y, x + width, y)
        c.line(x + width, y, x + width, bottom_y)
        c.line(x, y, x, bottom_y)
        c.line(x, title_bottom, x + width, title_bottom)
        # Title text (white on blue to match reference)
        c.setFillColor(colors.white)
        c.setFont(font_name, font_size_heading)
        c.drawCentredString(x + width / 2, title_bottom + 6, title)

    return bottom_y


def spacer_height(lines: float = 1.0) -> float:
    """Suggested vertical space between sections (points).

    Args:
        lines: Approximate number of line heights (default 1).

    Returns:
        Height in points.
    """
    return 12.0 * lines


def horizontal_rule(
    c: canvas.Canvas,
    x: float,
    y: float,
    width: float,
    thickness: float = 0.5,
) -> None:
    """Draw a horizontal line (e.g. separator).

    Args:
        c: ReportLab canvas.
        x: Left x in points.
        y: y position in points.
        width: Line length in points.
        thickness: Line thickness in points.
    """
    c.setStrokeColor(brand_dark)
    c.setLineWidth(thickness)
    c.line(x, y, x + width, y)
