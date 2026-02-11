# PDF Template Generator

A modular, command-line PDF template generator that runs multiple Python scripts to produce fillable PDF templates using ReportLab. Templates share centralized branding and settings; new templates can be added without changing core code.

## Features

- **Console-based**: Run a single template or batch-process all templates.
- **Pluggable templates**: Each template is a self-contained script following a consistent contract.
- **Centralized config**: Shared colors, fonts, margins, and output paths in `config/`.
- **Form-ready output**: PDFs include AcroForm fields suitable for Fillout, Adobe Acrobat, and similar tools.

## Installation

Requires Python 3.8+.

```bash
cd pdf-generator
pip install -r requirements.txt
```

## Usage

Run from the `pdf-generator` directory (so that `config` and `templates` packages resolve).

```bash
# List available templates
python generator.py --list

# Generate a single template (writes to output/ by default)
python generator.py --template membership_form

# Generate all templates
python generator.py --all

# Use a custom output directory
python generator.py --template membership_form --output ./pdfs
python generator.py --all -o ./pdfs

# Verbose or quiet logging
python generator.py --template membership_form -v
python generator.py --all -q
```

## Project layout

```
pdf-generator/
├── generator.py           # CLI entry point
├── config/
│   ├── branding.py       # Colors, fonts, style presets
│   └── settings.py       # Output path, margins, page size
├── templates/
│   ├── __init__.py       # Template discovery and registry
│   ├── base.py           # Shared helpers (boxed_section, etc.)
│   ├── membership_form.py
│   └── ...               # Other templates
├── assets/
│   ├── logos/            # Optional logo images (png/jpg)
│   └── fonts/            # Optional custom fonts
├── output/               # Default output directory for PDFs
├── requirements.txt
└── README.md
```

## Adding a new template

1. Add a new Python module under `templates/` (e.g. `templates/employment_agreement.py`).
2. Implement a **generate** function with this signature:

   ```python
   def generate(output_path: Path, **kwargs) -> None:
       """Create the PDF and write it to output_path."""
   ```

3. Use `config.branding` and `config.settings` for styling and layout, and `templates.base` for shared drawing helpers (`boxed_section`, `horizontal_rule`, `spacer_height`).
4. The template will be discovered automatically; its name is the module name (e.g. `employment_agreement`). Run it with:

   ```bash
   python generator.py --template employment_agreement
   ```

Do not add a `generate` callable to `base.py` or `__init__.py`; those are excluded from the registry.

## Assets (logos and fonts)

- **Logos**: Place image files (e.g. `logo.png`) in `assets/logos/`. Templates may draw the first available image for branding; if none is found, they log and continue without a logo.
- **Fonts**: Custom fonts can be placed in `assets/fonts/` and registered in `config/branding.py` if needed.

## Form field naming

Use clear, consistent names for AcroForm fields so they map easily in Fillout or Adobe Acrobat (e.g. `member_name`, `signature_date`, `contact_email`). Avoid spaces and special characters in field names.
