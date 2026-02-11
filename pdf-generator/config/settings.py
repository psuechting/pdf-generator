"""Shared settings: output paths, page size, margins, and asset paths.

Pure configuration; no CLI or template logic.
"""

from pathlib import Path
from typing import Tuple

# ---------------------------------------------------------------------------
# Paths (relative to project root = directory containing generator.py)
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).resolve().parent.parent

default_output_dir: Path = _PROJECT_ROOT / "output"
"""Default directory for generated PDFs."""

# ---------------------------------------------------------------------------
# Page and layout
# ---------------------------------------------------------------------------

default_margin: float = 72.0
"""Default margin in points (1 inch = 72 pt)."""

page_size: Tuple[float, float] = (612.0, 792.0)
"""Page size in points (US Letter: 8.5" x 11")."""


def get_assets_path() -> Path:
    """Return the project assets directory (logos, fonts)."""
    return _PROJECT_ROOT / "assets"


def get_logos_path() -> Path:
    """Return the logos subdirectory under assets."""
    return get_assets_path() / "logos"


def get_fonts_path() -> Path:
    """Return the fonts subdirectory under assets."""
    return get_assets_path() / "fonts"
