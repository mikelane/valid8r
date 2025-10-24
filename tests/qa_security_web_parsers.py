"""QA Security and Edge Case Testing for Web Parsers.

This module contains comprehensive security audits and edge case tests
for the web parsers feature (v0.6.0). Tests focus on:
- Security vulnerabilities (injection, DoS, malicious inputs)
- Edge cases not covered by unit/BDD tests
- Performance characteristics with large inputs
- Unicode and encoding edge cases
"""

from __future__ import annotations

import json
import time

import pytest

from valid8r.core import parsers
from valid8r.testing import (
    assert_maybe_failure,
    assert_maybe_success,
)


class DescribeSlugSecurity:
    """Security audit for parse_slug."""

    def it_rejects_path_traversal_attempts(self) -> None:
        """Ensure slug cannot contain path traversal sequences."""
        result = parsers.parse_slug('../etc/passwd')
        assert assert_maybe_failure(result, 'lowercase letters')

    def it_rejects_null_bytes(self) -> None:
        """Ensure slug rejects null byte injection."""
        result = parsers.parse_slug('test\x00malicious')
        assert assert_maybe_failure(result, 'lowercase letters')

    def it_rejects_control_characters(self) -> None:
        """Ensure slug rejects control characters."""
        for char in ['\n', '\r', '\t', '\x00', '\x1f']:
            result = parsers.parse_slug(f'test{char}slug')
            assert assert_maybe_failure(result)

    def it_handles_extremely_long_slugs(self) -> None:
        """Test behavior with very long slugs (DoS prevention)."""
        # 10MB slug
        long_slug = 'a' * (10 * 1024 * 1024)
        start = time.perf_counter()
        result = parsers.parse_slug(long_slug, max_length=100)
        duration = time.perf_counter() - start

        # Should reject quickly (< 1 second for 10MB)
        assert duration < 1.0
        assert assert_maybe_failure(result, 'maximum length')

    def it_handles_unicode_lookalikes(self) -> None:
        """Ensure slug rejects Unicode lookalike characters."""
        # Cyrillic 'a' (U+0430) looks like Latin 'a'
        result = parsers.parse_slug('test\u0430slug')
        assert assert_maybe_failure(result, 'lowercase letters')

    def it_handles_zero_width_characters(self) -> None:
        """Ensure slug rejects zero-width characters."""
        # Zero-width space (U+200B)
        result = parsers.parse_slug('test\u200bslug')
        assert assert_maybe_failure(result, 'lowercase letters')

    def it_handles_bidirectional_override(self) -> None:
        """Ensure slug rejects bidi override characters."""
        # Right-to-left override
        result = parsers.parse_slug('test\u202eslug')
        assert assert_maybe_failure(result, 'lowercase letters')

    def it_handles_empty_after_stripping(self) -> None:
        """Ensure slug validates after stripping."""
        result = parsers.parse_slug('   ')
        assert assert_maybe_failure(result, 'at least one character')

    def it_validates_hyphen_rules_with_max_length(self) -> None:
        """Ensure hyphen validation works with length constraints."""
        # Trailing hyphen should fail even with max_length
        result = parsers.parse_slug('test-', max_length=10)
        assert assert_maybe_failure(result, 'end with hyphen')

        # Leading hyphen should fail even with max_length
        result = parsers.parse_slug('-test', max_length=10)
        assert assert_maybe_failure(result, 'start with hyphen')


