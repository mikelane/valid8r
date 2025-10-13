"""Smoke test for URL and email parsing functionality.

This script provides a quick sanity check that URL and email parsing
are working correctly without requiring the full test suite.
"""

from __future__ import annotations

from valid8r.core.maybe import (
    Failure,
    Success,
)
from valid8r.core.parsers import (
    parse_email,
    parse_url,
)


def main() -> None:
    """Run smoke tests for URL and email parsing."""
    # URL
    match parse_url('https://example.com/path?q=1#x'):
        case Success(u):
            assert u.scheme == 'https'
            assert u.host == 'example.com'
        case Failure(err):
            msg = f'URL parse failed: {err}'
            raise SystemExit(msg)

    # Email
    match parse_email('user@example.com'):
        case Success(e):
            assert e.local == 'user'
            assert e.domain == 'example.com'
        case Failure(err):
            msg = f'Email parse failed: {err}'
            raise SystemExit(msg)

    print('ok')


if __name__ == '__main__':
    main()
