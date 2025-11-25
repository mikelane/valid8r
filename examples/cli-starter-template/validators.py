"""Validation functions for CLI input using valid8r.

This module demonstrates how to create custom validators using valid8r's
Maybe monad pattern for clean error handling.

Customize this module by:
1. Adding your own validation functions
2. Combining validators using & (and), | (or), ~ (not)
3. Using valid8r's built-in parsers (parse_email, parse_int, etc.)
"""

from __future__ import annotations

from valid8r import (
    Maybe,
    parsers,
)

# Validation constants
MAX_AGE = 150
MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 100


def parse_age(age_str: str) -> Maybe[int]:
    """Parse and validate an age value.

    Args:
        age_str: String representation of age

    Returns:
        Success(age) if valid, Failure(error_message) otherwise

    Examples:
        >>> result = parse_age('25')
        >>> result.is_success()
        True
        >>> result.value_or(0)
        25

        >>> result = parse_age('not-a-number')
        >>> result.is_failure()
        True

    """
    # Handle empty input
    if not age_str or not age_str.strip():
        return Maybe.failure('Age cannot be empty')

    # Parse as integer first
    result = parsers.parse_int(age_str)

    if result.is_failure():
        return Maybe.failure('Age must be a valid integer')

    age = result.value_or(0)

    # Validate age range
    if age < 0:
        return Maybe.failure('Age cannot be negative')

    if age > MAX_AGE:
        return Maybe.failure(f'Age is unrealistic (must be <= {MAX_AGE})')

    return Maybe.success(age)


def parse_name(name_str: str) -> Maybe[str]:
    """Parse and validate a name value.

    Args:
        name_str: String representation of name

    Returns:
        Success(name) if valid, Failure(error_message) otherwise

    Examples:
        >>> result = parse_name('John Doe')
        >>> result.is_success()
        True
        >>> result.value_or('')
        'John Doe'

        >>> result = parse_name('')
        >>> result.is_failure()
        True

    """
    # Handle empty input
    if not name_str or not name_str.strip():
        return Maybe.failure('Name cannot be empty')

    trimmed = name_str.strip()

    # Validate length
    if len(trimmed) < MIN_NAME_LENGTH:
        return Maybe.failure(f'Name is too short (must be at least {MIN_NAME_LENGTH} characters)')

    if len(trimmed) > MAX_NAME_LENGTH:
        return Maybe.failure(f'Name is too long (must be at most {MAX_NAME_LENGTH} characters)')

    return Maybe.success(trimmed)


def parse_email(email_str: str) -> Maybe[str]:
    """Parse and validate an email address.

    Args:
        email_str: String representation of email

    Returns:
        Success(email_string) if valid, Failure(error_message) otherwise

    Examples:
        >>> result = parse_email('user@example.com')
        >>> result.is_success()
        True

        >>> result = parse_email('not-an-email')
        >>> result.is_failure()
        True

    """
    # Handle empty input
    if not email_str or not email_str.strip():
        return Maybe.failure('Email cannot be empty')

    # Use valid8r's built-in email parser
    result = parsers.parse_email(email_str)

    if result.is_failure():
        return Maybe.failure('Must be a valid email address')

    # Return the original email string, not the EmailAddress object
    return Maybe.success(email_str.strip())