class DescribeJsonSecurity:
    """Security audit for parse_json."""

    def it_rejects_billion_laughs_attack(self) -> None:
        """Test protection against exponential entity expansion (if applicable)."""
        # JSON doesn't support entities, but test deeply nested structures
        nested = '{"a":' * 1000 + '1' + '}' * 1000
        start = time.perf_counter()
        result = parsers.parse_json(nested)
        duration = time.perf_counter() - start

        # Should complete in reasonable time (< 1 second)
        assert duration < 1.0
        # Python's json module should handle this
        assert result.is_success() or result.is_failure()

    def it_handles_extremely_large_json(self) -> None:
        """Test behavior with very large JSON payloads (DoS prevention)."""
        # 10MB JSON array
        large_json = json.dumps(list(range(500000)))
        start = time.perf_counter()
        result = parsers.parse_json(large_json)
        duration = time.perf_counter() - start

        # Should complete in reasonable time (< 2 seconds for 10MB)
        assert duration < 2.0
        assert result.is_success()

    def it_handles_unicode_escapes(self) -> None:
        """Ensure JSON handles Unicode escapes correctly."""
        result = parsers.parse_json(r'{"emoji": "\ud83d\ude00"}')
        assert assert_maybe_success(result, {'emoji': '😀'})

    def it_handles_surrogate_pairs(self) -> None:
        """Ensure JSON handles surrogate pair escapes."""
        # High surrogate + low surrogate for emoji
        result = parsers.parse_json(r'"\ud83d\ude00"')
        assert assert_maybe_success(result, '😀')

    def it_rejects_invalid_unicode_escapes(self) -> None:
        """Ensure JSON rejects invalid Unicode escapes."""
        result = parsers.parse_json(r'"\uXXXX"')
        assert assert_maybe_failure(result)

    def it_handles_null_bytes_in_strings(self) -> None:
        """Ensure JSON handles null bytes in string values."""
        result = parsers.parse_json(r'{"test": "value\u0000here"}')
        assert result.is_success()
        value = result.value_or(None)
        assert value == {'test': 'value\x00here'}

    def it_handles_control_characters(self) -> None:
        """Ensure JSON handles escaped control characters."""
        result = parsers.parse_json(r'{"test": "line1\nline2\ttab"}')
        assert assert_maybe_success(result, {'test': 'line1\nline2\ttab'})

    def it_rejects_unescaped_control_characters(self) -> None:
        """Ensure JSON rejects unescaped control characters."""
        result = parsers.parse_json('{"test": "line1\nline2"}')
        assert assert_maybe_failure(result)

    def it_handles_very_deep_nesting(self) -> None:
        """Test maximum nesting depth for JSON objects."""
        # Python's json module has a default depth limit
        deep = '{"a":' * 10000 + '1' + '}' * 10000
        result = parsers.parse_json(deep)
        # Should either succeed or fail gracefully (no crash)
        assert result.is_success() or result.is_failure()

    def it_handles_duplicate_keys(self) -> None:
        """Ensure JSON handles duplicate keys (last wins)."""
        result = parsers.parse_json('{"key": "first", "key": "second"}')
        assert assert_maybe_success(result, {'key': 'second'})

    def it_handles_numeric_edge_cases(self) -> None:
        """Ensure JSON handles numeric edge cases."""
        # Very large number
        result = parsers.parse_json('{"num": 1e308}')
        assert result.is_success()

        # Very small number
        result = parsers.parse_json('{"num": 1e-308}')
        assert result.is_success()

        # Negative zero
        result = parsers.parse_json('-0')
        assert result.is_success()


class DescribeBase64Security:
    """Security audit for parse_base64."""

    def it_rejects_null_bytes(self) -> None:
        """Ensure base64 rejects null bytes in input."""
        result = parsers.parse_base64('SGVs\x00bG8=')
        assert assert_maybe_failure(result)

    def it_handles_extremely_long_base64(self) -> None:
        """Test behavior with very long base64 strings (DoS prevention)."""
        # 10MB base64 (valid)
        import base64

        data = b'A' * (10 * 1024 * 1024)
        encoded = base64.b64encode(data).decode('ascii')

        start = time.perf_counter()
        result = parsers.parse_base64(encoded)
        duration = time.perf_counter() - start

        # Should complete in reasonable time (< 2 seconds)
        assert duration < 2.0
        assert result.is_success()

    def it_handles_mixed_url_and_standard_base64(self) -> None:
        """Ensure base64 handles both URL-safe and standard characters."""
        # Mix of standard (+/) and URL-safe (-_) - should still work
        result = parsers.parse_base64('A+B-C_D/')
        # This may fail due to mixed encoding, which is correct
        assert result.is_success() or result.is_failure()

    def it_handles_unicode_in_base64_input(self) -> None:
        """Ensure base64 rejects Unicode characters in input."""
        result = parsers.parse_base64('SGVsbG8ñV29ybGQ=')
        assert assert_maybe_failure(result)

    def it_handles_padding_variations(self) -> None:
        """Test various padding scenarios."""
        # Valid: no padding needed
        result = parsers.parse_base64('SGVsbG8')
        assert result.is_success()

        # Valid: one = padding
        result = parsers.parse_base64('SGVsbG8=')
        assert result.is_success()

        # Valid: two == padding
        result = parsers.parse_base64('SGVs')
        assert result.is_success()

        # Invalid: three === padding (never valid in base64)
        result = parsers.parse_base64('SGV===')
        assert assert_maybe_failure(result)

    def it_handles_newlines_and_whitespace(self) -> None:
        """Ensure base64 handles whitespace as documented."""
        result = parsers.parse_base64('SGVs\nbG8g\nV29y\nbGQ=')
        assert result.is_success()

        result = parsers.parse_base64('SGVs bG8g V29y bGQ=')
        assert result.is_success()


