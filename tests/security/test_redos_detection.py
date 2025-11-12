"""Performance tests for ReDoS detection and prevention.

These tests verify that our parsers are protected against Regular Expression
Denial of Service (ReDoS) attacks by validating input length BEFORE expensive
regex operations.

Following the pattern established in valid8r v0.9.1 for phone parser DoS protection.
"""

from __future__ import annotations

import time

import pytest

from valid8r.core import parsers


class DescribeReDoSProtection:
    """Test suite for ReDoS protection in parsers."""

    def it_phone_parser_rejects_oversized_input_quickly(self) -> None:
        """Phone parser rejects extremely long input in < 10ms to prevent DoS."""
        # Create malicious input (1000 characters)
        malicious_input = '4' * 1000

        start = time.perf_counter()
        result = parsers.parse_phone(malicious_input)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Verify both correctness AND performance
        assert result.is_failure()
        assert 'too long' in result.error_or('').lower()
        assert elapsed_ms < 10, f'Rejection took {elapsed_ms:.2f}ms, should be < 10ms'

    def it_url_parser_handles_oversized_input_safely(self) -> None:
        """URL parser handles very long URLs without performance degradation."""
        # Create a URL with extremely long path
        malicious_url = 'https://example.com/' + 'a' * 10000

        start = time.perf_counter()
        parsers.parse_url(malicious_url)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # URL parsing should be quick even for long inputs
        # urlsplit is implemented in C and very fast
        assert elapsed_ms < 50, f'URL parsing took {elapsed_ms:.2f}ms, should be < 50ms'

    def it_email_parser_handles_oversized_input_safely(self) -> None:
        """Email parser handles very long email addresses without hanging."""
        # Create an email with extremely long local part
        malicious_email = 'a' * 10000 + '@example.com'

        start = time.perf_counter()
        result = parsers.parse_email(malicious_email)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Should reject quickly (email-validator has internal limits)
        assert result.is_failure()
        assert elapsed_ms < 100, f'Email rejection took {elapsed_ms:.2f}ms, should be < 100ms'

    def it_slug_parser_handles_oversized_input_safely(self) -> None:
        """Slug parser handles very long slugs without performance issues."""
        # Create an extremely long slug
        malicious_slug = 'a' * 10000

        start = time.perf_counter()
        parsers.parse_slug(malicious_slug)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Slug parsing is simple string operations, should be fast
        assert elapsed_ms < 20, f'Slug parsing took {elapsed_ms:.2f}ms, should be < 20ms'

    def it_ipv4_parser_handles_oversized_input_safely(self) -> None:
        """IPv4 parser handles very long inputs without hanging."""
        # Create malicious input
        malicious_ip = '192.168.1.' + '1' * 10000

        start = time.perf_counter()
        result = parsers.parse_ipv4(malicious_ip)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Should reject quickly (ipaddress module is well-optimized)
        assert result.is_failure()
        assert elapsed_ms < 20, f'IPv4 rejection took {elapsed_ms:.2f}ms, should be < 20ms'

    def it_ipv6_parser_handles_oversized_input_safely(self) -> None:
        """IPv6 parser handles very long inputs without hanging."""
        # Create malicious input
        malicious_ip = '2001:0db8:85a3::' + '8a2e' * 1000

        start = time.perf_counter()
        result = parsers.parse_ipv6(malicious_ip)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Should reject quickly
        assert result.is_failure()
        assert elapsed_ms < 20, f'IPv6 rejection took {elapsed_ms:.2f}ms, should be < 20ms'

    def it_uuid_parser_handles_oversized_input_safely(self) -> None:
        """UUID parser handles very long inputs without hanging."""
        # Create malicious input (valid UUID format but repeated)
        valid_uuid = '123e4567-e89b-12d3-a456-426614174000'
        malicious_input = valid_uuid * 100

        start = time.perf_counter()
        result = parsers.parse_uuid(malicious_input)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Should reject quickly
        assert result.is_failure()
        assert elapsed_ms < 20, f'UUID rejection took {elapsed_ms:.2f}ms, should be < 20ms'

    def it_json_parser_handles_deeply_nested_objects_safely(self) -> None:
        """JSON parser handles deeply nested objects without stack overflow."""
        # Create deeply nested JSON (100 levels)
        nested_json = '{"a":' * 100 + '1' + '}' * 100

        start = time.perf_counter()
        parsers.parse_json(nested_json)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Should parse or reject within reasonable time
        # Python's json module has built-in depth limits
        assert elapsed_ms < 100, f'JSON parsing took {elapsed_ms:.2f}ms, should be < 100ms'

    def it_base64_parser_handles_oversized_input_safely(self) -> None:
        """Base64 parser handles very long base64 strings without hanging."""
        # Create very long base64 string
        malicious_b64 = 'SGVsbG8gV29ybGQ=' * 1000

        start = time.perf_counter()
        parsers.parse_base64(malicious_b64)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Base64 decoding is fast (C implementation)
        assert elapsed_ms < 50, f'Base64 parsing took {elapsed_ms:.2f}ms, should be < 50ms'

    def it_jwt_parser_handles_oversized_tokens_safely(self) -> None:
        """JWT parser handles very long tokens without hanging."""
        # Create JWT with very long payload
        header = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
        payload = 'eyJzdWIiOiIxMjM0NTY3ODkwIn0' * 100
        signature = 'sig'
        malicious_jwt = f'{header}.{payload}.{signature}'

        start = time.perf_counter()
        parsers.parse_jwt(malicious_jwt)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # JWT parsing should be fast
        assert elapsed_ms < 50, f'JWT parsing took {elapsed_ms:.2f}ms, should be < 50ms'


