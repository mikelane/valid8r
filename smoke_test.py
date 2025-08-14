from __future__ import annotations

from valid8r.core.maybe import Failure, Success
from valid8r.core.parsers import parse_email, parse_url


def main() -> None:
    # URL
    match parse_url('https://example.com/path?q=1#x'):
        case Success(u):
            assert u.scheme == 'https' and u.host == 'example.com'
        case Failure(err):
            raise SystemExit(f'URL parse failed: {err}')

    # Email
    match parse_email('user@example.com'):
        case Success(e):
            assert e.local == 'user' and e.domain == 'example.com'
        case Failure(err):
            raise SystemExit(f'Email parse failed: {err}')

    print('ok')


if __name__ == '__main__':
    main()