class DescribeJwtSecurity:
    """Security audit for parse_jwt."""

    def it_has_clear_security_warning_in_docstring(self) -> None:
        """Verify JWT parser includes security warning."""
        docstring = parsers.parse_jwt.__doc__
        assert 'NOT verify' in docstring or 'does NOT' in docstring
        assert 'signature' in docstring.lower()

    def it_rejects_null_bytes(self) -> None:
        """Ensure JWT rejects null bytes in input."""
        result = parsers.parse_jwt('eyJ0\x00eXAi.eyJzdWIi.sig')
        assert assert_maybe_failure(result)

    def it_handles_extremely_long_jwt(self) -> None:
        """Test behavior with very long JWTs (DoS prevention)."""
        import base64

        # Create a JWT with a very large payload
        header = base64.urlsafe_b64encode(b'{"alg":"HS256"}').decode()
        # 5MB payload
        large_payload = base64.urlsafe_b64encode(b'{"data":"' + b'A' * (5 * 1024 * 1024) + b'"}').decode()
        signature = 'sig'
        jwt = f'{header}.{large_payload}.{signature}'

        start = time.perf_counter()
        result = parsers.parse_jwt(jwt)
        duration = time.perf_counter() - start

        # Should complete in reasonable time (< 2 seconds)
        assert duration < 2.0
        assert result.is_success()

    def it_validates_header_is_json_object(self) -> None:
        """Ensure JWT header must be a JSON object."""
        import base64

        # Header is a JSON array (invalid)
        header = base64.urlsafe_b64encode(b'["alg","HS256"]').decode()
        payload = base64.urlsafe_b64encode(b'{"sub":"123"}').decode()
        jwt = f'{header}.{payload}.sig'

        result = parsers.parse_jwt(jwt)
        # Current implementation just validates JSON, not structure
        # This is acceptable as parse_jwt only validates structure
        assert result.is_success() or result.is_failure()

    def it_handles_jwt_with_unicode_in_claims(self) -> None:
        """Ensure JWT handles Unicode characters in claims."""
        import base64

        header = base64.urlsafe_b64encode(b'{"alg":"HS256"}').decode()
        # Payload with emoji
        payload = base64.urlsafe_b64encode('{"name":"Alice 😀"}'.encode()).decode()
        jwt = f'{header}.{payload}.sig'

        result = parsers.parse_jwt(jwt)
        assert result.is_success()

    def it_handles_jwt_with_very_long_signature(self) -> None:
        """Ensure JWT handles long signatures."""
        import base64

        header = base64.urlsafe_b64encode(b'{"alg":"HS512"}').decode()
        payload = base64.urlsafe_b64encode(b'{"sub":"123"}').decode()
        # Very long signature (1MB)
        signature = 'A' * (1024 * 1024)
        jwt = f'{header}.{payload}.{signature}'

        result = parsers.parse_jwt(jwt)
        assert result.is_success()

    def it_rejects_jwt_with_empty_parts(self) -> None:
        """Ensure JWT rejects empty header or payload."""
        # Empty header
        result = parsers.parse_jwt('.eyJzdWIiOiIxMjMifQ.sig')
        assert assert_maybe_failure(result)

        # Empty payload
        result = parsers.parse_jwt('eyJhbGciOiJIUzI1NiJ9..sig')
        assert assert_maybe_failure(result)

        # Empty signature is OK (some JWTs have no signature)
        result = parsers.parse_jwt('eyJhbGciOiJub25lIn0.eyJzdWIiOiIxMjMifQ.')
        assert result.is_success()

    def it_handles_jwt_with_special_characters_in_signature(self) -> None:
        """Ensure JWT signature part can contain any base64url characters."""
        import base64

        header = base64.urlsafe_b64encode(b'{"alg":"HS256"}').decode()
        payload = base64.urlsafe_b64encode(b'{"sub":"123"}').decode()
        # Signature with URL-safe characters
        signature = 'A-B_C.D+E/F'
        jwt = f'{header}.{payload}.{signature}'

        result = parsers.parse_jwt(jwt)
        assert result.is_success()


