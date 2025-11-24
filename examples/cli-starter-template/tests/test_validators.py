"""Unit tests for validators module.

Tests follow strict TDD discipline: tests written BEFORE implementation.
Each test demonstrates expected behavior using valid8r's Maybe monad.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add parent directory to path to import validators
sys.path.insert(0, str(Path(__file__).parent.parent))

from validators import (
    parse_age,
    parse_email,
    parse_name,
)


class DescribeParseAge:
    """Tests for parse_age validator."""

    @pytest.mark.parametrize(
        ('age_str', 'expected'),
        [
            pytest.param('25', 25, id='valid-25'),
            pytest.param('0', 0, id='zero'),
            pytest.param('150', 150, id='edge-150'),
            pytest.param('18', 18, id='adult-18'),
        ],
    )
    def it_parses_valid_age_strings(self, age_str: str, expected: int) -> None:
        """Parse valid age strings into integers."""
        result = parse_age(age_str)

        assert result.is_success()
        assert result.value_or(None) == expected

    @pytest.mark.parametrize(
        ('invalid_age', 'error_substr'),
        [
            pytest.param('not-a-number', 'integer', id='non-numeric'),
            pytest.param('twenty', 'integer', id='word-twenty'),
            pytest.param('', 'empty', id='empty-string'),
            pytest.param('   ', 'empty', id='whitespace-only'),
            pytest.param('-5', 'negative', id='negative'),
            pytest.param('999', 'unrealistic', id='too-large'),
            pytest.param('25.5', 'integer', id='float'),
        ],
    )
    def it_rejects_invalid_age_strings(self, invalid_age: str, error_substr: str) -> None:
        """Reject invalid age strings with clear error messages."""
        result = parse_age(invalid_age)

        assert result.is_failure()
        assert error_substr.lower() in result.error_or('').lower()


class DescribeParseName:
    """Tests for parse_name validator."""

    @pytest.mark.parametrize(
        ('name_str', 'expected'),
        [
            pytest.param('John Doe', 'John Doe', id='two-words'),
            pytest.param('Alice', 'Alice', id='single-name'),
            pytest.param('Mary Jane Watson', 'Mary Jane Watson', id='three-words'),
            pytest.param('José García', 'José García', id='unicode-accents'),
        ],
    )
    def it_parses_valid_names(self, name_str: str, expected: str) -> None:
        """Parse valid name strings."""
        result = parse_name(name_str)

        assert result.is_success()
        assert result.value_or(None) == expected

    @pytest.mark.parametrize(
        ('invalid_name', 'error_substr'),
        [
            pytest.param('', 'empty', id='empty-string'),
            pytest.param('   ', 'empty', id='whitespace-only'),
            pytest.param('A', 'too short', id='single-char'),
            pytest.param('X' * 101, 'too long', id='over-100-chars'),
        ],
    )
    def it_rejects_invalid_names(self, invalid_name: str, error_substr: str) -> None:
        """Reject invalid names with clear error messages."""
        result = parse_name(invalid_name)

        assert result.is_failure()
        assert error_substr.lower() in result.error_or('').lower()


class DescribeParseEmail:
    """Tests for parse_email validator."""

    @pytest.mark.parametrize(
        'email_str',
        [
            pytest.param('john@example.com', id='simple'),
            pytest.param('alice.smith@company.co.uk', id='subdomain-uk'),
            pytest.param('user+tag@domain.org', id='plus-sign'),
            pytest.param('test_user@test-domain.com', id='underscore-hyphen'),
        ],
    )
    def it_parses_valid_emails(self, email_str: str) -> None:
        """Parse valid email addresses."""
        result = parse_email(email_str)

        assert result.is_success()

    @pytest.mark.parametrize(
        ('invalid_email', 'error_substr'),
        [
            pytest.param('', 'empty', id='empty-string'),
            pytest.param('   ', 'empty', id='whitespace-only'),
            pytest.param('not-an-email', 'valid email', id='no-at-sign'),
            pytest.param('missing-domain@', 'valid email', id='missing-domain'),
            pytest.param('@missing-local.com', 'valid email', id='missing-local'),
            pytest.param('double@@at.com', 'valid email', id='double-at'),
            pytest.param('spaces in@email.com', 'valid email', id='spaces'),
        ],
    )
    def it_rejects_invalid_emails(self, invalid_email: str, error_substr: str) -> None:
        """Reject invalid email addresses with clear error messages."""
        result = parse_email(invalid_email)

        assert result.is_failure()
        assert error_substr.lower() in result.error_or('').lower()
