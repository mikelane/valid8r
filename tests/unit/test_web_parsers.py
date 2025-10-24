"""Unit tests for web-related parsers (slug, JSON, base64, JWT)."""

from __future__ import annotations

import base64

from valid8r.core import parsers
from valid8r.testing import assert_maybe_success


class DescribeParseSlug:
    """Tests for parse_slug() parser."""

    def it_parses_valid_slug(self) -> None:
        """Parse a valid URL slug."""
        result = parsers.parse_slug('hello-world')
        assert assert_maybe_success(result, 'hello-world')

    def it_parses_slug_with_numbers(self) -> None:
        """Parse slug with numbers."""
        result = parsers.parse_slug('post-123')
        assert assert_maybe_success(result, 'post-123')

    def it_rejects_empty_slug(self) -> None:
        """Reject empty slug."""
        result = parsers.parse_slug('')
        assert result.is_failure()
        assert 'empty' in result.error_or('').lower()

    def it_rejects_uppercase(self) -> None:
        """Reject slug with uppercase."""
        result = parsers.parse_slug('Hello-World')
        assert result.is_failure()
        assert 'lowercase' in result.error_or('').lower()

    def it_rejects_spaces(self) -> None:
        """Reject slug with spaces."""
        result = parsers.parse_slug('hello world')
        assert result.is_failure()
        assert 'invalid' in result.error_or('').lower()

    def it_rejects_leading_hyphen(self) -> None:
        """Reject leading hyphen."""
        result = parsers.parse_slug('-hello')
        assert result.is_failure()
        assert 'start' in result.error_or('').lower()

    def it_rejects_trailing_hyphen(self) -> None:
        """Reject trailing hyphen."""
        result = parsers.parse_slug('hello-')
        assert result.is_failure()
        assert 'end' in result.error_or('').lower()

    def it_rejects_consecutive_hyphens(self) -> None:
        """Reject consecutive hyphens."""
        result = parsers.parse_slug('hello--world')
        assert result.is_failure()
        assert 'consecutive' in result.error_or('').lower()

    def it_enforces_min_length(self) -> None:
        """Enforce minimum length."""
        result = parsers.parse_slug('ab', min_length=3)
        assert result.is_failure()
        assert 'short' in result.error_or('').lower()

    def it_enforces_max_length(self) -> None:
        """Enforce maximum length."""
        result = parsers.parse_slug('a' * 51, max_length=50)
        assert result.is_failure()
        assert 'long' in result.error_or('').lower()


class DescribeParseJson:
    """Tests for parse_json() parser."""

    def it_parses_json_object(self) -> None:
        """Parse JSON object."""
        result = parsers.parse_json('{"key": "value"}')
        assert assert_maybe_success(result, {'key': 'value'})

    def it_parses_json_array(self) -> None:
        """Parse JSON array."""
        result = parsers.parse_json('[1, 2, 3]')
        assert assert_maybe_success(result, [1, 2, 3])

    def it_parses_json_primitives(self) -> None:
        """Parse JSON primitives."""
        assert assert_maybe_success(parsers.parse_json('"hello"'), 'hello')
        assert assert_maybe_success(parsers.parse_json('42'), 42)
        assert assert_maybe_success(parsers.parse_json('true'), True)  # noqa: FBT003
        assert assert_maybe_success(parsers.parse_json('false'), False)  # noqa: FBT003
        assert assert_maybe_success(parsers.parse_json('null'), None)

    def it_rejects_invalid_json(self) -> None:
        """Reject invalid JSON."""
        result = parsers.parse_json('{invalid}')
        assert result.is_failure()
        assert 'json' in result.error_or('').lower()

        result = parsers.parse_json('')
        assert result.is_failure()
        assert 'empty' in result.error_or('').lower()

        result = parsers.parse_json('{"key": ')
        assert result.is_failure()
        assert 'json' in result.error_or('').lower()


class DescribeParseBase64:
    """Tests for parse_base64() parser."""

    def it_parses_valid_base64(self) -> None:
        """Parse valid base64."""
        encoded = base64.b64encode(b'hello').decode('ascii')
        result = parsers.parse_base64(encoded)
        assert assert_maybe_success(result, b'hello')

    def it_parses_without_padding(self) -> None:
        """Parse base64 without padding."""
        encoded = base64.b64encode(b'hello').decode('ascii').rstrip('=')
        result = parsers.parse_base64(encoded)
        assert assert_maybe_success(result, b'hello')

    def it_rejects_empty_string(self) -> None:
        """Reject empty base64."""
        result = parsers.parse_base64('')
        assert result.is_failure()
        assert 'empty' in result.error_or('').lower()

    def it_rejects_invalid_chars(self) -> None:
        """Reject invalid base64 characters."""
        result = parsers.parse_base64('hello@world!')
        assert result.is_failure()
        assert 'invalid' in result.error_or('').lower()


class DescribeParseJwt:
    """Tests for parse_jwt() parser."""

    def it_parses_valid_jwt(self) -> None:
        """Parse valid JWT."""
        jwt = (
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
            '.eyJzdWIiOiIxMjM0NTY3ODkwIn0'
            '.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
        )
        result = parsers.parse_jwt(jwt)
        assert assert_maybe_success(result, jwt)

    def it_rejects_two_parts(self) -> None:
        """Reject JWT with two parts."""
        result = parsers.parse_jwt('part1.part2')
        assert result.is_failure()
        assert 'three parts' in result.error_or('').lower()

    def it_rejects_four_parts(self) -> None:
        """Reject JWT with four parts."""
        result = parsers.parse_jwt('part1.part2.part3.part4')
        assert result.is_failure()
        assert 'three parts' in result.error_or('').lower()

    def it_rejects_empty_jwt(self) -> None:
        """Reject empty JWT."""
        result = parsers.parse_jwt('')
        assert result.is_failure()
        assert 'empty' in result.error_or('').lower()

    def it_rejects_invalid_base64(self) -> None:
        """Reject invalid base64 in JWT."""
        result = parsers.parse_jwt('invalid@.invalid@.invalid@')
        assert result.is_failure()
        assert 'header' in result.error_or('').lower()
