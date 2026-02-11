"""Configuration package: shared branding and settings for PDF templates."""

from config.branding import (  # noqa: F401
    brand_blue,
    brand_dark,
    accent_color,
    font_name,
    font_size_body,
    font_size_heading,
    font_size_label,
    section_header_style,
    body_style,
    form_label_style,
)
from config.settings import (  # noqa: F401
    default_output_dir,
    default_margin,
    page_size,
    get_assets_path,
)

__all__ = [
    "brand_blue",
    "brand_dark",
    "accent_color",
    "font_name",
    "font_size_body",
    "font_size_heading",
    "font_size_label",
    "section_header_style",
    "body_style",
    "form_label_style",
    "default_output_dir",
    "default_margin",
    "page_size",
    "get_assets_path",
]
