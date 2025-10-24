# valid8r/__init__.py
"""Valid8r: A clean, flexible input validation library for Python."""

from __future__ import annotations

__version__ = '0.5.8'

# Public API re-exports for concise imports
# Modules
from . import prompt
from .core import (
    combinators,
    parsers,
    validators,
)
from .core.maybe import Maybe

# Types

__all__ = [
    'Maybe',
    '__version__',
    'combinators',
    'parsers',
    'prompt',
    'validators',
]
