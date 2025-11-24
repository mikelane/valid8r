"""Async validator library for I/O-bound validation operations.

This module provides validators for operations that require async I/O,
such as database queries, API calls, and DNS lookups.

All validators return `Maybe[T]` and follow the same composable pattern
as synchronous validators.
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
    in the specified field of the specified table.

    Args:
        field: The database field/column to check
        table: The database table to query
        connection: An async database connection object with an execute() method

    Returns:
        An async validator function that returns Maybe[Any]

    Example:
        >>> async def example():
        ...     validator = await unique_in_db(
        ...         field='email',
        ...         table='users',
        ...         connection=db_conn
        ...     )
        ...     result = await validator('new@example.com')
        ...     assert result.is_success()

    """

    async def validator(value: Any) -> Maybe[Any]:  # noqa: ANN401
        """Validate that value is unique in the database."""
        try:
            # Query database to check if value exists
            # noqa: S608 - Using parameterized query ($1), table/field from trusted code
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

    This validator queries the database to ensure the value exists
    in the specified field of the specified table.

    Args:
        field: The database field/column to check
        table: The database table to query
        connection: An async database connection object with an execute() method

    Returns:
        An async validator function that returns Maybe[Any]

    Example:
        >>> async def example():
        ...     validator = await exists_in_db(
        ...         field='id',
        ...         table='categories',
        ...         connection=db_conn
        ...     )
        ...     result = await validator('42')
        ...     assert result.is_success()

    """

    async def validator(value: Any) -> Maybe[Any]:  # noqa: ANN401
        """Validate that value exists in the database."""
        try:
            # Query database to check if value exists
            # noqa: S608 - Using parameterized query ($1), table/field from trusted code
            query = f'SELECT COUNT(*) FROM {table} WHERE {field} = $1'  # noqa: S608
            result = await connection.execute(query, value)
            count = await result.scalar()

            if count == 0:
                return Maybe.failure(f'{field} "{value}" does not exist in {table}')

            return Maybe.success(value)

        except Exception as e:  # noqa: BLE001
            return Maybe.failure(f'Database error: {e}')

    return validator
