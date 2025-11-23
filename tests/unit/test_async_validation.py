"""Unit tests for async validation support.

This module contains TDD tests for:
- Maybe.bind_async() method for async validator composition
- Schema.validate_async() method for async validation
- Detection and execution of async validators
- Concurrent execution of multiple async validators
- Error accumulation in async validation
"""

from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from valid8r.core.maybe import Maybe
    from valid8r.core.parsers import EmailAddress


class DescribeMaybeBindAsync:
    """Tests for Maybe.bind_async() method."""

    @pytest.mark.asyncio
    async def it_applies_async_function_to_success(self) -> None:
        """Apply async function to successful Maybe."""
        from valid8r.core.maybe import Maybe

        async def async_double(x: int) -> Maybe[int]:
            await asyncio.sleep(0.001)  # Simulate async operation
            return Maybe.success(x * 2)

        result = await Maybe.success(21).bind_async(async_double)

        assert result.is_success()
        assert result.value_or(None) == 42

    @pytest.mark.asyncio
    async def it_skips_async_function_on_failure(self) -> None:
        """Skip async function for failed Maybe."""
        from valid8r.core.maybe import Maybe

        call_count = 0

        async def async_double(x: int) -> Maybe[int]:
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.001)
            return Maybe.success(x * 2)

        result = await Maybe.failure('error').bind_async(async_double)

        assert result.is_failure()
        assert result.error_or('') == 'error'
        assert call_count == 0  # Function not called

    @pytest.mark.asyncio
    async def it_propagates_async_failure(self) -> None:
        """Propagate failure from async function."""
        from valid8r.core.maybe import Maybe

        async def async_validator(x: int) -> Maybe[int]:
            await asyncio.sleep(0.001)
            if x < 0:
                return Maybe.failure('must be non-negative')
            return Maybe.success(x)

        result = await Maybe.success(-5).bind_async(async_validator)

        assert result.is_failure()
        assert 'non-negative' in result.error_or('')

    @pytest.mark.asyncio
    async def it_chains_multiple_async_functions(self) -> None:
        """Chain multiple async functions together."""
        from valid8r.core.maybe import Maybe

        async def async_double(x: int) -> Maybe[int]:
            await asyncio.sleep(0.001)
            return Maybe.success(x * 2)

        async def async_add_ten(x: int) -> Maybe[int]:
            await asyncio.sleep(0.001)
            return Maybe.success(x + 10)

        # Chain async operations by awaiting each step
        result = await Maybe.success(5).bind_async(async_double)  # 10
        result = await result.bind_async(async_add_ten)  # 20

        assert result.value_or(None) == 20


