"""Membership form PDF template: member info, contact, authorization, signatures, optional sections.

Generates a fillable PDF suitable for mapping in Fillout, Adobe Acrobat, etc.
"""

import logging
from pathlib import Path

from reportlab.pdfgen import canvas

from config.branding import (
    brand_dark,
    font_name,
    font_size_body,
    font_size_label,
)
from config.settings import get_logos_path, page_size, default_margin
from templates.base import boxed_section, horizontal_rule, spacer_height

LOG = logging.getLogger(__name__)

# Content area width (page width minus margins)
PAGE_W, PAGE_H = page_size
CONTENT_WIDTH = PAGE_W - 2 * default_margin
FIELD_HEIGHT = 18.0
LABEL_WIDTH = 120.0
FIELD_X = default_margin + LABEL_WIDTH + 8


def _draw_logo(c: canvas.Canvas, x: float, y: float, max_width: float, max_height: float) -> bool:
    """Draw logo from assets/logos if present. Return True if drawn, False otherwise."""
    logos_dir = get_logos_path()
    if not logos_dir.exists():
        LOG.debug("Logos directory not found: %s", logos_dir)
        return False
    # Use first image found (e.g. logo.png)
    for ext in ("png", "jpg", "jpeg"):
        for path in logos_dir.glob(f"*.{ext}"):
            try:
                c.drawImage(str(path), x, y - max_height, width=max_width, height=max_height)
                return True
            except Exception as e:
                LOG.warning("Could not draw logo %s: %s", path, e)
                return False
    LOG.debug("No logo image found in %s", logos_dir)
    return False


def _label(c: canvas.Canvas, x: float, y: float, text: str) -> None:
    """Draw a form label."""
    c.setFont(font_name, font_size_label)
    c.setFillColor(brand_dark)
    c.drawString(x, y - 4, text)


def _text_field(
    c: canvas.Canvas,
    name: str,
    x: float,
    y: float,
    width: float,
    height: float = FIELD_HEIGHT,
) -> None:
    """Add a fillable text field (for GUI mapping)."""
    form = c.acroForm
    form.textfield(
        name=name,
        tooltip=name,
        x=x,
        y=y - height,
        width=width,
        height=height,
        borderStyle="inset",
        forceBorder=True,
    )


def _checkbox(
    c: canvas.Canvas,
    name: str,
    x: float,
    y: float,
    size: float = 14.0,
    checked: bool = False,
) -> None:
    """Add a fillable checkbox."""
    form = c.acroForm
    form.checkbox(
        name=name,
        tooltip=name,
        x=x,
        y=y - size,
        size=size,
        buttonStyle="check",
        forceBorder=True,
        checked=checked,
    )


