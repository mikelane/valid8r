"""Example: Async Database Validation with valid8r.

This example demonstrates how to use async validators to validate user input
against a PostgreSQL database without blocking the event loop.

Requirements:
    pip install asyncpg

Usage:
    python examples/async-validation/database_example.py
"""

from __future__ import annotations

import asyncio
from typing import Any

from valid8r.async_validators import (
    exists_in_db,
    unique_in_db,
)
from valid8r.core.maybe import (
    Failure,
    Success,
)


# Mock database connection for demonstration
class MockAsyncConnection:
    """Mock async database connection for demonstration purposes.

    In a real application, use asyncpg.connect() or similar.
    """

    def __init__(self) -> None:
        """Initialize mock connection with sample data."""
        self.users = {'alice@example.com', 'bob@example.com'}
        self.categories = {'electronics', 'books', 'clothing'}

    async def execute(self, query: str, *args: Any) -> MockQueryResult:  # noqa: ANN401
        """Execute a query (mock implementation)."""
        await asyncio.sleep(0.01)  # Simulate network delay

        # Parse simple COUNT query
        if 'COUNT' in query:
            if 'users' in query and 'email' in query:
                value = args[0] if args else None
                count = 1 if value in self.users else 0
            elif 'categories' in query and 'id' in query:
                value = args[0] if args else None
                count = 1 if value in self.categories else 0
            else:
                count = 0

            return MockQueryResult(count)

        return MockQueryResult(None)


class MockQueryResult:
    """Mock query result."""

    def __init__(self, scalar_value: Any) -> None:  # noqa: ANN401
        """Initialize result."""
        self._scalar_value = scalar_value

    async def scalar(self) -> Any:  # noqa: ANN401
        """Get scalar value from result."""
        return self._scalar_value


async def example_unique_email_validation() -> None:
    """Example: Validate that an email address is unique in the users table."""
    print('=== Example 1: Email Uniqueness Validation ===\n')

    # Create mock database connection
    # In real app: conn = await asyncpg.connect('postgresql://localhost/mydb')
    conn = MockAsyncConnection()

    # Create validator for email uniqueness
    email_validator = await unique_in_db(field='email', table='users', connection=conn)

    # Test with a new email (should succeed)
    result = await email_validator('new@example.com')
    if result.is_success():
        print(f'✓ Email "{result.value_or(None)}" is available')
    else:
        print(f'✗ Error: {result.error_or("")}')

    # Test with an existing email (should fail)
    result = await email_validator('alice@example.com')
    if result.is_success():
        print(f'✓ Email "{result.value_or(None)}" is available')
    else:
        print(f'✗ Error: {result.error_or("")}')

    print()


async def example_category_reference_validation() -> None:
    """Example: Validate that a category ID exists before creating a product."""
    print('=== Example 2: Foreign Key Validation ===\n')

    # Create mock database connection
    conn = MockAsyncConnection()

    # Create validator for category existence
    category_validator = await exists_in_db(field='id', table='categories', connection=conn)

    # Test with valid category (should succeed)
    result = await category_validator('electronics')
    if result.is_success():
        print(f'✓ Category "{result.value_or(None)}" exists')
    else:
        print(f'✗ Error: {result.error_or("")}')

    # Test with invalid category (should fail)
    result = await category_validator('nonexistent')
    if result.is_success():
        print(f'✓ Category "{result.value_or(None)}" exists')
    else:
        print(f'✗ Error: {result.error_or("")}')

    print()


async def example_user_registration_workflow() -> None:
    """Example: Complete user registration workflow with async validation."""
    print('=== Example 3: User Registration Workflow ===\n')

    conn = MockAsyncConnection()

    # Create validators
    email_validator = await unique_in_db(field='email', table='users', connection=conn)

    # Simulate user registration
    email = 'charlie@example.com'

    print(f'Registering user with email: {email}')

    # Validate email uniqueness
    result = await email_validator(email)

    match result:
        case Success(value):
            print(f'✓ Email validation passed: {value}')
            print('  → Proceeding with user creation...')
            print('  → User created successfully!')
        case Failure(error):
            print(f'✗ Email validation failed: {error}')
            print('  → Registration aborted')

    print()


async def example_concurrent_validation() -> None:
    """Example: Validate multiple values concurrently."""
    print('=== Example 4: Concurrent Validation ===\n')

    conn = MockAsyncConnection()

    # Create validator
    email_validator = await unique_in_db(field='email', table='users', connection=conn)

    # Validate multiple emails concurrently
    emails = ['dave@example.com', 'alice@example.com', 'eve@example.com']

    print(f'Validating {len(emails)} emails concurrently...\n')

    # Run validations in parallel
    results = await asyncio.gather(*[email_validator(email) for email in emails])

    # Process results
    for email, result in zip(emails, results, strict=False):
        if result.is_success():
            print(f'✓ {email}: Available')
        else:
            print(f'✗ {email}: {result.error_or("")}')

    print()


async def main() -> None:
    """Run all examples."""
    print('\n' + '=' * 60)
    print('Async Database Validation Examples')
    print('=' * 60 + '\n')

    await example_unique_email_validation()
    await example_category_reference_validation()
    await example_user_registration_workflow()
    await example_concurrent_validation()

    print('=' * 60)
    print('Examples completed!')
    print('=' * 60 + '\n')


if __name__ == '__main__':
    asyncio.run(main())
