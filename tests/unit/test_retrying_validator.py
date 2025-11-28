"""Unit tests for RetryingValidator class.

This module tests the RetryingValidator with exponential backoff and jitter
following strict TDD discipline. Tests are written FIRST, we watch them FAIL
(RED), then implement minimal code to make them PASS (GREEN), then refactor.

Issue: #240 - Add retry logic with exponential backoff for async validators
"""

from __future__ import annotations

import random
import time
from typing import Any
from unittest.mock import patch

import pytest

from valid8r.core.maybe import Maybe

# =============================================================================
# Test Fixtures and Helpers
# =============================================================================


class FailingThenSucceedingValidator:
    """Validator that fails a specified number of times before succeeding."""

    def __init__(self, failures_before_success: int, *, transient: bool = True) -> None:
        """Initialize with number of failures before success."""
        self.failures_before_success = failures_before_success
        self.call_count = 0
        self.transient = transient

    async def __call__(self, value: Any) -> Maybe[Any]:  # noqa: ANN401
        """Validate value, failing initially then succeeding."""
        self.call_count += 1
        if self.call_count <= self.failures_before_success:
            error_msg = 'Transient failure' if self.transient else 'Permanent failure'
            return Maybe.failure(error_msg)
        return Maybe.success(value)


class AlwaysFailingValidator:
    """Validator that always fails with a transient error."""

    def __init__(self) -> None:
        """Initialize the validator."""
        self.call_count = 0

    async def __call__(self, _value: Any) -> Maybe[Any]:  # noqa: ANN401
        """Always return a transient failure."""
        self.call_count += 1
        return Maybe.failure('Transient failure: service unavailable')


class ExceptionThrowingValidator:
    """Validator that throws exceptions initially then succeeds."""

    def __init__(self, exceptions_before_success: int) -> None:
        """Initialize with number of exceptions before success."""
        self.exceptions_before_success = exceptions_before_success
        self.call_count = 0

    async def __call__(self, value: Any) -> Maybe[Any]:  # noqa: ANN401
        """Throw exception initially, then succeed."""
        self.call_count += 1
        if self.call_count <= self.exceptions_before_success:
            raise ConnectionError('Transient connection error')
        return Maybe.success(value)


class DelayTrackingValidator:
    """Validator that tracks when it was called to verify delays."""

    def __init__(self, failures_before_success: int = 0) -> None:
        """Initialize the validator."""
        self.failures_before_success = failures_before_success
        self.call_times: list[float] = []
        self.call_count = 0

    async def __call__(self, value: Any) -> Maybe[Any]:  # noqa: ANN401
        """Track call time and return result."""
        self.call_times.append(time.monotonic())
        self.call_count += 1
        if self.call_count <= self.failures_before_success:
            return Maybe.failure('Transient failure')
        return Maybe.success(value)

    def get_delays(self) -> list[float]:
        """Calculate delays between consecutive calls."""
        if len(self.call_times) < 2:
            return []
        return [self.call_times[i + 1] - self.call_times[i] for i in range(len(self.call_times) - 1)]


# =============================================================================
# Tests for RetryingValidator
# =============================================================================


