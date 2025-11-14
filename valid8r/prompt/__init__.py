# valid8r/prompt/__init__.py
"""Input prompting functionality for command-line applications.

This module provides interactive prompting with validation, parsing, and
pluggable I/O providers for testing and alternative UIs.
"""

from __future__ import annotations

from .basic import ask
from .io_provider import (
    BuiltinIOProvider,
    IOProvider,
    TestIOProvider,
)

__all__ = [
    'BuiltinIOProvider',
    'IOProvider',
    'TestIOProvider',
    'ask',
]
