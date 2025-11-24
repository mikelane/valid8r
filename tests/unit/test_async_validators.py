"""Unit tests for async validators.

This module tests the async validator library following strict TDD discipline.
Tests are written FIRST, we watch them FAIL (RED), then implement minimal code
to make them PASS (GREEN), then refactor while keeping tests GREEN.
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest


# Mock database connection for testing
class MockAsyncConnection:
    """Mock async database connection for testing."""

    def __init__(self) -> None:
        """Initialize the mock connection."""
        self.data: dict[str, dict[str, set[Any]]] = {}
        self.query_count = 0

    async def execute(self, query: str, *args: Any) -> MockQueryResult:  # noqa: ANN401
        """Execute a query."""
        await asyncio.sleep(0.001)  # Simulate I/O
        self.query_count += 1

        # Parse simple query (this is a mock, not a real SQL parser)
        if 'COUNT' in query:
            parts = query.split()
            table = parts[parts.index('FROM') + 1]
            field = parts[parts.index('WHERE') + 1]
            value = args[0] if args else None

            if table in self.data and field in self.data[table]:
                count = 1 if value in self.data[table][field] else 0
            else:
                count = 0

            return MockQueryResult(count)

        return MockQueryResult(None)

    def add_record(self, table: str, field: str, value: Any) -> None:  # noqa: ANN401
        """Add a record to the mock database."""
        if table not in self.data:
            self.data[table] = {}
        if field not in self.data[table]:
            self.data[table][field] = set()
        self.data[table][field].add(value)


class MockQueryResult:
    """Mock query result."""

    def __init__(self, scalar_value: Any) -> None:  # noqa: ANN401
        """Initialize the mock result."""
        self._scalar_value = scalar_value

    async def scalar(self) -> Any:  # noqa: ANN401
        """Get scalar value from result."""
        return self._scalar_value


class DescribeUniqueInDb:
    """Tests for unique_in_db validator."""

    @pytest.fixture
    def db_connection(self) -> MockAsyncConnection:
        """Create a mock database connection."""
        return MockAsyncConnection()

    @pytest.mark.asyncio
    async def it_validates_unique_value_in_database(self, db_connection: MockAsyncConnection) -> None:
        """It validates a unique value against the database."""
        # Arrange
        from valid8r.async_validators import unique_in_db

        db_connection.add_record('users', 'email', 'existing@example.com')
        validator = await unique_in_db(field='email', table='users', connection=db_connection)

        # Act
        result = await validator('new@example.com')

        # Assert
        assert result.is_success()
        assert result.value_or(None) == 'new@example.com'

    @pytest.mark.asyncio
    async def it_rejects_non_unique_value_in_database(self, db_connection: MockAsyncConnection) -> None:
        """It rejects a non-unique value in the database."""
        # Arrange
        from valid8r.async_validators import unique_in_db

        db_connection.add_record('users', 'email', 'existing@example.com')
        validator = await unique_in_db(field='email', table='users', connection=db_connection)

        # Act
        result = await validator('existing@example.com')

        # Assert
        assert result.is_failure()
        assert 'already exists' in result.error_or('').lower()


class DescribeExistsInDb:
    """Tests for exists_in_db validator."""

    @pytest.fixture
    def db_connection(self) -> MockAsyncConnection:
        """Create a mock database connection."""
        return MockAsyncConnection()

    @pytest.mark.asyncio
    async def it_validates_existing_value_in_database(self, db_connection: MockAsyncConnection) -> None:
        """It validates that a value exists in the database."""
        # Arrange
        from valid8r.async_validators import exists_in_db

        db_connection.add_record('categories', 'id', '42')
        validator = await exists_in_db(field='id', table='categories', connection=db_connection)

        # Act
        result = await validator('42')

        # Assert
        assert result.is_success()
        assert result.value_or(None) == '42'

    @pytest.mark.asyncio
    async def it_rejects_missing_value_in_database(self, db_connection: MockAsyncConnection) -> None:
        """It rejects a value that doesn't exist in the database."""
        # Arrange
        from valid8r.async_validators import exists_in_db

        db_connection.add_record('categories', 'id', '42')
        validator = await exists_in_db(field='id', table='categories', connection=db_connection)

        # Act
        result = await validator('999')

        # Assert
        assert result.is_failure()
        assert 'does not exist' in result.error_or('').lower()