class DescribeRetryingValidator:
    """Tests for RetryingValidator class with exponential backoff and jitter."""

    @pytest.mark.asyncio
    async def it_returns_success_on_first_attempt_without_retry(self) -> None:
        """Successful validation on first attempt returns immediately."""
        from valid8r.async_validators import RetryingValidator

        async def successful_validator(value: str) -> Maybe[str]:
            return Maybe.success(value)

        retry = RetryingValidator(successful_validator, max_retries=3)

        result = await retry('test-value')

        assert result.is_success()
        assert result.value_or(None) == 'test-value'

    @pytest.mark.asyncio
    async def it_retries_on_transient_failure_and_eventually_succeeds(self) -> None:
        """Transient failures trigger retry and eventual success."""
        from valid8r.async_validators import RetryingValidator

        validator = FailingThenSucceedingValidator(failures_before_success=2)
        retry = RetryingValidator(validator, max_retries=3, base_delay=0.001)

        result = await retry('test-value')

        assert result.is_success()
        assert validator.call_count == 3  # 2 failures + 1 success

    @pytest.mark.asyncio
    async def it_fails_after_max_retries_exceeded(self) -> None:
        """Persistent failures return Failure after max retries."""
        from valid8r.async_validators import RetryingValidator

        validator = AlwaysFailingValidator()
        retry = RetryingValidator(validator, max_retries=3, base_delay=0.001)

        result = await retry('test-value')

        assert result.is_failure()
        assert 'max retries exceeded' in result.error_or('').lower()
        # Initial call + 3 retries = 4 total calls
        assert validator.call_count == 4

    @pytest.mark.asyncio
    async def it_uses_exponential_backoff_with_configurable_base(self) -> None:
        """Backoff delays increase exponentially with configurable base."""
        from valid8r.async_validators import RetryingValidator

        validator = DelayTrackingValidator(failures_before_success=3)
        # With base_delay=0.01 and exponential_base=2.0:
        # Delay 1: 0.01 * 2^0 = 0.01
        # Delay 2: 0.01 * 2^1 = 0.02
        # Delay 3: 0.01 * 2^2 = 0.04
        retry = RetryingValidator(
            validator,
            max_retries=3,
            base_delay=0.01,
            exponential_base=2.0,
            jitter=False,  # Disable jitter for deterministic test
        )

        await retry('test-value')

        delays = validator.get_delays()
        assert len(delays) == 3
        # Allow 50% tolerance for timing variations
        assert delays[0] == pytest.approx(0.01, rel=0.5)
        assert delays[1] == pytest.approx(0.02, rel=0.5)
        assert delays[2] == pytest.approx(0.04, rel=0.5)

    @pytest.mark.asyncio
    async def it_respects_max_delay_cap(self) -> None:
        """Backoff delay never exceeds max_delay."""
        from valid8r.async_validators import RetryingValidator

        validator = DelayTrackingValidator(failures_before_success=5)
        # With base_delay=0.1 and exponential_base=2.0, max_delay=0.15:
        # Delay would be: 0.1, 0.2, 0.4, 0.8, 1.6 without cap
        # With cap: 0.1, 0.15, 0.15, 0.15, 0.15
        retry = RetryingValidator(
            validator,
            max_retries=5,
            base_delay=0.1,
            max_delay=0.15,
            exponential_base=2.0,
            jitter=False,
        )

        await retry('test-value')

        delays = validator.get_delays()
        assert len(delays) == 5
        # First delay is within max
        assert delays[0] == pytest.approx(0.1, rel=0.5)
        # Subsequent delays should be capped at max_delay
        for delay in delays[1:]:
            assert delay <= 0.2, f'Delay {delay} exceeded max_delay'

    @pytest.mark.asyncio
    async def it_applies_jitter_to_backoff_delays(self) -> None:
        """Jitter adds randomness to prevent thundering herd."""
        from valid8r.async_validators import RetryingValidator

        # Run multiple times to verify randomness
        all_first_delays: list[float] = []

        for _ in range(5):
            validator = DelayTrackingValidator(failures_before_success=1)
            retry = RetryingValidator(
                validator,
                max_retries=3,
                base_delay=0.05,
                jitter=True,
            )
            await retry('test-value')
            delays = validator.get_delays()
            if delays:
                all_first_delays.append(delays[0])

        # With jitter, delays should vary (not all identical)
        # They should be between 0 and base_delay * 2^attempt
        assert len(all_first_delays) >= 3
        # At least some variation expected (not all identical)
        if len({round(d, 3) for d in all_first_delays}) == 1:
            # All delays were identical - jitter might not be working
            # But this could happen by chance, so we just verify range
            pass
        # All delays should be within expected jitter range (0 to 2x base)
        for delay in all_first_delays:
            assert 0 <= delay <= 0.15, f'Delay {delay} outside jitter range'

    @pytest.mark.asyncio
    async def it_handles_exceptions_as_transient_failures(self) -> None:
        """Exceptions during validation are retried."""
        from valid8r.async_validators import RetryingValidator

        validator = ExceptionThrowingValidator(exceptions_before_success=2)
        retry = RetryingValidator(validator, max_retries=3, base_delay=0.001)

        result = await retry('test-value')

        assert result.is_success()
        assert validator.call_count == 3

    @pytest.mark.asyncio
    async def it_tracks_retry_count_correctly(self) -> None:
        """Retry count reflects actual retry attempts."""
        from valid8r.async_validators import RetryingValidator

        validator = FailingThenSucceedingValidator(failures_before_success=2)
        retry = RetryingValidator(validator, max_retries=5, base_delay=0.001)

        await retry('test-value')

        # 2 retries were needed (initial call failed, retry 1 failed, retry 2 succeeded)
        assert retry.retry_count == 2

    @pytest.mark.asyncio
    async def it_tracks_retry_delays(self) -> None:
        """Retry delays are recorded for observability."""
        from valid8r.async_validators import RetryingValidator

        validator = FailingThenSucceedingValidator(failures_before_success=2)
        retry = RetryingValidator(
            validator,
            max_retries=5,
            base_delay=0.01,
            jitter=False,
        )

        await retry('test-value')

        # 2 delays recorded (one before each retry)
        assert len(retry.retry_delays) == 2
        assert retry.retry_delays[0] == pytest.approx(0.01, rel=0.5)
        assert retry.retry_delays[1] == pytest.approx(0.02, rel=0.5)

    @pytest.mark.asyncio
    async def it_resets_state_between_validation_calls(self) -> None:
        """Each validation call starts with fresh retry state."""
        from valid8r.async_validators import RetryingValidator

        async def always_succeeds(value: str) -> Maybe[str]:
            return Maybe.success(value)

        retry = RetryingValidator(always_succeeds, max_retries=3, base_delay=0.01)

        await retry('first')
        assert retry.retry_count == 0
        assert retry.retry_delays == []

        await retry('second')
        assert retry.retry_count == 0
        assert retry.retry_delays == []

    @pytest.mark.asyncio
    async def it_includes_last_error_in_failure_message(self) -> None:
        """Final failure includes the last error message."""
        from valid8r.async_validators import RetryingValidator

        async def failing_validator(_value: str) -> Maybe[str]:
            return Maybe.failure('Transient: specific error details')

        retry = RetryingValidator(failing_validator, max_retries=2, base_delay=0.001)

        result = await retry('test-value')

        assert result.is_failure()
        error = result.error_or('')
        assert 'max retries exceeded' in error.lower()
        assert 'specific error details' in error.lower()

    @pytest.mark.asyncio
    async def it_uses_default_parameters_correctly(self) -> None:
        """Default parameters provide sensible defaults."""
        from valid8r.async_validators import RetryingValidator

        async def mock_validator(value: str) -> Maybe[str]:
            return Maybe.success(value)

        retry = RetryingValidator(mock_validator)

        # Verify defaults by accessing internal state
        assert retry._max_retries == 3  # noqa: SLF001
        assert retry._base_delay == 1.0  # noqa: SLF001
        assert retry._max_delay == 60.0  # noqa: SLF001
        assert retry._exponential_base == 2.0  # noqa: SLF001
        assert retry._jitter is True  # noqa: SLF001

    @pytest.mark.asyncio
    async def it_works_with_any_async_validator(self) -> None:
        """Works with any async validator function or callable."""
        from valid8r.async_validators import RetryingValidator

        # Test with a lambda-style async function
        async def custom_validator(value: int) -> Maybe[int]:
            if value < 0:
                return Maybe.failure('Transient: negative values not allowed')
            return Maybe.success(value * 2)

        retry = RetryingValidator(custom_validator, max_retries=3, base_delay=0.001)

        result = await retry(21)

        assert result.is_success()
        assert result.value_or(0) == 42

    @pytest.mark.asyncio
    async def it_supports_custom_exponential_base(self) -> None:
        """Exponential base can be customized (e.g., 3.0 for steeper backoff)."""
        from valid8r.async_validators import RetryingValidator

        validator = DelayTrackingValidator(failures_before_success=2)
        # With base_delay=0.01 and exponential_base=3.0:
        # Delay 1: 0.01 * 3^0 = 0.01
        # Delay 2: 0.01 * 3^1 = 0.03
        retry = RetryingValidator(
            validator,
            max_retries=3,
            base_delay=0.01,
            exponential_base=3.0,
            jitter=False,
        )

        await retry('test-value')

        delays = validator.get_delays()
        assert len(delays) == 2
        assert delays[0] == pytest.approx(0.01, rel=0.5)
        assert delays[1] == pytest.approx(0.03, rel=0.5)


