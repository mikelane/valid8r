"""DoS Vulnerability Assessment for valid8r parsers.

This script tests all parsers in valid8r/core/parsers.py for DoS vulnerabilities
by measuring their performance when processing malicious inputs (1KB, 1MB).

Following the pattern established in v0.9.1 phone parser fix, we identify parsers
that don't have early length guards before expensive regex operations.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

from valid8r.core.parsers import (
    parse_base64,
    parse_cidr,
    parse_email,
    parse_ip,
    parse_ipv4,
    parse_ipv6,
    parse_json,
    parse_jwt,
    parse_phone,
    parse_slug,
    parse_url,
    parse_uuid,
)


@dataclass
class DoSTestResult:
    """Result of a DoS vulnerability test."""

    parser_name: str
    input_size: int
    elapsed_ms: float
    is_vulnerable: bool
    error_message: str | None


def test_parser_performance(
    parser: Callable[[str], object],
    parser_name: str,
    malicious_input: str,
    threshold_ms: float,
) -> DoSTestResult:
    """Test a parser's performance with malicious input.

    Args:
        parser: Parser function to test
        parser_name: Name of the parser for reporting
        malicious_input: Large input to test with
        threshold_ms: Maximum acceptable time in milliseconds (default: 10ms)

    Returns:
        DoSTestResult with performance metrics

    """
    start = time.perf_counter()
    result = parser(malicious_input)
    elapsed_ms = (time.perf_counter() - start) * 1000

    is_vulnerable = elapsed_ms > threshold_ms

    # Extract error message if failure
    error_msg = None
    if hasattr(result, 'is_failure') and result.is_failure():
        error_msg = result.error_or('')

    return DoSTestResult(
        parser_name=parser_name,
        input_size=len(malicious_input),
        elapsed_ms=elapsed_ms,
        is_vulnerable=is_vulnerable,
        error_message=error_msg,
    )


def main() -> None:  # noqa: PLR0915
    """Run DoS vulnerability assessment on all parsers."""
    print('=' * 80)
    print('DoS Vulnerability Assessment for valid8r parsers')
    print('=' * 80)
    print()

    # Test configurations: (parser, name, malicious_input)
    tests = [
        # Email parser (RFC 5321 max: 254 chars)
        (parse_email, 'parse_email', 'a' * 1000 + '@example.com'),
        # URL parser (browser limit: 2048 chars)
        (parse_url, 'parse_url', 'https://example.com/' + 'a' * 5000),
        # UUID parser (standard format: 36 chars)
        (parse_uuid, 'parse_uuid', '0' * 1000),
        # IPv4 parser (max: 15 chars)
        (parse_ipv4, 'parse_ipv4', '1' * 1000 + '.2.3.4'),
        # IPv6 parser (max: 45 chars)
        (parse_ipv6, 'parse_ipv6', '2001:' + '0' * 1000),
        # IP parser (max: 45 chars)
        (parse_ip, 'parse_ip', '1' * 1000 + '.2.3.4'),
        # CIDR parser (max: ~50 chars)
        (parse_cidr, 'parse_cidr', '1' * 1000 + '.0.0.0/24'),
        # Phone parser (has protection as of v0.9.1)
        (parse_phone, 'parse_phone', '4' * 1000),
        # Slug parser (no clear max, but should be reasonable)
        (parse_slug, 'parse_slug', 'a' * 10000),
        # JSON parser (can be large, but should fail fast on invalid)
        (parse_json, 'parse_json', '{' + 'a' * 10000),
        # JWT parser (can be large, but should fail fast)
        (parse_jwt, 'parse_jwt', 'a' * 10000),
        # Base64 parser (can be large)
        (parse_base64, 'parse_base64', 'A' * 10000 + '==='),
    ]

    results: list[DoSTestResult] = []

    for parser, name, malicious_input in tests:
        print(f'Testing {name}...')
        result = test_parser_performance(parser, name, malicious_input)
        results.append(result)

        # Display result
        status = '❌ VULNERABLE' if result.is_vulnerable else '✓ PROTECTED'
        print(f'  {status}: {result.elapsed_ms:.2f}ms for {result.input_size:,} chars')
        if result.error_message:
            print(
                f'  Error: {result.error_message[:80]}...'
                if len(result.error_message) > 80
                else f'  Error: {result.error_message}'
            )
        print()

    # Summary
    print('=' * 80)
    print('SUMMARY')
    print('=' * 80)
    print()

    vulnerable = [r for r in results if r.is_vulnerable]
    protected = [r for r in results if not r.is_vulnerable]

    print(f'Total parsers tested: {len(results)}')
    print(f'Protected (< 10ms):   {len(protected)}')
    print(f'Vulnerable (>= 10ms): {len(vulnerable)}')
    print()

    if vulnerable:
        print('VULNERABLE PARSERS (need DoS protection):')
        print('-' * 80)
        for r in sorted(vulnerable, key=lambda x: x.elapsed_ms, reverse=True):
            print(f'  {r.parser_name:25s} {r.elapsed_ms:8.2f}ms for {r.input_size:,} chars')
        print()

    if protected:
        print('PROTECTED PARSERS (already have DoS protection or naturally fast):')
        print('-' * 80)
        for r in sorted(protected, key=lambda x: x.elapsed_ms):
            print(f'  {r.parser_name:25s} {r.elapsed_ms:8.2f}ms for {r.input_size:,} chars')
        print()

    # Recommendations
    print('=' * 80)
    print('RECOMMENDATIONS')
    print('=' * 80)
    print()
    print('Based on issue #132 and v0.9.1 phone parser fix:')
    print()
    print('HIGH PRIORITY (add length guards):')
    for r in vulnerable:
        print(f'  - {r.parser_name}: Add early length guard before regex operations')
    print()
    print('Suggested limits (from issue #132):')
    print('  - parse_email():  254 chars (RFC 5321)')
    print('  - parse_url():    2048 chars (browser limit)')
    print('  - parse_uuid():   36 chars (standard format)')
    print('  - parse_ip():     45 chars (IPv6 max)')
    print('  - parse_cidr():   50 chars (IPv6 + CIDR)')
    print('  - parse_slug():   100 chars (reasonable for URL slugs)')
    print('  - parse_json():   1000000 chars (1MB, reasonable for API payloads)')
    print('  - parse_jwt():    10000 chars (10KB, typical JWT size)')
    print('  - parse_base64(): 10000000 chars (10MB, reasonable for files)')


if __name__ == '__main__':
    main()
