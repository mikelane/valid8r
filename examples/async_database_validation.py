#!/usr/bin/env python3
"""Example: Async database validation with valid8r.

This example demonstrates how to use async validators to check database
constraints like email uniqueness and username availability.

Real-world use case: User registration form validation
- Check if email is already registered (async database query)
- Check if username is available (async database query)
- Validate password strength (sync validation)
- All validations run efficiently with proper error accumulation

Requirements:
    pip install valid8r aiosqlite

Run:
    python examples/async_database_validation.py
"""

from __future__ import annotations

import asyncio
from functools import partial
from typing import Any

import aiosqlite

from valid8r.core import (
    parsers,
    schema,
    validators,
)
from valid8r.core.maybe import (
    Failure,
    Maybe,
    Success,
)

# ============================================================================
# Database Setup (Simulated User Database)
# ============================================================================


async def setup_test_database(db_path: str = ':memory:') -> aiosqlite.Connection:
    """Create a test database with sample users.

    Args:
        db_path: Path to SQLite database (default: in-memory)

    Returns:
        Database connection

    """
    db = await aiosqlite.connect(db_path)

    # Create users table
    await db.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    # Insert sample users
    sample_users = [
        ('admin@example.com', 'admin', 'hash1'),
        ('user@example.com', 'user123', 'hash2'),
        ('alice@example.com', 'alice', 'hash3'),
    ]

    await db.executemany(
        'INSERT INTO users (email, username, password_hash) VALUES (?, ?, ?)',
        sample_users,
    )
    await db.commit()

    return db


# ============================================================================
# Async Validators
# ============================================================================


async def check_email_unique(email: str, db: aiosqlite.Connection) -> Maybe[str]:
    """Check if email is not already registered.

    Args:
        email: Email address to check
        db: Database connection

    Returns:
        Success with email if unique, Failure with error message if taken

    """
    cursor = await db.execute('SELECT COUNT(*) FROM users WHERE email = ?', (email,))
    (count,) = await cursor.fetchone()

    if count > 0:
        return Maybe.failure(f'Email {email} is already registered')
    return Maybe.success(email)


async def check_username_available(username: str, db: aiosqlite.Connection) -> Maybe[str]:
    """Check if username is available.

    Args:
        username: Username to check
        db: Database connection

    Returns:
        Success with username if available, Failure with error message if taken

    """
    cursor = await db.execute('SELECT COUNT(*) FROM users WHERE username = ?', (username,))
    (count,) = await cursor.fetchone()

    if count > 0:
        return Maybe.failure(f'Username {username} is not available')
    return Maybe.success(username)


# ============================================================================
# Schema Definition
# ============================================================================


def create_registration_schema(db: aiosqlite.Connection) -> schema.Schema:
    """Create user registration schema with async validators.

    Args:
        db: Database connection for async validators

    Returns:
        Schema for validating user registration data

    """
    return schema.Schema(
        fields={
            'email': schema.Field(
                parser=parsers.parse_email,
                validators=[
                    # Async validator with dependency injection
                    partial(check_email_unique, db=db),
                ],
                required=True,
            ),
            'username': schema.Field(
                parser=parsers.parse_str,
                validators=[
                    # Sync validators first (fail fast)
                    validators.length(3, 20),
                    validators.matches_regex(r'^[a-zA-Z0-9_]+$'),
                    # Async validator after sync validators pass
                    partial(check_username_available, db=db),
                ],
                required=True,
            ),
            'password': schema.Field(
                parser=parsers.parse_str,
                validators=[
                    # Sync validators only (no database check needed)
                    validators.length(8, 100),
                ],
                required=True,
            ),
        },
        strict=True,
    )


# ============================================================================
# Example Usage
# ============================================================================


async def validate_registration(data: dict[str, Any], db: aiosqlite.Connection) -> Maybe[dict[str, Any]]:
    """Validate user registration data.

    Args:
        data: Registration form data
        db: Database connection

    Returns:
        Success with validated data or Failure with errors

    """
    registration_schema = create_registration_schema(db)

    # Use validate_async for async database checks
    return await registration_schema.validate_async(data, timeout=5.0)