class DescribeRegexPatternSafety:
    """Test suite to verify regex patterns are not vulnerable to ReDoS."""

    def it_phone_extension_pattern_is_safe(self) -> None:
        """Phone extension regex pattern is not vulnerable to catastrophic backtracking."""
        # The pattern: r'\s*[,;]\s*(\d+)$|\s+(?:x|ext\.?|extension)\s*(\d+)$'
        # Should not exhibit exponential complexity
        import re

        pattern = re.compile(r'\s*[,;]\s*(\d+)$|\s+(?:x|ext\.?|extension)\s*(\d+)$', re.IGNORECASE)

        # Test with adversarial input (many spaces)
        adversarial = ' ' * 1000 + 'x123'

        start = time.perf_counter()
        pattern.search(adversarial)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Should complete quickly (no catastrophic backtracking)
        assert elapsed_ms < 10, f'Pattern matching took {elapsed_ms:.2f}ms, should be < 10ms'

    def it_phone_valid_chars_pattern_is_safe(self) -> None:
        """Phone valid chars regex pattern is not vulnerable to catastrophic backtracking."""
        # The pattern: r'^[\d\s()\-+.]+$'
        # Character class with no nested quantifiers - inherently safe
        import re

        pattern = re.compile(r'^[\d\s()\-+.]+$', re.MULTILINE)

        # Test with long valid input
        adversarial = '123-456-7890 ' * 100

        start = time.perf_counter()
        pattern.match(adversarial)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Should complete quickly
        assert elapsed_ms < 10, f'Pattern matching took {elapsed_ms:.2f}ms, should be < 10ms'

    def it_slug_pattern_is_safe(self) -> None:
        """Slug validation regex pattern is not vulnerable to catastrophic backtracking."""
        # The pattern: r'^[a-z0-9-]+$'
        # Character class with no nested quantifiers - inherently safe
        import re

        pattern = re.compile(r'^[a-z0-9-]+$')

        # Test with long valid input
        adversarial = 'a' * 10000

        start = time.perf_counter()
        pattern.match(adversarial)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Should complete very quickly
        assert elapsed_ms < 5, f'Pattern matching took {elapsed_ms:.2f}ms, should be < 5ms'


class DescribeInputLengthValidation:
    """Test suite to verify parsers validate input length before expensive operations."""

    def it_phone_parser_validates_length_first(self) -> None:
        """Phone parser checks input length BEFORE regex operations."""
        # The phone parser should have this structure:
        # 1. Check None/empty
        # 2. Check length > 100 (DoS mitigation)
        # 3. Then do regex operations

        # Verify this by ensuring oversized input fails with length error
        oversized = '4' * 200
        result = parsers.parse_phone(oversized)

        assert result.is_failure()
        error_msg = result.error_or('').lower()
        assert 'too long' in error_msg or 'length' in error_msg

    @pytest.mark.parametrize(
        ('parser', 'oversized_input'),
        [
            pytest.param(
                parsers.parse_phone,
                '5' * 200,
                id='phone',
            ),
        ],
    )
    def it_parsers_fail_fast_on_oversized_input(self, parser, oversized_input) -> None:
        """All parsers with length validation fail within 10ms."""
        start = time.perf_counter()
        result = parser(oversized_input)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Should fail quickly
        assert result.is_failure()
        assert elapsed_ms < 10, f'Parser took {elapsed_ms:.2f}ms to reject, should be < 10ms'


class DescribeScannerIntegration:
    """Test that the ReDoS scanner correctly identifies safe patterns in codebase."""

    def it_scanner_confirms_codebase_patterns_are_safe(self) -> None:
        """Run scanner on actual codebase to confirm no vulnerabilities."""
        import subprocess

        # Run scanner on parsers.py
        result = subprocess.run(
            ['uv', 'run', 'python', 'scripts/check_regex_safety.py', 'valid8r/core/parsers.py'],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should exit successfully (no vulnerabilities)
        assert result.returncode == 0, f'Scanner found vulnerabilities:\n{result.stdout}\n{result.stderr}'
        assert 'safe' in result.stdout.lower() or 'no' in result.stdout.lower()
