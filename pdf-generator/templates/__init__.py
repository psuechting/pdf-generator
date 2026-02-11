"""Template registry and discovery.

Scans templates/ for modules that expose a generate(output_path, **kwargs) callable.
Template name = module filename without .py (e.g. membership_form).
"""

import importlib.util
import logging
from pathlib import Path
from typing import Callable, List

logger = logging.getLogger(__name__)

_TEMPLATES_DIR = Path(__file__).resolve().parent
_EXCLUDED = {"__init__", "base"}
_Registry = dict  # name -> callable

_registry: _Registry = {}


def _discover_templates() -> _Registry:
    """Scan templates dir for .py modules with a generate() callable; return name -> callable."""
    result: _Registry = {}
    for path in _TEMPLATES_DIR.glob("*.py"):
        name = path.stem
        if name in _EXCLUDED:
            continue
        try:
            spec = importlib.util.spec_from_file_location(
                f"templates.{name}", path
            )
            if spec is None or spec.loader is None:
                continue
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            gen = getattr(mod, "generate", None)
            if callable(gen):
                result[name] = gen
            else:
                logger.debug("Template '%s' has no callable 'generate', skipped", name)
        except Exception as e:
            logger.warning("Failed to load template '%s': %s", name, e)
    return result


def _get_registry() -> _Registry:
    """Lazy-populate and return the template registry."""
    global _registry
    if not _registry:
        _registry = _discover_templates()
    return _registry


def list_templates() -> List[str]:
    """Return sorted list of available template names."""
    return sorted(_get_registry().keys())


def get_generator(template_name: str) -> Callable:
    """Return the generate callable for the given template.

    Args:
        template_name: Name of the template (e.g. 'membership_form').

    Returns:
        Callable with signature generate(output_path: Path, **kwargs) -> None.

    Raises:
        KeyError: If template_name is not registered.
    """
    reg = _get_registry()
    if template_name not in reg:
        raise KeyError(f"Unknown template: {template_name}. Available: {list(reg.keys())}")
    return reg[template_name]
