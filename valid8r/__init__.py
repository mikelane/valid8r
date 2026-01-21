# valid8r/__init__.py
"""Valid8r: A clean, flexible input validation library for Python."""

from __future__ import annotations

# Import version from generated file
try:
    from valid8r._version import __version__
except ImportError:
    __version__ = '1.27.0'

# Public API re-exports for concise imports
# Modules
from . import prompt
from .core import (
    combinators,
    parsers,
    validators,
)
from .core.errors import (
    ErrorCode,
    ValidationError,
)
from .core.maybe import Maybe
from .core.parsers import (
    EmailAddress,
    PhoneNumber,
    UrlParts,
)
from .core.schema import (
    Field,
    Schema,
)
from .core.type_adapters import from_type

# Types

__all__ = [
    'EmailAddress',
    'ErrorCode',
    'Field',
    'Maybe',
    'PhoneNumber',
    'Schema',
    'UrlParts',
    'ValidationError',
    '__version__',
    'combinators',
    'from_type',
    'parsers',
    'prompt',
    'validators',
]