class DescribeSchemaValidateAsync:
    """Tests for Schema.validate_async() method."""

    @pytest.mark.asyncio
    async def it_validates_with_async_validator(self) -> None:
        """Validate data with async validator."""
        from valid8r.core import (
            parsers,
            schema,
        )
        from valid8r.core.maybe import Maybe

        async def async_validator(val: str) -> Maybe[str]:
            await asyncio.sleep(0.001)
            if val == 'invalid':
                return Maybe.failure('Value is invalid')
            return Maybe.success(val)

        s = schema.Schema(
            fields={
                'field': schema.Field(parser=parsers.parse_str, validators=[async_validator], required=True),
            }
        )

        result = await s.validate_async({'field': 'valid'})

        assert result.is_success()
        assert result.value_or({})['field'] == 'valid'

    @pytest.mark.asyncio
    async def it_accumulates_async_validator_errors(self) -> None:
        """Accumulate errors from failing async validator."""
        from valid8r.core import (
            parsers,
            schema,
        )
        from valid8r.core.maybe import Maybe

        async def async_validator(_val: str) -> Maybe[str]:
            await asyncio.sleep(0.001)
            return Maybe.failure('async validation failed')

        s = schema.Schema(
            fields={
                'field': schema.Field(parser=parsers.parse_str, validators=[async_validator], required=True),
            }
        )

        result = await s.validate_async({'field': 'value'})

        assert result.is_failure()
        # Result contains list of ValidationErrors, check the validation_error list
        errors = result.validation_error
        assert isinstance(errors, list)
        assert len(errors) == 1
        assert 'async validation failed' in errors[0].message

    @pytest.mark.asyncio
    async def it_runs_sync_validators_before_async(self) -> None:
        """Run sync validators before async validators."""
        from valid8r.core import (
            parsers,
            schema,
            validators,
        )
        from valid8r.core.maybe import Maybe

        execution_order = []

        def sync_validator(val: str) -> Maybe[str]:
            execution_order.append('sync')
            return validators.length(3, 100)(val)

        async def async_validator(val: str) -> Maybe[str]:
            execution_order.append('async')
            await asyncio.sleep(0.001)
            return Maybe.success(val)

        s = schema.Schema(
            fields={
                'field': schema.Field(
                    parser=parsers.parse_str, validators=[sync_validator, async_validator], required=True
                ),
            }
        )

        await s.validate_async({'field': 'test'})

        assert execution_order == ['sync', 'async']

    @pytest.mark.asyncio
    async def it_skips_async_validators_if_sync_fails(self) -> None:
        """Skip async validators if sync validators fail."""
        from valid8r.core import (
            parsers,
            schema,
            validators,
        )
        from valid8r.core.maybe import Maybe

        async_called = False

        async def async_validator(val: str) -> Maybe[str]:
            nonlocal async_called
            async_called = True
            await asyncio.sleep(0.001)
            return Maybe.success(val)

        s = schema.Schema(
            fields={
                'field': schema.Field(
                    parser=parsers.parse_str,
                    validators=[validators.length(10, 100), async_validator],  # Sync will fail
                    required=True,
                ),
            }
        )

        result = await s.validate_async({'field': 'short'})

        assert result.is_failure()
        assert not async_called  # Async validator should not run

    @pytest.mark.asyncio
    async def it_runs_async_validators_concurrently(self) -> None:
        """Run async validators for multiple fields concurrently."""
        from valid8r.core import (
            parsers,
            schema,
        )
        from valid8r.core.maybe import Maybe

        async def slow_validator(val: str) -> Maybe[str]:
            await asyncio.sleep(0.01)  # 10ms delay
            return Maybe.success(val)

        s = schema.Schema(
            fields={
                'field1': schema.Field(parser=parsers.parse_str, validators=[slow_validator], required=True),
                'field2': schema.Field(parser=parsers.parse_str, validators=[slow_validator], required=True),
                'field3': schema.Field(parser=parsers.parse_str, validators=[slow_validator], required=True),
            }
        )

        start_time = time.perf_counter()
        result = await s.validate_async({'field1': 'a', 'field2': 'b', 'field3': 'c'})
        elapsed = time.perf_counter() - start_time

        assert result.is_success()
        # If concurrent: ~10ms. If sequential: ~30ms. Allow margin for CI variability.
        assert elapsed < 0.025, f'Expected concurrent execution (~10ms) but took {elapsed * 1000:.1f}ms'

    @pytest.mark.asyncio
    async def it_respects_timeout_parameter(self) -> None:
        """Respect timeout parameter for async validation."""
        from valid8r.core import (
            parsers,
            schema,
        )
        from valid8r.core.maybe import Maybe

        async def slow_validator(val: str) -> Maybe[str]:
            await asyncio.sleep(2.0)  # 2 seconds
            return Maybe.success(val)

        s = schema.Schema(
            fields={
                'field': schema.Field(parser=parsers.parse_str, validators=[slow_validator], required=True),
            }
        )

        with pytest.raises(asyncio.TimeoutError):
            await s.validate_async({'field': 'value'}, timeout=0.1)

    @pytest.mark.asyncio
    async def it_maintains_backward_compatibility_for_sync_only(self) -> None:
        """Maintain backward compatibility when using only sync validators."""
        from valid8r.core import (
            parsers,
            schema,
            validators,
        )

        s = schema.Schema(
            fields={
                'age': schema.Field(
                    parser=parsers.parse_int,
                    validators=[validators.minimum(0), validators.maximum(120)],
                    required=True,
                ),
            }
        )

        # Synchronous validate() should still work
        sync_result = s.validate({'age': '25'})
        assert sync_result.is_success()
        assert sync_result.value_or({})['age'] == 25

        # Async validate() should also work
        async_result = await s.validate_async({'age': '30'})
        assert async_result.is_success()
        assert async_result.value_or({})['age'] == 30

    @pytest.mark.asyncio
    async def it_handles_exceptions_in_async_validators(self) -> None:
        """Handle exceptions raised in async validators."""
        from valid8r.core import (
            parsers,
            schema,
        )

        async def failing_validator(_val: str) -> Maybe[str]:
            await asyncio.sleep(0.001)
            raise ValueError('Unexpected error in validator')

        s = schema.Schema(
            fields={
                'field': schema.Field(parser=parsers.parse_str, validators=[failing_validator], required=True),
            }
        )

        result = await s.validate_async({'field': 'value'})

        # Exception should be caught and converted to Failure
        assert result.is_failure()
        errors = result.validation_error
        assert isinstance(errors, list)
        assert len(errors) == 1
        assert 'Unexpected error' in errors[0].message

    @pytest.mark.asyncio
    async def it_validates_multiple_fields_with_mixed_validators(self) -> None:
        """Validate multiple fields with mix of sync and async validators."""
        from valid8r.core import (
            parsers,
            schema,
            validators,
        )
        from valid8r.core.maybe import Maybe

        async def async_unique_email(email_addr: EmailAddress) -> Maybe[EmailAddress]:
            await asyncio.sleep(0.001)
            # Mock uniqueness check
            email_str = f'{email_addr.local}@{email_addr.domain}'
            if email_str == 'existing@example.com':
                return Maybe.failure('Email already registered')
            return Maybe.success(email_addr)

        s = schema.Schema(
            fields={
                'username': schema.Field(
                    parser=parsers.parse_str,
                    validators=[validators.length(3, 100)],
                    required=True,
                ),
                'email': schema.Field(
                    parser=parsers.parse_email,
                    validators=[async_unique_email],
                    required=True,
                ),
                'age': schema.Field(
                    parser=parsers.parse_int,
                    validators=[validators.minimum(0)],
                    required=True,
                ),
            }
        )

        result = await s.validate_async(
            {
                'username': 'alice',
                'email': 'alice@example.com',
                'age': '25',
            }
        )

        assert result.is_success()
        data = result.value_or({})
        assert data['username'] == 'alice'
        assert data['email'].local == 'alice'
        assert data['age'] == 25

    @pytest.mark.asyncio
    async def it_detects_async_validators_automatically(self) -> None:
        """Automatically detect async validators without explicit registration."""
        from valid8r.core import (
            parsers,
            schema,
        )
        from valid8r.core.maybe import Maybe

        # No explicit marking needed - just define as async
        async def async_validator(val: str) -> Maybe[str]:
            await asyncio.sleep(0.001)
            return Maybe.success(val.upper())

        s = schema.Schema(
            fields={
                'field': schema.Field(parser=parsers.parse_str, validators=[async_validator], required=True),
            }
        )

        result = await s.validate_async({'field': 'hello'})

        assert result.is_success()
        assert result.value_or({})['field'] == 'HELLO'