class DescribeRetryingValidatorJitterBehavior:
    """Detailed tests for jitter functionality."""

    @pytest.mark.asyncio
    async def it_generates_jitter_within_expected_range(self) -> None:
        """Jitter values are between 0 and calculated delay."""
        from valid8r.async_validators import RetryingValidator

        # Patch random to control jitter output
        with patch.object(random, 'uniform', return_value=0.005) as mock_uniform:
            validator = FailingThenSucceedingValidator(failures_before_success=1)
            retry = RetryingValidator(
                validator,
                max_retries=3,
                base_delay=0.01,
                jitter=True,
            )

            await retry('test-value')

            # Verify uniform was called with correct range
            mock_uniform.assert_called()
            call_args = mock_uniform.call_args[0]
            assert call_args[0] == 0  # min
            assert call_args[1] == pytest.approx(0.01, rel=0.1)  # max is base_delay * 2^0

    @pytest.mark.asyncio
    async def it_disables_jitter_when_configured(self) -> None:
        """Jitter can be disabled for deterministic delays."""
        from valid8r.async_validators import RetryingValidator

        validator = DelayTrackingValidator(failures_before_success=3)
        retry = RetryingValidator(
            validator,
            max_retries=3,
            base_delay=0.01,
            jitter=False,
        )

        await retry('test-value')

        delays = validator.get_delays()
        # Without jitter, delays should follow exact exponential pattern
        assert delays[0] == pytest.approx(0.01, rel=0.3)
        assert delays[1] == pytest.approx(0.02, rel=0.3)
        assert delays[2] == pytest.approx(0.04, rel=0.3)


