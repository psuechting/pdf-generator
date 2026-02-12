#!/usr/bin/env python3
"""CLI entry point for the PDF template generator.

Run single template, all templates, or list available templates.
"""

import argparse
import logging
import sys
from pathlib import Path

from config.settings import default_output_dir
from templates import get_generator, list_templates

LOG = logging.getLogger("pdf_generator")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate fillable PDF templates using ReportLab.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--template",
        metavar="NAME",
        help="Run a single template by name (e.g. membership_form).",
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="Run all registered templates.",
    )
    group.add_argument(
        "--list",
        action="store_true",
        dest="list_templates",
        help="List available template names and exit.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        metavar="DIR",
        help="Output directory for generated PDFs (default: output/).",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Increase logging verbosity.",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Only log errors.",
    )
    parser.add_argument(
        "--no-fillable",
        action="store_true",
        help="Generate static PDF with placeholder cells only (no AcroForm fields).",
    )
    return parser.parse_args()


def _setup_logging(verbose: bool, quiet: bool) -> None:
    level = logging.INFO
    if verbose:
        level = logging.DEBUG
    elif quiet:
        level = logging.ERROR
    logging.basicConfig(
        format="%(levelname)s: %(message)s",
        level=level,
    )


def _run_template(name: str, output_dir: Path, fillable: bool = True) -> bool:
    """Run one template; return True on success, False on failure."""
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{name}.pdf"
    try:
        gen = get_generator(name)
        LOG.info("Generating %s -> %s", name, output_path)
        gen(output_path, fillable=fillable)
        LOG.info("Wrote %s", output_path)
        return True
    except KeyError as e:
        LOG.error("%s", e)
        return False
    except Exception as e:
        LOG.exception("Template %s failed: %s", name, e)
        return False


def main() -> int:
    args = _parse_args()
    _setup_logging(args.verbose, args.quiet)

    output_dir = args.output if args.output is not None else default_output_dir

    if args.list_templates:
        names = list_templates()
        if not names:
            print("No templates found.")
            return 0
        print("Available templates:")
        for n in names:
            print(f"  {n}")
        return 0

    fillable = not args.no_fillable

    if args.template:
        ok = _run_template(args.template, output_dir, fillable=fillable)
        return 0 if ok else 1

    if args.all:
        names = list_templates()
        if not names:
            LOG.error("No templates found.")
            return 1
        failed = []
        for n in names:
            if not _run_template(n, output_dir, fillable=fillable):
                failed.append(n)
        if failed:
            LOG.error("Failed templates: %s", ", ".join(failed))
            return 1
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
