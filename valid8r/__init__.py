# valid8r/__init__.py
"""Valid8r: A clean, flexible input validation library for Python."""

from __future__ import annotations

# Import version from generated file
try:
    from valid8r._version import __version__
except ImportError:
    __version__ = '1.6.0'

# Public API re-exports for concise imports
# Modules
from . import prompt
from .core import (
    combinators,
    parsers,
    validators,
)
from .core.maybe import Maybe
from .core.parsers import (
    EmailAddress,
    PhoneNumber,
    UrlParts,
)

# Types

__all__ = [
    'EmailAddress',
    'Maybe',
    'PhoneNumber',
    'UrlParts',
    '__version__',
    'combinators',
    'parsers',
    'prompt',
    'validators',
]