async def example_successful_registration(db: aiosqlite.Connection) -> None:
    """Example: Successful registration with unique email and username."""
    print('\n=== Example 1: Successful Registration ===')

    data = {
        'email': 'bob@example.com',  # Not in database
        'username': 'bob123',  # Not in database
        'password': 'SecurePass123',
    }

    result = await validate_registration(data, db)

    match result:
        case Success(validated_data):
            print('✓ Registration valid:')
            print(f'  Email: {validated_data["email"]}')
            print(f'  Username: {validated_data["username"]}')
            print(f'  Password length: {len(validated_data["password"])} chars')
        case Failure(errors):
            print(f'✗ Registration failed with {len(errors)} errors:')
            for error in errors:
                print(f'  {error.path}: {error.message}')


async def example_duplicate_email(db: aiosqlite.Connection) -> None:
    """Example: Registration fails due to duplicate email."""
    print('\n=== Example 2: Duplicate Email ===')

    data = {
        'email': 'admin@example.com',  # Already in database
        'username': 'newuser',
        'password': 'SecurePass123',
    }

    result = await validate_registration(data, db)

    match result:
        case Success(validated_data):
            print(f'✓ Registration valid: {validated_data}')
        case Failure(errors):
            print(f'✗ Registration failed with {len(errors)} errors:')
            for error in errors:
                print(f'  {error.path}: {error.message}')


async def example_multiple_errors(db: aiosqlite.Connection) -> None:
    """Example: Multiple validation errors (sync and async)."""
    print('\n=== Example 3: Multiple Validation Errors ===')

    data = {
        'email': 'user@example.com',  # Duplicate (async error)
        'username': 'ab',  # Too short (sync error)
        'password': 'weak',  # Too short (sync error)
    }

    result = await validate_registration(data, db)

    match result:
        case Success(validated_data):
            print(f'✓ Registration valid: {validated_data}')
        case Failure(errors):
            print(f'✗ Registration failed with {len(errors)} errors:')
            for error in errors:
                print(f'  {error.path}: {error.message}')


async def example_invalid_format(db: aiosqlite.Connection) -> None:
    """Example: Invalid data format prevents async validation."""
    print('\n=== Example 4: Invalid Format (Fast Fail) ===')

    data = {
        'email': 'not-an-email',  # Invalid format (parser fails)
        'username': 'valid_username',
        'password': 'SecurePass123',
    }

    result = await validate_registration(data, db)

    match result:
        case Success(validated_data):
            print(f'✓ Registration valid: {validated_data}')
        case Failure(errors):
            print(f'✗ Registration failed with {len(errors)} errors:')
            for error in errors:
                print(f'  {error.path}: {error.message}')
            print('\nNote: Async validators were skipped because parser failed')


async def example_concurrent_validation(db: aiosqlite.Connection) -> None:
    """Example: Concurrent async validation of multiple fields."""
    print('\n=== Example 5: Concurrent Async Validation ===')

    data = {
        'email': 'concurrent@example.com',
        'username': 'concurrent_user',
        'password': 'SecurePass123',
    }

    import time

    start_time = time.perf_counter()
    result = await validate_registration(data, db)
    elapsed_ms = (time.perf_counter() - start_time) * 1000

    match result:
        case Success(validated_data):
            print(f'✓ Registration valid: {validated_data}')
            print(f'  Validation completed in {elapsed_ms:.2f}ms')
            print('  Note: Email and username checks ran concurrently')
        case Failure(errors):
            print(f'✗ Registration failed: {errors}')


async def main() -> None:
    """Run all examples."""
    print('Valid8r Async Database Validation Examples')
    print('=' * 50)

    # Setup test database
    db = await setup_test_database()

    try:
        # Run examples
        await example_successful_registration(db)
        await example_duplicate_email(db)
        await example_multiple_errors(db)
        await example_invalid_format(db)
        await example_concurrent_validation(db)

        print('\n' + '=' * 50)
        print('All examples completed!')

    finally:
        await db.close()


if __name__ == '__main__':
    asyncio.run(main())