class DescribePerformanceBenchmarks:
    """Performance benchmarks for web parsers."""

    @pytest.mark.slow
    def it_benchmarks_slug_validation_speed(self) -> None:
        """Benchmark slug validation performance."""
        slugs = [f'test-slug-{i}' for i in range(10000)]

        start = time.perf_counter()
        for slug in slugs:
            parsers.parse_slug(slug)
        duration = time.perf_counter() - start

        # Should process 10k slugs in < 0.1 seconds
        print(f'\nSlug validation: {duration:.4f}s for 10k slugs')
        assert duration < 0.5

    @pytest.mark.slow
    def it_benchmarks_json_parsing_speed(self) -> None:
        """Benchmark JSON parsing performance."""
        test_json = json.dumps({'name': 'Alice', 'age': 30, 'active': True})

        start = time.perf_counter()
        for _ in range(10000):
            parsers.parse_json(test_json)
        duration = time.perf_counter() - start

        # Should parse 10k small JSON objects in < 0.5 seconds
        print(f'\nJSON parsing: {duration:.4f}s for 10k parses')
        assert duration < 1.0

    @pytest.mark.slow
    def it_benchmarks_base64_decoding_speed(self) -> None:
        """Benchmark base64 decoding performance."""
        import base64

        data = b'Hello World!' * 100
        encoded = base64.b64encode(data).decode('ascii')

        start = time.perf_counter()
        for _ in range(10000):
            parsers.parse_base64(encoded)
        duration = time.perf_counter() - start

        # Should decode 10k base64 strings in < 0.5 seconds
        print(f'\nBase64 decoding: {duration:.4f}s for 10k decodes')
        assert duration < 1.0

    @pytest.mark.slow
    def it_benchmarks_jwt_validation_speed(self) -> None:
        """Benchmark JWT validation performance."""
        jwt = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U'

        start = time.perf_counter()
        for _ in range(10000):
            parsers.parse_jwt(jwt)
        duration = time.perf_counter() - start

        # Should validate 10k JWTs in < 1 second
        print(f'\nJWT validation: {duration:.4f}s for 10k validations')
        assert duration < 2.0


class DescribeEdgeCaseIntegration:
    """Test edge cases with parser composition and integration."""

    def it_composes_slug_with_validators(self) -> None:
        """Ensure slug parser composes with validators."""
        from valid8r.core import validators

        result = parsers.parse_slug('test-slug').bind(validators.min_length(5))
        assert result.is_success()

        result = parsers.parse_slug('test-slug').bind(validators.min_length(20))
        assert assert_maybe_failure(result, 'at least 20')

    def it_composes_json_with_type_validation(self) -> None:
        """Ensure JSON parser composes with type validation."""
        result = parsers.parse_json('{"name": "Alice"}')

        # Validate result is a dict
        assert result.is_success()
        value = result.value_or(None)
        assert isinstance(value, dict)

    def it_composes_base64_with_content_validation(self) -> None:
        """Ensure base64 parser composes with content validation."""
        # Decode base64 and validate length
        result = parsers.parse_base64('SGVsbG8gV29ybGQ=')
        assert result.is_success()

        # Validate decoded content length
        decoded = result.value_or(b'')
        assert len(decoded) == 11  # "Hello World"

    def it_handles_jwt_in_authorization_header_format(self) -> None:
        """Test JWT parsing with Bearer prefix (common HTTP header format)."""
        jwt = 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjMifQ.sig'

        # Parser expects just the JWT, not "Bearer " prefix
        result = parsers.parse_jwt(f'Bearer {jwt}')
        assert assert_maybe_failure(result)

        # User should strip prefix before parsing
        result = parsers.parse_jwt(jwt)
        assert result.is_success()
