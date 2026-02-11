"""Shared brand colors, fonts, and style presets for PDF templates.

Uses ReportLab color and style types. No PDF drawing logic—pure configuration.
"""

from typing import Any, Dict

from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle

# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------

brand_blue = HexColor("#60a5fa")
"""Primary brand blue for headers and accents."""

brand_dark = HexColor("#1e293b")
"""Dark text and strong contrast."""

accent_color = HexColor("#64748b")
"""Secondary accent (e.g. rules, borders)."""

# ---------------------------------------------------------------------------
# Fonts and sizes
# ---------------------------------------------------------------------------

font_name = "Helvetica"
"""Default font family."""

font_size_body = 10
"""Body text size in points."""

font_size_heading = 12
"""Section heading size in points."""

font_size_label = 9
"""Form label size in points."""

# ---------------------------------------------------------------------------
# Paragraph/style presets (for use with ReportLab Paragraph)
# ---------------------------------------------------------------------------


def _make_paragraph_styles() -> Dict[str, ParagraphStyle]:
    """Build paragraph style presets. Returns dict of name -> ParagraphStyle."""
    return {
        "section_header": ParagraphStyle(
            name="SectionHeader",
            fontName=font_name,
            fontSize=font_size_heading,
            textColor=HexColor("#ffffff"),
            spaceAfter=6,
            alignment=1,  # TA_CENTER
        ),
        "body": ParagraphStyle(
            name="Body",
            fontName=font_name,
            fontSize=font_size_body,
            textColor=brand_dark,
            spaceAfter=4,
        ),
        "form_label": ParagraphStyle(
            name="FormLabel",
            fontName=font_name,
            fontSize=font_size_label,
            textColor=brand_dark,
            spaceAfter=2,
        ),
    }


_styles = _make_paragraph_styles()

section_header_style: ParagraphStyle = _styles["section_header"]
"""Style for section headers (e.g. on colored bar)."""

body_style: ParagraphStyle = _styles["body"]
"""Style for body text."""

form_label_style: ParagraphStyle = _styles["form_label"]
"""Style for form field labels."""
