# valid8r/core/__init__.py
"""Core validation components."""

from __future__ import annotations

from valid8r.core import schema
from valid8r.core.parsers import (
    EmailAddress,
    UrlParts,
    parse_cidr,
    parse_email,
    parse_ip,
    parse_ipv4,
    parse_ipv6,
    parse_url,
)
from valid8r.core.type_adapters import from_type

__all__ = [
    'EmailAddress',
    'UrlParts',
    'from_type',
    'parse_cidr',
    'parse_email',
    'parse_ip',
    # existing exports may be defined elsewhere; explicitly expose IP helpers
    'parse_ipv4',
    'parse_ipv6',
    # URL/Email helpers
    'parse_url',
    # Schema validation
    'schema',
]
