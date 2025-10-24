"""Unit tests for web-related parsers (slug, JSON, base64, JWT)."""

from __future__ import annotations

import base64

from valid8r.core import parsers


class DescribeParseSlug:
    """Tests for parse_slug() parser."""

    def it_parses_valid_slug(self) -> None:
        """Parse a valid URL slug."""
        result = parsers.parse_slug('hello-world')
        assert result.is_success()
        assert result.value_or(None) == 'hello-world'

    def it_parses_slug_with_numbers(self) -> None:
        """Parse slug with numbers."""
        result = parsers.parse_slug('post-123')
        assert result.is_success()

    def it_rejects_empty_slug(self) -> None:
        """Reject empty slug."""
        result = parsers.parse_slug('')
        assert result.is_failure()

    def it_rejects_uppercase(self) -> None:
        """Reject slug with uppercase."""
        result = parsers.parse_slug('Hello-World')
        assert result.is_failure()

    def it_rejects_spaces(self) -> None:
        """Reject slug with spaces."""
        result = parsers.parse_slug('hello world')
        assert result.is_failure()

    def it_rejects_leading_hyphen(self) -> None:
        """Reject leading hyphen."""
        result = parsers.parse_slug('-hello')
        assert result.is_failure()

    def it_rejects_trailing_hyphen(self) -> None:
        """Reject trailing hyphen."""
        result = parsers.parse_slug('hello-')
        assert result.is_failure()

    def it_rejects_consecutive_hyphens(self) -> None:
        """Reject consecutive hyphens."""
        result = parsers.parse_slug('hello--world')
        assert result.is_failure()

    def it_enforces_min_length(self) -> None:
        """Enforce minimum length."""
        result = parsers.parse_slug('ab', min_length=3)
        assert result.is_failure()

    def it_enforces_max_length(self) -> None:
        """Enforce maximum length."""
        result = parsers.parse_slug('a' * 51, max_length=50)
        assert result.is_failure()


class DescribeParseJson:
    """Tests for parse_json() parser."""

    def it_parses_json_object(self) -> None:
        """Parse JSON object."""
        result = parsers.parse_json('{"key": "value"}')
        assert result.is_success()
        assert result.value_or(None) == {'key': 'value'}

    def it_parses_json_array(self) -> None:
        """Parse JSON array."""
        result = parsers.parse_json('[1, 2, 3]')
        assert result.is_success()
        assert result.value_or(None) == [1, 2, 3]

    def it_parses_json_primitives(self) -> None:
        """Parse JSON primitives."""
        assert parsers.parse_json('"hello"').value_or(None) == 'hello'
        assert parsers.parse_json('42').value_or(None) == 42
        assert parsers.parse_json('true').value_or(None) is True
        assert parsers.parse_json('false').value_or(None) is False
        assert parsers.parse_json('null').value_or(None) is None

    def it_rejects_invalid_json(self) -> None:
        """Reject invalid JSON."""
        assert parsers.parse_json('{invalid}').is_failure()
        assert parsers.parse_json('').is_failure()
        assert parsers.parse_json('{"key": ').is_failure()


class DescribeParseBase64:
    """Tests for parse_base64() parser."""

    def it_parses_valid_base64(self) -> None:
        """Parse valid base64."""
        encoded = base64.b64encode(b'hello').decode('ascii')
        result = parsers.parse_base64(encoded)
        assert result.is_success()
        assert result.value_or(None) == b'hello'

    def it_parses_without_padding(self) -> None:
        """Parse base64 without padding."""
        encoded = base64.b64encode(b'hello').decode('ascii').rstrip('=')
        result = parsers.parse_base64(encoded)
        assert result.is_success()
        assert result.value_or(None) == b'hello'

    def it_rejects_empty_string(self) -> None:
        """Reject empty base64."""
        result = parsers.parse_base64('')
        assert result.is_failure()
        assert 'empty' in result.error_or('').lower()

    def it_rejects_invalid_chars(self) -> None:
        """Reject invalid base64 characters."""
        result = parsers.parse_base64('hello@world!')
        assert result.is_failure()


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
        assert result.is_success()
        assert result.value_or(None) == jwt

    def it_rejects_two_parts(self) -> None:
        """Reject JWT with two parts."""
        result = parsers.parse_jwt('part1.part2')
        assert result.is_failure()

    def it_rejects_four_parts(self) -> None:
        """Reject JWT with four parts."""
        result = parsers.parse_jwt('part1.part2.part3.part4')
        assert result.is_failure()

    def it_rejects_empty_jwt(self) -> None:
        """Reject empty JWT."""
        result = parsers.parse_jwt('')
        assert result.is_failure()

    def it_rejects_invalid_base64(self) -> None:
        """Reject invalid base64 in JWT."""
        result = parsers.parse_jwt('invalid@.invalid@.invalid@')
        assert result.is_failure()