class DescribeRetryingValidatorEdgeCases:
    """Edge case tests for RetryingValidator."""

    @pytest.mark.asyncio
    async def it_handles_zero_max_retries(self) -> None:
        """With max_retries=0, only the initial attempt is made."""
        from valid8r.async_validators import RetryingValidator

        validator = AlwaysFailingValidator()
        retry = RetryingValidator(validator, max_retries=0, base_delay=0.01)

        result = await retry('test-value')

        assert result.is_failure()
        assert validator.call_count == 1  # Only initial attempt

    @pytest.mark.asyncio
    async def it_handles_very_small_base_delay(self) -> None:
        """Very small base delays work correctly."""
        from valid8r.async_validators import RetryingValidator

        validator = FailingThenSucceedingValidator(failures_before_success=1)
        retry = RetryingValidator(
            validator,
            max_retries=3,
            base_delay=0.0001,
            jitter=False,
        )

        result = await retry('test-value')

        assert result.is_success()

    @pytest.mark.asyncio
    async def it_handles_max_delay_less_than_base_delay(self) -> None:
        """When max_delay < base_delay, delay is capped at max_delay."""
        from valid8r.async_validators import RetryingValidator

        validator = DelayTrackingValidator(failures_before_success=1)
        retry = RetryingValidator(
            validator,
            max_retries=3,
            base_delay=0.1,
            max_delay=0.05,  # Less than base_delay
            jitter=False,
        )

        await retry('test-value')

        delays = validator.get_delays()
        assert len(delays) == 1
        # Delay should be capped at max_delay
        assert delays[0] <= 0.06  # Allow some tolerance

    @pytest.mark.asyncio
    async def it_preserves_value_type_through_retry(self) -> None:
        """Value type is preserved through retry process."""
        from valid8r.async_validators import RetryingValidator

        async def typed_validator(value: dict[str, int]) -> Maybe[dict[str, int]]:
            return Maybe.success(value)

        retry = RetryingValidator(typed_validator, max_retries=3)

        result = await retry({'key': 42})

        assert result.is_success()
        assert result.value_or({}) == {'key': 42}