def generate(output_path: Path, **kwargs: object) -> None:
    """Generate the membership form PDF and write to output_path.

    Args:
        output_path: Full path for the output PDF file.
        **kwargs: Reserved for future options.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(output_path), pagesize=page_size)
    c.setTitle("Membership Form")
    c.setAuthor("PDF Template Generator")

    # Working y from top of page (canvas coords: y increases upward)
    y = PAGE_H - default_margin

    # ----- Logo / branding -----
    logo_h = 40.0
    if not _draw_logo(c, default_margin, y, max_width=180, max_height=logo_h):
        c.setFont(font_name, 16)
        c.setFillColor(brand_dark)
        c.drawString(default_margin, y - 20, "Membership Form")
    y -= logo_h + spacer_height(1.5)
    horizontal_rule(c, default_margin, y, CONTENT_WIDTH)
    y -= spacer_height(1)

    # ----- Section: Member Information -----
    section_h = 100.0
    y = boxed_section(c, default_margin, y, CONTENT_WIDTH, section_h, "Member Information")
    inner_top = y + section_h - 22.0  # below title bar
    row_y = inner_top - 12.0

    _label(c, default_margin + 6, row_y, "Full Name:")
    _text_field(c, "member_name", FIELD_X, row_y, CONTENT_WIDTH - (FIELD_X - default_margin) - 6)
    row_y -= FIELD_HEIGHT + 10
    _label(c, default_margin + 6, row_y, "Member ID:")
    _text_field(c, "member_id", FIELD_X, row_y, 120)
    _label(c, FIELD_X + 140, row_y, "Date:")
    _text_field(c, "member_date", FIELD_X + 170, row_y, 100)
    row_y -= FIELD_HEIGHT + 10
    _label(c, default_margin + 6, row_y, "Address:")
    _text_field(c, "member_address", FIELD_X, row_y, CONTENT_WIDTH - (FIELD_X - default_margin) - 6)
    y = row_y - 12.0

    # ----- Section: Contact Details -----
    section_h = 95.0
    y = boxed_section(c, default_margin, y, CONTENT_WIDTH, section_h, "Contact Details")
    row_y = y + section_h - 22.0 - 12.0

    _label(c, default_margin + 6, row_y, "Email:")
    _text_field(c, "contact_email", FIELD_X, row_y, 220)
    _label(c, default_margin + 6 + 240, row_y, "Phone:")
    _text_field(c, "contact_phone", FIELD_X + 240, row_y, 140)
    row_y -= FIELD_HEIGHT + 10
    _label(c, default_margin + 6, row_y, "Preferred Contact:")
    _checkbox(c, "contact_pref_email", FIELD_X, row_y)
    c.setFont(font_name, font_size_label)
    c.drawString(FIELD_X + 20, row_y - 4, "Email")
    _checkbox(c, "contact_pref_phone", FIELD_X + 80, row_y)
    c.drawString(FIELD_X + 100, row_y - 4, "Phone")
    _checkbox(c, "contact_pref_mail", FIELD_X + 150, row_y)
    c.drawString(FIELD_X + 170, row_y - 4, "Mail")
    y = row_y - 14.0

    # ----- Section: Authorization -----
    section_h = 72.0
    y = boxed_section(c, default_margin, y, CONTENT_WIDTH, section_h, "Authorization")
    row_y = y + section_h - 22.0 - 8.0
    c.setFont(font_name, font_size_body)
    c.setFillColor(brand_dark)
    c.drawString(default_margin + 6, row_y, "I authorize the organization to use my information for membership")
    c.drawString(default_margin + 6, row_y - 14, "and communications. I have read and agree to the terms.")
    row_y -= 32
    _checkbox(c, "authorization_agreed", default_margin + 6, row_y)
    c.drawString(default_margin + 24, row_y - 4, "I agree")
    y = row_y - 14.0

    # ----- Section: Signature -----
    section_h = 85.0
    y = boxed_section(c, default_margin, y, CONTENT_WIDTH, section_h, "Signature")
    row_y = y + section_h - 22.0 - 10.0
    _label(c, default_margin + 6, row_y, "Signature:")
    _text_field(c, "signature", FIELD_X, row_y, 200, height=28)
    row_y -= FIELD_HEIGHT + 14
    _label(c, default_margin + 6, row_y, "Printed Name:")
    _text_field(c, "signature_printed_name", FIELD_X, row_y, 180)
    _label(c, FIELD_X + 200, row_y, "Date:")
    _text_field(c, "signature_date", FIELD_X + 230, row_y, 90)
    y = row_y - 14.0

    # ----- Section: Optional - PAC & Volunteer -----
    section_h = 95.0
    y = boxed_section(c, default_margin, y, CONTENT_WIDTH, section_h, "Optional")
    row_y = y + section_h - 22.0 - 10.0
    _label(c, default_margin + 6, row_y, "PAC contribution:")
    _text_field(c, "pac_amount", FIELD_X, row_y, 80)
    _checkbox(c, "pac_opt_out", FIELD_X + 100, row_y)
    c.setFont(font_name, font_size_label)
    c.drawString(FIELD_X + 118, row_y - 4, "Opt out")
    row_y -= FIELD_HEIGHT + 12
    c.setFont(font_name, font_size_label)
    c.drawString(default_margin + 6, row_y, "Volunteer interests (check all that apply):")
    row_y -= 8
    _checkbox(c, "volunteer_events", default_margin + 6, row_y)
    c.drawString(default_margin + 24, row_y - 4, "Events")
    _checkbox(c, "volunteer_outreach", default_margin + 90, row_y)
    c.drawString(default_margin + 108, row_y - 4, "Outreach")
    _checkbox(c, "volunteer_admin", default_margin + 190, row_y)
    c.drawString(default_margin + 208, row_y - 4, "Admin")
    _checkbox(c, "volunteer_other", default_margin + 280, row_y)
    c.drawString(default_margin + 298, row_y - 4, "Other")
    row_y -= 10
    _label(c, default_margin + 6, row_y, "Other (describe):")
    _text_field(c, "volunteer_other_desc", FIELD_X, row_y, CONTENT_WIDTH - (FIELD_X - default_margin) - 6)

    c.save()
