"""Async validator library for I/O-bound validation operations.

This module provides validators for operations that require async I/O,
such as database queries, API calls, and DNS lookups.

All validators return `Maybe[T]` and follow the same composable pattern
as synchronous validators. This allows for efficient validation against
external systems without blocking the event loop.

Key Features:
    - Database validation (unique_in_db, exists_in_db)
    - Non-blocking async operations
    - Compatible with Maybe monad pattern
    - Works with any async database connection

Example:
    >>> import asyncio
    >>> from valid8r.async_validators import unique_in_db
    >>>
    >>> async def example():
    ...     # Create validator for checking email uniqueness
    ...     validator = await unique_in_db(
    ...         field='email',
    ...         table='users',
    ...         connection=db_conn
    ...     )
    ...
    ...     # Validate that email is unique
    ...     result = await validator('new@example.com')
    ...     if result.is_success():
    ...         print(f"Email {result.value_or(None)} is available!")
    ...     else:
    ...         print(f"Error: {result.error_or('')}")

"""

from __future__ import annotations

from collections.abc import (
    Awaitable,
    Callable,
)
from typing import Any

from valid8r.core.maybe import Maybe

# Type alias for async validators
AsyncValidator = Callable[[Any], Awaitable[Maybe[Any]]]


async def unique_in_db(
    *,
    field: str,
    table: str,
    connection: Any,  # noqa: ANN401
) -> AsyncValidator:
    """Create a validator that checks if a value is unique in a database table.

    This validator queries the database to ensure the value doesn't already exist
    in the specified field of the specified table. Use this when validating user
    input that must be unique, such as email addresses, usernames, or identifiers.

    The validator executes a COUNT query against the database and returns a Failure
    if the value already exists, or Success if it's unique.

    Args:
        field: The database field/column to check (e.g., 'email', 'username')
        table: The database table to query (e.g., 'users', 'accounts')
        connection: An async database connection object with an execute() method
            that returns a result with a scalar() method. Compatible with asyncpg,
            aiopg, and similar async database libraries.

    Returns:
        An async validator function that:
            - Accepts a value to validate
            - Returns Maybe[Any]: Success(value) if unique, Failure(error_msg) if not
            - Returns Failure for database errors

    Example:
        >>> import asyncio
        >>> import asyncpg
        >>> from valid8r.async_validators import unique_in_db
        >>>
        >>> async def validate_new_user_email():
        ...     # Connect to database
        ...     conn = await asyncpg.connect('postgresql://localhost/mydb')
        ...
        ...     # Create validator
        ...     email_validator = await unique_in_db(
        ...         field='email',
        ...         table='users',
        ...         connection=conn
        ...     )
        ...
        ...     # Validate email uniqueness
        ...     result = await email_validator('new@example.com')
        ...     if result.is_success():
        ...         print(f"Email is available: {result.value_or(None)}")
        ...     else:
        ...         print(f"Email taken: {result.error_or('')}")
        ...
        ...     await conn.close()
        >>>
        >>> asyncio.run(validate_new_user_email())

    Notes:
        - The validator is non-blocking and safe to use in async frameworks
        - Database errors are caught and returned as Failure results
        - The field and table names are interpolated into the SQL query
        - Use parameterized queries to prevent SQL injection

    """

    async def validator(value: Any) -> Maybe[Any]:  # noqa: ANN401
        """Validate that value is unique in the database."""
        try:
            # Query database to check if value exists

            query = f'SELECT COUNT(*) FROM {table} WHERE {field} = $1'  # noqa: S608
            result = await connection.execute(query, value)
            count = await result.scalar()

            if count > 0:
                return Maybe.failure(f'{field} "{value}" already exists in {table}')

            return Maybe.success(value)

        except Exception as e:  # noqa: BLE001
            return Maybe.failure(f'Database error: {e}')

    return validator


async def exists_in_db(
    *,
    field: str,
    table: str,
    connection: Any,  # noqa: ANN401
) -> AsyncValidator:
    """Create a validator that checks if a value exists in a database table.

    This validator queries the database to ensure the value exists in the specified
    field of the specified table. Use this when validating foreign keys, references,
    or ensuring that a related entity exists before proceeding.

    The validator executes a COUNT query against the database and returns a Failure
    if the value doesn't exist, or Success if it does.

    Args:
        field: The database field/column to check (e.g., 'id', 'category_id')
        table: The database table to query (e.g., 'categories', 'users')
        connection: An async database connection object with an execute() method
            that returns a result with a scalar() method. Compatible with asyncpg,
            aiopg, and similar async database libraries.

    Returns:
        An async validator function that:
            - Accepts a value to validate
            - Returns Maybe[Any]: Success(value) if exists, Failure(error_msg) if not
            - Returns Failure for database errors

    Example:
        >>> import asyncio
        >>> import asyncpg
        >>> from valid8r.async_validators import exists_in_db
        >>>
        >>> async def validate_category_reference():
        ...     # Connect to database
        ...     conn = await asyncpg.connect('postgresql://localhost/mydb')
        ...
        ...     # Create validator for category_id foreign key
        ...     category_validator = await exists_in_db(
        ...         field='id',
        ...         table='categories',
        ...         connection=conn
        ...     )
        ...
        ...     # Validate that category exists
        ...     result = await category_validator('electronics')
        ...     if result.is_success():
        ...         print(f"Category exists: {result.value_or(None)}")
        ...     else:
        ...         print(f"Invalid category: {result.error_or('')}")
        ...
        ...     await conn.close()
        >>>
        >>> asyncio.run(validate_category_reference())

    Notes:
        - The validator is non-blocking and safe to use in async frameworks
        - Database errors are caught and returned as Failure results
        - The field and table names are interpolated into the SQL query
        - Use parameterized queries to prevent SQL injection

    """

    async def validator(value: Any) -> Maybe[Any]:  # noqa: ANN401
        """Validate that value exists in the database."""
        try:
            # Query database to check if value exists

            query = f'SELECT COUNT(*) FROM {table} WHERE {field} = $1'  # noqa: S608
            result = await connection.execute(query, value)
            count = await result.scalar()

            if count == 0:
                return Maybe.failure(f'{field} "{value}" does not exist in {table}')

            return Maybe.success(value)

        except Exception as e:  # noqa: BLE001
            return Maybe.failure(f'Database error: {e}')

    return validator
