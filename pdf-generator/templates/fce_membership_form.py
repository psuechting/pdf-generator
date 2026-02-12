"""Membership form PDF template: PCCFCE 3922 union membership commitment.

Matches reference layout: Member Information, Contact, Membership Authorization,
Signature, AFT-OR Political Action Fund (optional), Volunteer Interests (optional).
No dues table. By default produces a fillable PDF with AcroForm fields; use
fillable=False in kwargs (e.g. --no-fillable from CLI) for static placeholder cells.
"""

import logging
from pathlib import Path

from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

from config.branding import (
    brand_blue,
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
FIELD_HEIGHT = 16.0
ROW_STEP = 20.0
LABEL_WIDTH = 158.0  # ~2.2 inch
# Value column: starts after label column + small gap, ends at section right edge
VALUE_X_OFFSET = LABEL_WIDTH + 6
# Light grey for cell borders so entry areas look blank but defined
CELL_BORDER = colors.HexColor("#e5e7eb")
# Vertical centering in row: label baseline and value widget offset from row top
CHECKBOX_SIZE = 12.0
VALUE_TOP_OFFSET = (ROW_STEP - FIELD_HEIGHT) / 2  # 2pt: center 16pt field in 20pt row
CHECKBOX_TOP_OFFSET = (ROW_STEP - CHECKBOX_SIZE) / 2  # 4pt: center 12pt box in 20pt row
LABEL_BASELINE_OFFSET = ROW_STEP / 2 + font_size_label / 2  # center 9pt label in row


def _draw_logos(c: canvas.Canvas, y: float) -> float:
    """Draw up to two logos from assets/logos side by side. Return new y below logos.
    If no logo images exist, draw placeholders so layout is reserved.
    """
    from reportlab.lib.utils import ImageReader

    logo_h = 79.2  # 1.1 inch
    half_w = CONTENT_WIDTH / 2
    paths = []
    logos_dir = get_logos_path()
    if logos_dir.exists():
        for ext in ("png", "jpg", "jpeg"):
            for path in sorted(logos_dir.glob(f"*.{ext}")):
                paths.append(path)
                if len(paths) >= 2:
                    break
            if len(paths) >= 2:
                break
    x = default_margin
    for i, path in enumerate(paths[:2]):
        try:
            img = ImageReader(str(path))
            w, h = img.getSize()
            scale = min(logo_h / h, (half_w - 12) / w)
            draw_w = w * scale
            draw_h = h * scale
            c.drawImage(str(path), x + (half_w - draw_w) / 2, y - draw_h, width=draw_w, height=draw_h)
        except Exception as e:
            LOG.warning("Could not draw logo %s: %s", path, e)
        x += half_w
    # If no logos were drawn, reserve space with placeholders so title position is consistent
    if not paths:
        placeholder_h = min(logo_h, 36)
        for slot in range(2):
            px = default_margin + slot * half_w + (half_w - 60) / 2
            c.setFillColor(colors.HexColor("#f1f5f9"))
            c.rect(px, y - placeholder_h, 60, placeholder_h, stroke=1, fill=1)
            c.setStrokeColor(CELL_BORDER)
            c.setFillColor(brand_dark)
            c.setFont(font_name, 8)
            c.drawCentredString(px + 30, y - placeholder_h / 2 - 3, "Logo")
    return y - logo_h


def _label(c: canvas.Canvas, x: float, row_top_y: float, text: str) -> None:
    """Draw a form label vertically centered in the row (row_top_y = top of row)."""
    c.setFont(font_name, font_size_label)
    c.setFillColor(brand_dark)
    baseline = row_top_y - LABEL_BASELINE_OFFSET
    c.drawString(x, baseline, text)


def _text_field(
    c: canvas.Canvas,
    name: str,
    x: float,
    y: float,
    width: float,
    height: float = FIELD_HEIGHT,
) -> None:
    """Add a fillable text field (AcroForm). y is top-of-cell; PDF uses bottom-left."""
    c.acroForm.textfield(
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
    size: float = 12.0,
    checked: bool = False,
) -> None:
    """Add a fillable checkbox (AcroForm). y is top-of-cell; PDF uses bottom-left."""
    c.acroForm.checkbox(
        name=name,
        tooltip=name,
        x=x,
        y=y - size,
        size=size,
        buttonStyle="check",
        forceBorder=True,
        checked=checked,
    )


def _blank_cell(
    c: canvas.Canvas,
    x: float,
    y: float,
    width: float,
    height: float = FIELD_HEIGHT,
) -> None:
    """Draw a blank entry cell (no AcroForm); for filling by another program."""
    c.setFillColor(colors.white)
    c.setStrokeColor(CELL_BORDER)
    c.setLineWidth(0.25)
    c.rect(x, y - height, width, height, stroke=1, fill=1)


def _blank_checkbox_cell(c: canvas.Canvas, x: float, y: float, size: float = 12.0) -> None:
    """Draw a small blank square as checkbox placeholder."""
    c.setFillColor(colors.white)
    c.setStrokeColor(CELL_BORDER)
    c.setLineWidth(0.25)
    c.rect(x, y - size, size, size, stroke=1, fill=1)


def _section_fields(
    c: canvas.Canvas,
    x: float,
    y: float,
    width: float,
    title: str | None,
    rows: list[tuple[str, str, str]],
    fillable: bool = True,
) -> float:
    """Draw a section: full outer box with optional title, then label + value cells inside.
    Each row is (label, field_name, kind) with kind 'text' or 'checkbox'.
    If fillable, value cells are AcroForm fields; else blank placeholder cells.
    Returns bottom y.
    """
    n = len(rows)
    has_title = title is not None
    title_bar_h = 22.0 if has_title else 0.0
    section_h = title_bar_h + n * ROW_STEP
    bottom_y = boxed_section(c, x, y, width, section_h, title)
    value_width = width - VALUE_X_OFFSET - 6  # keep 6pt from right edge of box

    # Content area: from below title bar (or top of box if no title) down by n rows
    inner_top = y - title_bar_h
    table_bottom = inner_top - n * ROW_STEP  # bottom line of table
    row_y = inner_top  # first row top: align content with grid so fields sit inside cells

    # Vertical divider: label column | value column (only through table height)
    c.setStrokeColor(CELL_BORDER)
    c.setLineWidth(0.25)
    c.line(x + LABEL_WIDTH, inner_top, x + LABEL_WIDTH, table_bottom)

    for i, (label, field_name, kind) in enumerate(rows):
        # Horizontal line above this row: at top of table for i=0, else at bottom of previous row
        # (Cells are FIELD_HEIGHT tall; row slot is ROW_STEP, so line must be at row_y - FIELD_HEIGHT
        # after we've stepped, i.e. at (row_y + ROW_STEP) - FIELD_HEIGHT for i>=1.)
        if i == 0:
            c.line(x, inner_top, x + width, inner_top)
        else:
            c.line(x, row_y + ROW_STEP - FIELD_HEIGHT, x + width, row_y + ROW_STEP - FIELD_HEIGHT)

        label_x = x + 6
        value_x = x + VALUE_X_OFFSET
        _label(c, label_x, row_y, label + ":")
        if kind == "checkbox":
            value_y = row_y - CHECKBOX_TOP_OFFSET  # center 12pt checkbox in row
            if fillable:
                _checkbox(c, field_name, value_x, value_y, size=CHECKBOX_SIZE)
            else:
                _blank_checkbox_cell(c, value_x, value_y, size=CHECKBOX_SIZE)
        else:
            value_y = row_y - VALUE_TOP_OFFSET  # center 16pt field in row
            if fillable:
                _text_field(c, field_name, value_x, value_y, value_width, height=FIELD_HEIGHT)
            else:
                _blank_cell(c, value_x, value_y, value_width, height=FIELD_HEIGHT)
        row_y -= ROW_STEP

    # Bottom line of table (aligns with section box bottom)
    c.line(x, table_bottom, x + width, table_bottom)

    return bottom_y


def generate(output_path: Path, **kwargs: object) -> None:
    """Generate the membership form PDF and write to output_path.

    Args:
        output_path: Full path for the output PDF file.
        **kwargs: Optional 'fillable' (default True) to use AcroForm fields;
            False for static placeholder cells only.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fillable = kwargs.get("fillable", True)

    c = canvas.Canvas(str(output_path), pagesize=page_size)
    c.setTitle("Union Membership Commitment for PCCFCE 3922")
    c.setAuthor("PDF Template Generator")

    y = PAGE_H - default_margin

    # ----- Logos (PCC + AFT side by side) -----
    y = _draw_logos(c, y)
    y -= spacer_height(1)

    # ----- Title -----
    c.setFont(font_name, 16)
    c.setFillColor(brand_blue)
    c.drawCentredString(PAGE_W / 2, y - 6, "Union Membership Commitment for PCCFCE 3922")
    y -= 18
    horizontal_rule(c, default_margin, y, CONTENT_WIDTH)
    y -= spacer_height(1)

    # ----- MEMBER INFORMATION -----
    y = _section_fields(
        c,
        default_margin,
        y,
        CONTENT_WIDTH,
        "MEMBER INFORMATION",
        [
            ("First Name", "first_name", "text"),
            ("Preferred Name", "preferred_name", "text"),
            ("Last Name", "last_name", "text"),
            ("Pronouns", "pronouns", "text"),
            ("Street Address", "street_address", "text"),
            ("City", "city", "text"),
            ("State", "state", "text"),
            ("Zip Code", "zip_code", "text"),
            ("Employee ID", "employee_id", "text"),
        ],
        fillable=fillable,
    )
    y -= spacer_height(0.5)

    # ----- CONTACT INFORMATION -----
    y = _section_fields(
        c,
        default_margin,
        y,
        CONTENT_WIDTH,
        "CONTACT INFORMATION",
        [
            ("Mobile Phone", "mobile_phone", "text"),
            ("Home Phone", "home_phone", "text"),
            ("Work Phone", "work_phone", "text"),
            ("Personal Email", "personal_email", "text"),
            ("Work Email", "work_email", "text"),
        ],
        fillable=fillable,
    )
    y -= spacer_height(0.5)

    # ----- MEMBERSHIP AUTHORIZATION -----
    # Draw the MEMBERSHIP AUTHORIZATION section with prominent commitment text
    section_height = 86  # Space for commitment text + checkbox
    section_bottom_y = boxed_section(
        c,
        default_margin,
        y,
        CONTENT_WIDTH,
        section_height,
        title="MEMBERSHIP AUTHORIZATION",
    )
    commitment_text = (
        "I commit to my union membership in Local 3922, Portland Community College "
        "Federation of Classified Employees, AFT-Oregon, American Federation of Teachers, "
        "AFL-CIO (PCCFCE). I agree to abide by its constitution and bylaws and I authorize "
        "the union to act as my exclusive representative in collective bargaining over "
        "wages, benefits, and other terms and conditions of employment with my employer."
    )
    text_x = default_margin + 14
    text_w = CONTENT_WIDTH - 28
    content_top_y = section_bottom_y + section_height - 22  # below title bar
    line_height = 13
    c.setFont(font_name, font_size_body)
    c.setFillColor(brand_dark)
    draw_y = content_top_y - line_height
    for line in simpleSplit(commitment_text, font_name, font_size_body, text_w):
        c.drawString(text_x, draw_y, line)
        draw_y -= line_height

    # Commitment checkbox section below the text box
    y = section_bottom_y - spacer_height(0.5)
    y = _section_fields(
        c,
        default_margin,
        y,
        CONTENT_WIDTH,
        None,
        [
            ("Commitment Confirmed", "commitment_confirmed", "checkbox")
        ],
        fillable=fillable,
    )
    y -= spacer_height(0.5)

    # ----- SIGNATURE -----
    y = _section_fields(
        c,
        default_margin,
        y,
        CONTENT_WIDTH,
        "SIGNATURE",
        [
            ("Printed Name", "printed_name", "text"),
            ("Signature", "signature", "text"),
            ("Signature Date", "signature_date", "text"),
        ],
        fillable=fillable,
    )
    y -= spacer_height(0.5)

    # If we're too low, start a new page
    if y < default_margin + 120:
        c.showPage()
        y = PAGE_H - default_margin

    # ----- AFT-OREGON POLITICAL ACTION FUND (OPTIONAL) -----
    y = _section_fields(
        c,
        default_margin,
        y,
        CONTENT_WIDTH,
        "AFT-OREGON POLITICAL ACTION FUND (OPTIONAL)",
        [
            ("Selected Monthly Amount", "selected_monthly_amount", "text"),
            ("Custom Amount (if Other)", "custom_amount_if_other", "text"),
            ("PAC Authorization", "pac_authorization", "checkbox"),
        ],
        fillable=fillable,
    )
    y -= spacer_height(0.5)

    # ----- VOLUNTEER INTERESTS (OPTIONAL) -----
    y = _section_fields(
        c,
        default_margin,
        y,
        CONTENT_WIDTH,
        "VOLUNTEER INTERESTS (OPTIONAL)",
        [
            ("Political Action", "volunteer_political_action", "checkbox"),
            ("Communications", "volunteer_communications", "checkbox"),
            ("Accounting & Bookkeeping", "volunteer_accounting_bookkeeping", "checkbox"),
            ("Organizing Events", "volunteer_organizing_events", "checkbox"),
            ("Training & Education", "volunteer_training_education", "checkbox"),
            ("Address Co-Worker Concerns", "volunteer_address_coworker_concerns", "checkbox"),
            ("Social Justice", "volunteer_social_justice", "checkbox"),
            ("Data Input", "volunteer_data_input", "checkbox"),
            ("Share Info with Co-Workers", "volunteer_share_info", "checkbox"),
        ],
        fillable=fillable,
    )

    c.save()

