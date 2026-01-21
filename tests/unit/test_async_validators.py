"""Unit tests for async validators.

This module tests the async validator library following strict TDD discipline.
Tests are written FIRST, we watch them FAIL (RED), then implement minimal code
to make them PASS (GREEN), then refactor while keeping tests GREEN.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

import pytest

from valid8r.async_validators import (
    RateLimitedValidator,
    RetryValidator,
    compose_parallel,
    exists_in_db,
    parallel_validate,
    sequential_validate,
    unique_in_db,
    valid_api_key,
    valid_email_deliverable,
    valid_oauth_token,
)
from valid8r.core.maybe import Maybe

# =============================================================================
# Mock Objects for Testing
# =============================================================================


class MockAsyncConnection:
    """Mock async database connection for testing."""

    def __init__(self, *, raise_error: bool = False) -> None:
        """Initialize the mock connection."""
        self.data: dict[str, dict[str, set[Any]]] = {}
        self.query_count = 0
        self._raise_error = raise_error

    async def execute(self, query: str, *args: Any) -> MockQueryResult:  # noqa: ANN401
        """Execute a query."""
        await asyncio.sleep(0.001)  # Simulate I/O
        self.query_count += 1

        if self._raise_error:
            raise ConnectionError('Database connection failed')

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


class MockAPIVerifier:
    """Mock API verifier for testing valid_api_key and valid_oauth_token."""

    def __init__(
        self,
        *,
        valid_keys: set[str] | None = None,
        delay: float = 0.0,
        raise_timeout: bool = False,
        raise_error: bool = False,
    ) -> None:
        """Initialize mock verifier."""
        self._valid_keys = valid_keys or set()
        self._delay = delay
        self._raise_timeout = raise_timeout
        self._raise_error = raise_error
        self.call_count = 0

    async def verify_key(self, key: str) -> bool:
        """Verify an API key or token."""
        self.call_count += 1

        if self._raise_timeout:
            await asyncio.sleep(10)  # Will trigger timeout
            return False

        if self._raise_error:
            raise ConnectionError('Connection failed')

        if self._delay > 0:
            await asyncio.sleep(self._delay)

        return key in self._valid_keys


class MockAsyncCache:
    """Mock async cache for testing."""

    def __init__(self) -> None:
        """Initialize the mock cache."""
        self._cache: dict[str, Any] = {}
        self.get_count = 0
        self.set_count = 0

    async def get(self, key: str) -> Any | None:  # noqa: ANN401
        """Get value from cache."""
        self.get_count += 1
        return self._cache.get(key)

    async def set(self, key: str, value: Any) -> None:  # noqa: ANN401
        """Set value in cache."""
        self.set_count += 1
        self._cache[key] = value

    def prefill(self, key: str, value: Any) -> None:  # noqa: ANN401
        """Prefill the cache for testing."""
        self._cache[key] = value


class MockDNSResolver:
    """Mock DNS resolver for testing email deliverability."""

    def __init__(
        self,
        *,
        mx_records: dict[str, list[str]] | None = None,
        raise_error: bool = False,
        raise_nxdomain: bool = False,
    ) -> None:
        """Initialize mock resolver."""
        self._mx_records = mx_records or {}
        self._raise_error = raise_error
        self._raise_nxdomain = raise_nxdomain
        self.resolve_count = 0

    async def resolve_mx(self, domain: str) -> list[str]:
        """Resolve MX records for a domain."""
        self.resolve_count += 1

        if self._raise_error:
            raise ValueError('DNS resolution failed')

        if self._raise_nxdomain:
            raise ValueError('NXDOMAIN - domain does not exist')

        return self._mx_records.get(domain, [])


@dataclass
class MockEmailAddress:
    """Mock EmailAddress object for testing."""

    local: str
    domain: str

    def __str__(self) -> str:
        """Return email as string."""
        return f'{self.local}@{self.domain}'


# =============================================================================
# Tests for unique_in_db
# =============================================================================


class DescribeUniqueInDb:
    """Tests for unique_in_db validator."""

    @pytest.fixture
    def db_connection(self) -> MockAsyncConnection:
        """Create a mock database connection."""
        return MockAsyncConnection()

    @pytest.mark.asyncio
    async def it_validates_unique_value_in_database(self, db_connection: MockAsyncConnection) -> None:
        """Unique value returns Success with the value."""
        db_connection.add_record('users', 'email', 'existing@example.com')
        validator = await unique_in_db(field='email', table='users', connection=db_connection)

        result = await validator('new@example.com')

        assert result.is_success()
        assert result.value_or(None) == 'new@example.com'

    @pytest.mark.asyncio
    async def it_rejects_non_unique_value_in_database(self, db_connection: MockAsyncConnection) -> None:
        """Non-unique value returns Failure with descriptive error."""
        db_connection.add_record('users', 'email', 'existing@example.com')
        validator = await unique_in_db(field='email', table='users', connection=db_connection)

        result = await validator('existing@example.com')

        assert result.is_failure()
        assert 'already exists' in result.error_or('').lower()

    @pytest.mark.asyncio
    async def it_handles_database_errors_gracefully(self) -> None:
        """Database errors return Failure without raising exception."""
        db_connection = MockAsyncConnection(raise_error=True)
        validator = await unique_in_db(field='email', table='users', connection=db_connection)

        result = await validator('test@example.com')

        assert result.is_failure()
        assert 'database error' in result.error_or('').lower()


# =============================================================================
# Tests for exists_in_db
# =============================================================================


class DescribeExistsInDb:
    """Tests for exists_in_db validator."""

    @pytest.fixture
    def db_connection(self) -> MockAsyncConnection:
        """Create a mock database connection."""
        return MockAsyncConnection()

    @pytest.mark.asyncio
    async def it_validates_existing_value_in_database(self, db_connection: MockAsyncConnection) -> None:
        """Existing value returns Success with the value."""
        db_connection.add_record('categories', 'id', '42')
        validator = await exists_in_db(field='id', table='categories', connection=db_connection)

        result = await validator('42')

        assert result.is_success()
        assert result.value_or(None) == '42'

    @pytest.mark.asyncio
    async def it_rejects_missing_value_in_database(self, db_connection: MockAsyncConnection) -> None:
        """Missing value returns Failure with descriptive error."""
        db_connection.add_record('categories', 'id', '42')
        validator = await exists_in_db(field='id', table='categories', connection=db_connection)

        result = await validator('999')

        assert result.is_failure()
        assert 'does not exist' in result.error_or('').lower()

    @pytest.mark.asyncio
    async def it_handles_database_errors_gracefully(self) -> None:
        """Database errors return Failure without raising exception."""
        db_connection = MockAsyncConnection(raise_error=True)
        validator = await exists_in_db(field='id', table='categories', connection=db_connection)

        result = await validator('42')

        assert result.is_failure()
        assert 'database error' in result.error_or('').lower()


# =============================================================================
# Tests for valid_api_key
# =============================================================================


class DescribeValidApiKey:
    """Tests for valid_api_key validator factory."""

    @pytest.mark.asyncio
    async def it_validates_valid_api_key(self) -> None:
        """Valid API key returns Success."""
        verifier = MockAPIVerifier(valid_keys={'valid-key-123'})
        validator = await valid_api_key(
            api_url='https://api.example.com/validate',
            verifier=verifier,
        )

        result = await validator('valid-key-123')

        assert result.is_success()
        assert result.value_or(None) == 'valid-key-123'
        assert verifier.call_count == 1

    @pytest.mark.asyncio
    async def it_rejects_invalid_api_key(self) -> None:
        """Invalid API key returns Failure with clear error message."""
        verifier = MockAPIVerifier(valid_keys={'valid-key-123'})
        validator = await valid_api_key(
            api_url='https://api.example.com/validate',
            verifier=verifier,
        )

        result = await validator('invalid-key')

        assert result.is_failure()
        assert 'invalid api key' in result.error_or('').lower()

    @pytest.mark.asyncio
    async def it_handles_timeout_errors(self) -> None:
        """Timeout returns Failure with timeout message."""
        verifier = MockAPIVerifier(raise_timeout=True)
        validator = await valid_api_key(
            api_url='https://api.example.com/validate',
            verifier=verifier,
            timeout=0.01,  # Very short timeout
        )

        result = await validator('any-key')

        assert result.is_failure()
        assert 'timeout' in result.error_or('').lower()

    @pytest.mark.asyncio
    async def it_uses_cache_for_valid_keys(self) -> None:
        """Valid keys are cached to avoid redundant API calls."""
        verifier = MockAPIVerifier(valid_keys={'cached-key'})
        cache = MockAsyncCache()
        validator = await valid_api_key(
            api_url='https://api.example.com/validate',
            verifier=verifier,
            cache=cache,
        )

        # First call - hits API
        result1 = await validator('cached-key')
        assert result1.is_success()
        assert verifier.call_count == 1
        assert cache.set_count == 1

        # Second call - should use cache
        result2 = await validator('cached-key')
        assert result2.is_success()
        # Verifier should NOT be called again due to cache hit
        assert verifier.call_count == 1  # Still 1
        assert cache.get_count == 2

    @pytest.mark.asyncio
    async def it_returns_cached_result_without_api_call(self) -> None:
        """Prefilled cache returns Success without calling API."""
        verifier = MockAPIVerifier()
        cache = MockAsyncCache()
        cache.prefill('api_key_prefilled-key', True)

        validator = await valid_api_key(
            api_url='https://api.example.com/validate',
            verifier=verifier,
            cache=cache,
        )

        result = await validator('prefilled-key')

        assert result.is_success()
        assert verifier.call_count == 0  # API never called


# =============================================================================
# Tests for valid_oauth_token
# =============================================================================


class DescribeValidOAuthToken:
    """Tests for valid_oauth_token validator factory."""

    @pytest.mark.asyncio
    async def it_validates_valid_oauth_token(self) -> None:
        """Valid OAuth token returns Success."""
        verifier = MockAPIVerifier(valid_keys={'valid-token-abc'})
        validator = await valid_oauth_token(
            token_endpoint='https://oauth.example.com/verify',  # noqa: S106
            verifier=verifier,
        )

        result = await validator('valid-token-abc')

        assert result.is_success()
        assert result.value_or(None) == 'valid-token-abc'

    @pytest.mark.asyncio
    async def it_rejects_invalid_oauth_token(self) -> None:
        """Invalid OAuth token returns Failure."""
        verifier = MockAPIVerifier(valid_keys={'valid-token'})
        validator = await valid_oauth_token(
            token_endpoint='https://oauth.example.com/verify',  # noqa: S106
            verifier=verifier,
        )

        result = await validator('invalid-token')

        assert result.is_failure()
        assert 'invalid oauth token' in result.error_or('').lower()

    @pytest.mark.asyncio
    async def it_uses_cache_for_valid_tokens(self) -> None:
        """Valid tokens are cached to avoid redundant API calls."""
        verifier = MockAPIVerifier(valid_keys={'cached-token'})
        cache = MockAsyncCache()
        validator = await valid_oauth_token(
            token_endpoint='https://oauth.example.com/verify',  # noqa: S106
            verifier=verifier,
            cache=cache,
        )

        # First call - hits API
        result1 = await validator('cached-token')
        assert result1.is_success()
        assert verifier.call_count == 1
        assert cache.set_count == 1

        # Second call - should use cache
        result2 = await validator('cached-token')
        assert result2.is_success()
        assert verifier.call_count == 1  # Still 1 - cached

    @pytest.mark.asyncio
    async def it_returns_cached_result_without_api_call(self) -> None:
        """Prefilled cache returns Success without calling API."""
        verifier = MockAPIVerifier()
        cache = MockAsyncCache()
        cache.prefill('oauth_token_prefilled-token', True)

        validator = await valid_oauth_token(
            token_endpoint='https://oauth.example.com/verify',  # noqa: S106
            verifier=verifier,
            cache=cache,
        )

        result = await validator('prefilled-token')

        assert result.is_success()
        assert verifier.call_count == 0  # API never called


# =============================================================================
# Tests for valid_email_deliverable
# =============================================================================


class DescribeValidEmailDeliverable:
    """Tests for valid_email_deliverable validator."""

    @pytest.mark.asyncio
    async def it_validates_email_with_mx_records(self) -> None:
        """Email with valid MX records returns Success."""
        resolver = MockDNSResolver(mx_records={'example.com': ['mail.example.com']})
        validator = await valid_email_deliverable(resolver=resolver)

        result = await validator('user@example.com')

        assert result.is_success()
        assert result.value_or(None) == 'user@example.com'

    @pytest.mark.asyncio
    async def it_rejects_email_without_mx_records(self) -> None:
        """Email without MX records returns Failure."""
        resolver = MockDNSResolver(mx_records={})
        validator = await valid_email_deliverable(resolver=resolver)

        result = await validator('user@no-mx.example')

        assert result.is_failure()
        assert 'no mail server' in result.error_or('').lower()

    @pytest.mark.asyncio
    async def it_rejects_invalid_email_format(self) -> None:
        """Email without @ returns Failure."""
        resolver = MockDNSResolver()
        validator = await valid_email_deliverable(resolver=resolver)

        result = await validator('invalid-email-no-at-sign')

        assert result.is_failure()
        assert 'invalid email format' in result.error_or('').lower()

    @pytest.mark.asyncio
    async def it_handles_email_address_objects(self) -> None:
        """EmailAddress objects are properly validated."""
        resolver = MockDNSResolver(mx_records={'example.com': ['mx.example.com']})
        validator = await valid_email_deliverable(resolver=resolver)
        email_obj = MockEmailAddress(local='user', domain='example.com')

        result = await validator(email_obj)

        assert result.is_success()
        # Returns the original EmailAddress object
        assert result.value_or(None) is email_obj

    @pytest.mark.asyncio
    async def it_handles_dns_errors_gracefully(self) -> None:
        """DNS errors return Failure without raising exception."""
        resolver = MockDNSResolver(raise_error=True)
        validator = await valid_email_deliverable(resolver=resolver)

        result = await validator('user@error.example')

        assert result.is_failure()

    @pytest.mark.asyncio
    async def it_handles_nxdomain_errors(self) -> None:
        """NXDOMAIN errors indicate non-existent domain."""
        resolver = MockDNSResolver(raise_nxdomain=True)
        validator = await valid_email_deliverable(resolver=resolver)

        result = await validator('user@nonexistent.example')

        assert result.is_failure()
        assert 'does not exist' in result.error_or('').lower()


# =============================================================================
# Tests for RateLimitedValidator
# =============================================================================


class DescribeRateLimitedValidator:
    """Tests for RateLimitedValidator class."""

    @pytest.mark.asyncio
    async def it_passes_through_validation_result(self) -> None:
        """Validator result is returned correctly."""

        async def mock_validator(value: str) -> Maybe[str]:
            return Maybe.success(value)

        rate_limited = RateLimitedValidator(mock_validator, rate=10)

        result = await rate_limited('test-value')

        assert result.is_success()
        assert result.value_or(None) == 'test-value'

    @pytest.mark.asyncio
    async def it_propagates_failure_results(self) -> None:
        """Failure results pass through rate limiter."""

        async def failing_validator(_value: str) -> Maybe[str]:
            return Maybe.failure('Validation failed')

        rate_limited = RateLimitedValidator(failing_validator, rate=10)

        result = await rate_limited('test-value')

        assert result.is_failure()
        assert 'validation failed' in result.error_or('').lower()

    @pytest.mark.asyncio
    async def it_allows_burst_of_requests(self) -> None:
        """Initial burst up to burst limit is allowed without delay."""
        import time

        call_times: list[float] = []

        async def tracking_validator(value: str) -> Maybe[str]:
            call_times.append(time.monotonic())
            return Maybe.success(value)

        rate_limited = RateLimitedValidator(tracking_validator, rate=10, burst=5)

        # Make 5 rapid calls (within burst limit)
        start = time.monotonic()
        for i in range(5):
            await rate_limited(f'value-{i}')

        elapsed = time.monotonic() - start
        # Should complete quickly without rate limiting delays
        assert elapsed < 0.5
        assert len(call_times) == 5

    @pytest.mark.asyncio
    async def it_uses_default_burst_equal_to_rate(self) -> None:
        """Default burst equals rate when not specified."""

        async def mock_validator(value: str) -> Maybe[str]:
            return Maybe.success(value)

        rate_limited = RateLimitedValidator(mock_validator, rate=5)

        # Access private member to verify (for testing only)
        assert rate_limited._burst == 5  # noqa: SLF001


# =============================================================================
# Tests for RetryValidator
# =============================================================================


class DescribeRetryValidator:
    """Tests for RetryValidator class."""

    @pytest.mark.asyncio
    async def it_returns_success_without_retry(self) -> None:
        """Successful validation on first attempt returns immediately."""

        async def successful_validator(value: str) -> Maybe[str]:
            return Maybe.success(value)

        retry = RetryValidator(successful_validator, max_retries=3)

        result = await retry('test')

        assert result.is_success()
        assert retry.retry_count == 0  # No retries needed

    @pytest.mark.asyncio
    async def it_does_not_retry_non_transient_failures(self) -> None:
        """Non-transient failures return immediately without retry."""

        async def failing_validator(_value: str) -> Maybe[str]:
            return Maybe.failure('Invalid format')

        retry = RetryValidator(failing_validator, max_retries=3)

        result = await retry('test')

        assert result.is_failure()
        assert retry.retry_count == 0  # No retries for non-transient

    @pytest.mark.asyncio
    async def it_retries_transient_failures(self) -> None:
        """Transient failures trigger retry logic."""
        call_count = 0

        async def eventually_succeeds(value: str) -> Maybe[str]:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return Maybe.failure('Transient error: try again')
            return Maybe.success(value)

        retry = RetryValidator(eventually_succeeds, max_retries=5, base_delay=0.01)

        result = await retry('test')

        assert result.is_success()
        assert call_count == 3

    @pytest.mark.asyncio
    async def it_fails_after_max_retries_exceeded(self) -> None:
        """Persistent transient failures return Failure after max retries."""

        async def always_transient(_value: str) -> Maybe[str]:
            return Maybe.failure('Transient error')

        retry = RetryValidator(always_transient, max_retries=2, base_delay=0.01)

        result = await retry('test')

        assert result.is_failure()
        assert 'max retries exceeded' in result.error_or('').lower()

    @pytest.mark.asyncio
    async def it_uses_exponential_backoff_by_default(self) -> None:
        """Exponential backoff doubles delay between retries."""
        call_count = 0

        async def always_transient(_value: str) -> Maybe[str]:
            nonlocal call_count
            call_count += 1
            return Maybe.failure('Transient error')

        retry = RetryValidator(always_transient, max_retries=2, base_delay=0.01, exponential=True)

        await retry('test')

        # With exponential=True, delays should be: 0.01, 0.02, 0.04
        # Check that delays follow exponential pattern
        assert len(retry.retry_delays) == 2
        assert retry.retry_delays[0] == pytest.approx(0.01, rel=0.1)
        assert retry.retry_delays[1] == pytest.approx(0.02, rel=0.1)

    @pytest.mark.asyncio
    async def it_supports_constant_delay_backoff(self) -> None:
        """Non-exponential backoff uses constant delay."""

        async def always_transient(_value: str) -> Maybe[str]:
            return Maybe.failure('Transient error')

        retry = RetryValidator(always_transient, max_retries=2, base_delay=0.01, exponential=False)

        await retry('test')

        # With exponential=False, all delays should be equal
        assert len(retry.retry_delays) == 2
        assert retry.retry_delays[0] == pytest.approx(0.01, rel=0.1)
        assert retry.retry_delays[1] == pytest.approx(0.01, rel=0.1)

    @pytest.mark.asyncio
    async def it_handles_validator_exceptions(self) -> None:
        """Exceptions during validation are caught and counted as retries."""
        call_count = 0

        async def throws_then_succeeds(value: str) -> Maybe[str]:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError('Network error')
            return Maybe.success(value)

        retry = RetryValidator(throws_then_succeeds, max_retries=3, base_delay=0.01)

        result = await retry('test')

        assert result.is_success()
        assert call_count == 2


# =============================================================================
# Tests for parallel_validate
# =============================================================================


class DescribeParallelValidate:
    """Tests for parallel_validate function."""

    @pytest.mark.asyncio
    async def it_validates_multiple_values_concurrently(self) -> None:
        """Multiple values are validated in parallel."""
        validated_values: list[str] = []

        async def tracking_validator(value: str) -> Maybe[str]:
            validated_values.append(value)
            await asyncio.sleep(0.01)
            return Maybe.success(value)

        values = ['a', 'b', 'c', 'd']
        results = await parallel_validate(tracking_validator, values)

        assert len(results) == 4
        assert all(r.is_success() for r in results)
        assert set(validated_values) == {'a', 'b', 'c', 'd'}

    @pytest.mark.asyncio
    async def it_preserves_order_of_results(self) -> None:
        """Results are returned in same order as input values."""

        async def echo_validator(value: int) -> Maybe[int]:
            await asyncio.sleep(0.01 * (5 - value))  # Later values complete faster
            return Maybe.success(value * 10)

        values = [1, 2, 3, 4]
        results = await parallel_validate(echo_validator, values)

        assert [r.value_or(0) for r in results] == [10, 20, 30, 40]

    @pytest.mark.asyncio
    async def it_returns_both_successes_and_failures(self) -> None:
        """Mixed results include both successes and failures."""

        async def even_only_validator(value: int) -> Maybe[int]:
            if value % 2 == 0:
                return Maybe.success(value)
            return Maybe.failure(f'{value} is odd')

        values = [1, 2, 3, 4, 5]
        results = await parallel_validate(even_only_validator, values)

        successes = [r for r in results if r.is_success()]
        failures = [r for r in results if r.is_failure()]

        assert len(successes) == 2
        assert len(failures) == 3
        assert [r.value_or(0) for r in successes] == [2, 4]

    @pytest.mark.asyncio
    async def it_handles_empty_input(self) -> None:
        """Empty input returns empty results list."""

        async def mock_validator(value: str) -> Maybe[str]:
            return Maybe.success(value)

        results = await parallel_validate(mock_validator, [])

        assert results == []


# =============================================================================
# Tests for sequential_validate
# =============================================================================


class DescribeSequentialValidate:
    """Tests for sequential_validate function."""

    @pytest.mark.asyncio
    async def it_runs_validators_in_order(self) -> None:
        """Validators are executed sequentially in order."""
        execution_order: list[str] = []

        async def validator_a(value: int) -> Maybe[int]:
            execution_order.append('a')
            return Maybe.success(value + 1)

        async def validator_b(value: int) -> Maybe[int]:
            execution_order.append('b')
            return Maybe.success(value * 2)

        async def validator_c(value: int) -> Maybe[int]:
            execution_order.append('c')
            return Maybe.success(value + 10)

        result = await sequential_validate([validator_a, validator_b, validator_c], 5)

        assert execution_order == ['a', 'b', 'c']
        # (5 + 1) * 2 + 10 = 22
        assert result.is_success()
        assert result.value_or(0) == 22

    @pytest.mark.asyncio
    async def it_stops_on_first_failure(self) -> None:
        """Chain stops executing when a validator fails."""
        execution_order: list[str] = []

        async def validator_pass(value: int) -> Maybe[int]:
            execution_order.append('pass')
            return Maybe.success(value)

        async def validator_fail(_value: int) -> Maybe[int]:
            execution_order.append('fail')
            return Maybe.failure('Validation failed')

        async def validator_never_called(value: int) -> Maybe[int]:
            execution_order.append('never')
            return Maybe.success(value)

        result = await sequential_validate(
            [validator_pass, validator_fail, validator_never_called],
            10,
        )

        assert execution_order == ['pass', 'fail']
        assert result.is_failure()
        assert 'validation failed' in result.error_or('').lower()

    @pytest.mark.asyncio
    async def it_returns_success_for_empty_validators(self) -> None:
        """Empty validator list returns Success with original value."""
        result = await sequential_validate([], 42)

        assert result.is_success()
        assert result.value_or(0) == 42

    @pytest.mark.asyncio
    async def it_passes_transformed_value_through_chain(self) -> None:
        """Each validator receives the output of the previous one."""

        async def add_prefix(value: str) -> Maybe[str]:
            return Maybe.success(f'prefix_{value}')

        async def add_suffix(value: str) -> Maybe[str]:
            return Maybe.success(f'{value}_suffix')

        result = await sequential_validate([add_prefix, add_suffix], 'test')

        assert result.is_success()
        assert result.value_or('') == 'prefix_test_suffix'


# =============================================================================
# Tests for compose_parallel
# =============================================================================


class DescribeComposeParallel:
    """Tests for compose_parallel function."""

    @pytest.mark.asyncio
    async def it_returns_success_when_all_pass(self) -> None:
        """All validators passing returns Success."""

        async def check_length(value: str) -> Maybe[str]:
            if len(value) >= 3:
                return Maybe.success(value)
            return Maybe.failure('Too short')

        async def check_alpha(value: str) -> Maybe[str]:
            if value.isalpha():
                return Maybe.success(value)
            return Maybe.failure('Not alphabetic')

        result = await compose_parallel([check_length, check_alpha], 'hello')

        assert result.is_success()
        assert result.value_or('') == 'hello'

    @pytest.mark.asyncio
    async def it_returns_first_failure(self) -> None:
        """First failure from any validator is returned."""

        async def always_pass(value: str) -> Maybe[str]:
            return Maybe.success(value)

        async def always_fail(_value: str) -> Maybe[str]:
            return Maybe.failure('Always fails')

        result = await compose_parallel([always_pass, always_fail], 'test')

        assert result.is_failure()
        assert 'always fails' in result.error_or('').lower()

    @pytest.mark.asyncio
    async def it_runs_validators_concurrently(self) -> None:
        """Validators execute in parallel for efficiency."""
        import time

        async def slow_validator(value: str) -> Maybe[str]:
            await asyncio.sleep(0.05)
            return Maybe.success(value)

        validators = [slow_validator, slow_validator, slow_validator]

        start = time.monotonic()
        result = await compose_parallel(validators, 'test')
        elapsed = time.monotonic() - start

        assert result.is_success()
        # If truly parallel, should take ~0.05s, not 0.15s
        assert elapsed < 0.1

    @pytest.mark.asyncio
    async def it_returns_success_for_empty_validators(self) -> None:
        """Empty validator list returns Success with original value."""
        result = await compose_parallel([], 'test')

        assert result.is_success()
        assert result.value_or('') == 'test'


# =============================================================================
# Additional Tests for Edge Cases and Coverage
# =============================================================================


class DescribeRateLimitedValidatorWaitBehavior:
    """Additional tests for RateLimitedValidator wait/delay behavior."""

    @pytest.mark.asyncio
    async def it_delays_when_tokens_exhausted(self) -> None:
        """Requests are delayed when token bucket is empty."""
        import time

        call_count = 0

        async def tracking_validator(value: str) -> Maybe[str]:
            nonlocal call_count
            call_count += 1
            return Maybe.success(value)

        # Rate of 2/sec, burst of 1 - after first request, must wait
        rate_limited = RateLimitedValidator(tracking_validator, rate=2, burst=1)

        start = time.monotonic()
        # First call uses the burst token
        await rate_limited('first')
        # Second call must wait for token replenishment
        await rate_limited('second')
        elapsed = time.monotonic() - start

        assert call_count == 2
        # Should have waited approximately 0.5 seconds for second call
        assert elapsed >= 0.4, f'Expected at least 0.4s delay, got {elapsed:.2f}s'

    @pytest.mark.asyncio
    async def it_replenishes_tokens_over_time(self) -> None:
        """Tokens are replenished based on elapsed time and rate."""

        async def mock_validator(value: str) -> Maybe[str]:
            return Maybe.success(value)

        # Rate of 10/sec, burst of 2
        rate_limited = RateLimitedValidator(mock_validator, rate=10, burst=2)

        # Use both burst tokens
        await rate_limited('first')
        await rate_limited('second')

        # Wait for tokens to replenish (100ms should give ~1 token at 10/sec)
        await asyncio.sleep(0.15)

        # Should now be able to make a call without significant delay
        import time

        start = time.monotonic()
        await rate_limited('third')
        elapsed = time.monotonic() - start

        # Should complete quickly since tokens replenished
        assert elapsed < 0.1


class DescribeValidApiKeyEdgeCases:
    """Edge case tests for valid_api_key."""

    @pytest.mark.asyncio
    async def it_handles_connection_errors(self) -> None:
        """Connection errors return Failure with network error message."""
        verifier = MockAPIVerifier(raise_error=True)
        validator = await valid_api_key(
            api_url='https://api.example.com/validate',
            verifier=verifier,
        )

        result = await validator('any-key')

        assert result.is_failure()
        # Should indicate some kind of error occurred
        error = result.error_or('')
        assert 'error' in error.lower()


class DescribeValidOAuthTokenEdgeCases:
    """Edge case tests for valid_oauth_token."""

    @pytest.mark.asyncio
    async def it_handles_connection_errors(self) -> None:
        """Connection errors return Failure."""
        verifier = MockAPIVerifier(raise_error=True)
        validator = await valid_oauth_token(
            token_endpoint='https://oauth.example.com/verify',  # noqa: S106
            verifier=verifier,
        )

        result = await validator('any-token')

        assert result.is_failure()


class DescribeRetryValidatorEdgeCases:
    """Edge case tests for RetryValidator."""

    @pytest.mark.asyncio
    async def it_tracks_retry_count_correctly(self) -> None:
        """Retry count is accurately tracked through all attempts."""
        call_count = 0

        async def counting_validator(value: str) -> Maybe[str]:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return Maybe.failure('Transient: retry')
            return Maybe.success(value)

        retry = RetryValidator(counting_validator, max_retries=5, base_delay=0.001)
        await retry('test')

        # 3 calls total: initial + 2 retries
        assert call_count == 3
        # retry_count tracks the actual retry attempts (not the initial call)
        assert retry.retry_count == 2

    @pytest.mark.asyncio
    async def it_resets_state_between_calls(self) -> None:
        """Each validation call starts with fresh retry state."""
        call_count = 0

        async def always_succeeds(value: str) -> Maybe[str]:
            nonlocal call_count
            call_count += 1
            return Maybe.success(value)

        retry = RetryValidator(always_succeeds, max_retries=3, base_delay=0.001)

        await retry('first')
        assert retry.retry_count == 0
        assert retry.retry_delays == []

        await retry('second')
        assert retry.retry_count == 0
        assert retry.retry_delays == []


class DescribeValidApiKeyGenericExceptionHandling:
    """Tests for generic exception handling in valid_api_key."""

    @pytest.mark.asyncio
    async def it_handles_generic_exceptions(self) -> None:
        """Generic exceptions are caught and return Failure."""

        class RaisingVerifier:
            """Verifier that raises a generic exception."""

            async def verify_key(self, _key: str) -> bool:
                raise ValueError('Something unexpected happened')

        verifier = RaisingVerifier()
        validator = await valid_api_key(
            api_url='https://api.example.com/validate',
            verifier=verifier,
        )

        result = await validator('any-key')

        assert result.is_failure()
        assert 'error' in result.error_or('').lower()


class DescribeValidOAuthTokenGenericExceptionHandling:
    """Tests for generic exception handling in valid_oauth_token."""

    @pytest.mark.asyncio
    async def it_handles_generic_exceptions(self) -> None:
        """Generic exceptions are caught and return Failure."""

        class RaisingVerifier:
            """Verifier that raises a generic exception."""

            async def verify_key(self, _key: str) -> bool:
                raise ValueError('Something unexpected happened')

        verifier = RaisingVerifier()
        validator = await valid_oauth_token(
            token_endpoint='https://oauth.example.com/verify',  # noqa: S106
            verifier=verifier,
        )

        result = await validator('any-token')

        assert result.is_failure()
        assert 'error' in result.error_or('').lower()


class DescribeValidEmailDeliverableGenericExceptionHandling:
    """Tests for generic exception handling in valid_email_deliverable."""

    @pytest.mark.asyncio
    async def it_handles_generic_exceptions(self) -> None:
        """Generic exceptions are caught and return Failure."""

        class RaisingResolver:
            """Resolver that raises a generic exception."""

            async def resolve_mx(self, _domain: str) -> list[str]:
                raise RuntimeError('DNS subsystem crashed')

        resolver = RaisingResolver()
        validator = await valid_email_deliverable(resolver=resolver)

        result = await validator('user@example.com')

        assert result.is_failure()
        assert 'failed' in result.error_or('').lower()


# =============================================================================
# Tests for Default Implementations (aiohttp/aiodns)
# =============================================================================


class DescribeValidApiKeyWithAiohttp:
    """Tests for valid_api_key using default aiohttp implementation."""

    @pytest.mark.asyncio
    async def it_validates_key_with_successful_http_response(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Valid API key returns Success when HTTP 200 is received."""
        import sys
        from unittest.mock import (
            AsyncMock,
            MagicMock,
        )

        # Create a mock response with status 200
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        # Create a mock session
        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        # Create mock aiohttp module
        mock_aiohttp = MagicMock()
        mock_aiohttp.ClientSession = MagicMock(return_value=mock_session)
        mock_aiohttp.ClientTimeout = MagicMock(return_value=MagicMock())

        # Inject mock into sys.modules
        monkeypatch.setitem(sys.modules, 'aiohttp', mock_aiohttp)

        validator = await valid_api_key(api_url='https://api.example.com/validate', timeout=5.0)

        result = await validator('test-key')

        assert result.is_success()
        assert result.value_or(None) == 'test-key'

    @pytest.mark.asyncio
    async def it_rejects_key_with_non_200_response(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Invalid API key returns Failure when non-200 is received."""
        import sys
        from unittest.mock import (
            AsyncMock,
            MagicMock,
        )

        # Create a mock response with status 401
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        # Create a mock session
        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        # Create mock aiohttp module
        mock_aiohttp = MagicMock()
        mock_aiohttp.ClientSession = MagicMock(return_value=mock_session)
        mock_aiohttp.ClientTimeout = MagicMock(return_value=MagicMock())

        monkeypatch.setitem(sys.modules, 'aiohttp', mock_aiohttp)

        validator = await valid_api_key(api_url='https://api.example.com/validate')

        result = await validator('invalid-key')

        assert result.is_failure()
        assert 'invalid api key' in result.error_or('').lower()

    @pytest.mark.asyncio
    async def it_returns_failure_when_aiohttp_not_available(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Returns Failure when aiohttp is not installed."""
        import builtins
        import sys

        # Remove aiohttp from sys.modules if present, and make import fail
        monkeypatch.delitem(sys.modules, 'aiohttp', raising=False)

        # Create a mock that raises ImportError when aiohttp is imported
        original_import = builtins.__import__

        def mock_import(name: str, *args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
            if name == 'aiohttp':
                raise ImportError('No module named aiohttp')
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, '__import__', mock_import)

        validator = await valid_api_key(api_url='https://api.example.com/validate')

        result = await validator('any-key')

        assert result.is_failure()
        assert 'aiohttp required' in result.error_or('').lower()

    @pytest.mark.asyncio
    async def it_caches_successful_http_validation(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Successful HTTP validation is cached."""
        import sys
        from unittest.mock import (
            AsyncMock,
            MagicMock,
        )

        # Create a mock response with status 200
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        # Create a mock session
        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        # Create mock aiohttp module
        mock_aiohttp = MagicMock()
        mock_aiohttp.ClientSession = MagicMock(return_value=mock_session)
        mock_aiohttp.ClientTimeout = MagicMock(return_value=MagicMock())

        monkeypatch.setitem(sys.modules, 'aiohttp', mock_aiohttp)

        cache = MockAsyncCache()
        validator = await valid_api_key(api_url='https://api.example.com/validate', cache=cache)

        result = await validator('cached-key')

        assert result.is_success()
        assert cache.set_count == 1
        assert 'api_key_cached-key' in cache._cache  # noqa: SLF001


class DescribeValidOAuthTokenWithAiohttp:
    """Tests for valid_oauth_token using default aiohttp implementation."""

    @pytest.mark.asyncio
    async def it_validates_token_with_successful_http_response(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Valid OAuth token returns Success when HTTP 200 is received."""
        import sys
        from unittest.mock import (
            AsyncMock,
            MagicMock,
        )

        # Create a mock response with status 200
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        # Create a mock session
        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        # Create mock aiohttp module
        mock_aiohttp = MagicMock()
        mock_aiohttp.ClientSession = MagicMock(return_value=mock_session)

        monkeypatch.setitem(sys.modules, 'aiohttp', mock_aiohttp)

        validator = await valid_oauth_token(token_endpoint='https://oauth.example.com/verify')  # noqa: S106

        result = await validator('test-token')

        assert result.is_success()
        assert result.value_or(None) == 'test-token'

    @pytest.mark.asyncio
    async def it_rejects_token_with_non_200_response(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Invalid OAuth token returns Failure when non-200 is received."""
        import sys
        from unittest.mock import (
            AsyncMock,
            MagicMock,
        )

        # Create a mock response with status 401
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        # Create a mock session
        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        # Create mock aiohttp module
        mock_aiohttp = MagicMock()
        mock_aiohttp.ClientSession = MagicMock(return_value=mock_session)

        monkeypatch.setitem(sys.modules, 'aiohttp', mock_aiohttp)

        validator = await valid_oauth_token(token_endpoint='https://oauth.example.com/verify')  # noqa: S106

        result = await validator('invalid-token')

        assert result.is_failure()
        assert 'invalid oauth token' in result.error_or('').lower()

    @pytest.mark.asyncio
    async def it_returns_failure_when_aiohttp_not_available(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Returns Failure when aiohttp is not installed."""
        import builtins
        import sys

        # Remove aiohttp from sys.modules if present
        monkeypatch.delitem(sys.modules, 'aiohttp', raising=False)

        original_import = builtins.__import__

        def mock_import(name: str, *args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
            if name == 'aiohttp':
                raise ImportError('No module named aiohttp')
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, '__import__', mock_import)

        validator = await valid_oauth_token(token_endpoint='https://oauth.example.com/verify')  # noqa: S106

        result = await validator('any-token')

        assert result.is_failure()
        assert 'aiohttp required' in result.error_or('').lower()

    @pytest.mark.asyncio
    async def it_caches_successful_http_validation(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Successful HTTP validation is cached."""
        import sys
        from unittest.mock import (
            AsyncMock,
            MagicMock,
        )

        # Create a mock response with status 200
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        # Create a mock session
        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        # Create mock aiohttp module
        mock_aiohttp = MagicMock()
        mock_aiohttp.ClientSession = MagicMock(return_value=mock_session)

        monkeypatch.setitem(sys.modules, 'aiohttp', mock_aiohttp)

        cache = MockAsyncCache()
        validator = await valid_oauth_token(token_endpoint='https://oauth.example.com/verify', cache=cache)  # noqa: S106

        result = await validator('cached-token')

        assert result.is_success()
        assert cache.set_count == 1
        assert 'oauth_token_cached-token' in cache._cache  # noqa: SLF001


class DescribeValidEmailDeliverableWithAiodns:
    """Tests for valid_email_deliverable using default aiodns implementation."""

    @pytest.mark.asyncio
    async def it_validates_email_with_mx_records_from_dns(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Email with MX records returns Success."""
        import sys
        from unittest.mock import (
            AsyncMock,
            MagicMock,
        )

        # Create mock MX records
        mock_mx_records = [MagicMock(host='mail.example.com')]

        # Create mock DNS resolver
        mock_resolver_instance = MagicMock()
        mock_resolver_instance.query = AsyncMock(return_value=mock_mx_records)

        # Create mock aiodns module
        mock_aiodns = MagicMock()
        mock_aiodns.DNSResolver = MagicMock(return_value=mock_resolver_instance)

        monkeypatch.setitem(sys.modules, 'aiodns', mock_aiodns)

        validator = await valid_email_deliverable()

        result = await validator('user@example.com')

        assert result.is_success()
        assert result.value_or(None) == 'user@example.com'

    @pytest.mark.asyncio
    async def it_rejects_email_when_no_mx_records_found(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Email without MX records returns Failure."""
        import sys
        from unittest.mock import (
            AsyncMock,
            MagicMock,
        )

        # Create mock with empty MX records
        mock_resolver_instance = MagicMock()
        mock_resolver_instance.query = AsyncMock(return_value=[])

        mock_aiodns = MagicMock()
        mock_aiodns.DNSResolver = MagicMock(return_value=mock_resolver_instance)

        monkeypatch.setitem(sys.modules, 'aiodns', mock_aiodns)

        validator = await valid_email_deliverable()

        result = await validator('user@no-mx.example')

        assert result.is_failure()
        assert 'no mail server' in result.error_or('').lower()

    @pytest.mark.asyncio
    async def it_handles_dns_error_from_aiodns(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """DNS errors are handled gracefully."""
        import sys
        from unittest.mock import (
            AsyncMock,
            MagicMock,
        )

        # Create a mock error class
        class MockDNSError(Exception):
            """Mock DNS error."""

        # Create mock DNS resolver that raises error
        mock_resolver_instance = MagicMock()
        mock_resolver_instance.query = AsyncMock(side_effect=MockDNSError('DNS lookup failed'))

        mock_aiodns = MagicMock()
        mock_aiodns.DNSResolver = MagicMock(return_value=mock_resolver_instance)
        mock_aiodns.error = MagicMock()
        mock_aiodns.error.DNSError = MockDNSError

        monkeypatch.setitem(sys.modules, 'aiodns', mock_aiodns)

        validator = await valid_email_deliverable()

        result = await validator('user@error.example')

        assert result.is_failure()
        assert 'dns error' in result.error_or('').lower()

    @pytest.mark.asyncio
    async def it_handles_nxdomain_error_from_aiodns(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """NXDOMAIN errors indicate domain does not exist."""
        import sys
        from unittest.mock import (
            AsyncMock,
            MagicMock,
        )

        # Create a mock error class
        class MockDNSError(Exception):
            """Mock DNS error."""

        # Create mock DNS resolver that raises NXDOMAIN error
        mock_resolver_instance = MagicMock()
        mock_resolver_instance.query = AsyncMock(side_effect=MockDNSError('NXDOMAIN'))

        mock_aiodns = MagicMock()
        mock_aiodns.DNSResolver = MagicMock(return_value=mock_resolver_instance)
        mock_aiodns.error = MagicMock()
        mock_aiodns.error.DNSError = MockDNSError

        monkeypatch.setitem(sys.modules, 'aiodns', mock_aiodns)

        validator = await valid_email_deliverable()

        result = await validator('user@nonexistent.example')

        assert result.is_failure()
        assert 'does not exist' in result.error_or('').lower()

    @pytest.mark.asyncio
    async def it_returns_failure_when_aiodns_not_available(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Returns Failure when aiodns is not installed."""
        import builtins
        import sys

        # Remove aiodns from sys.modules if present
        monkeypatch.delitem(sys.modules, 'aiodns', raising=False)

        original_import = builtins.__import__

        def mock_import(name: str, *args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
            if name == 'aiodns':
                raise ImportError('No module named aiodns')
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, '__import__', mock_import)

        validator = await valid_email_deliverable()

        result = await validator('user@example.com')

        assert result.is_failure()
        assert 'aiodns required' in result.error_or('').lower()


class DescribeValidApiKeyTimeoutWithVerifier:
    """Tests for timeout handling when verifier is provided."""

    @pytest.mark.asyncio
    async def it_uses_timeout_with_verifier(self) -> None:
        """Timeout is applied when using injected verifier."""
        verifier = MockAPIVerifier(valid_keys={'valid-key'}, delay=0.001)
        validator = await valid_api_key(
            api_url='https://api.example.com/validate',
            verifier=verifier,
            timeout=1.0,
        )

        result = await validator('valid-key')

        assert result.is_success()

    @pytest.mark.asyncio
    async def it_times_out_with_verifier(self) -> None:
        """Timeout triggers failure with injected verifier."""
        verifier = MockAPIVerifier(valid_keys={'valid-key'}, delay=5.0)
        validator = await valid_api_key(
            api_url='https://api.example.com/validate',
            verifier=verifier,
            timeout=0.01,
        )

        result = await validator('valid-key')

        assert result.is_failure()
        assert 'timeout' in result.error_or('').lower()

    @pytest.mark.asyncio
    async def it_handles_no_timeout_with_verifier(self) -> None:
        """No timeout specified works correctly with verifier."""
        verifier = MockAPIVerifier(valid_keys={'valid-key'})
        validator = await valid_api_key(
            api_url='https://api.example.com/validate',
            verifier=verifier,
            timeout=None,  # No timeout
        )

        result = await validator('valid-key')

        assert result.is_success()

    @pytest.mark.asyncio
    async def it_displays_timeout_value_in_error_message(self) -> None:
        """Timeout value is shown in error message."""
        verifier = MockAPIVerifier(raise_timeout=True)
        validator = await valid_api_key(
            api_url='https://api.example.com/validate',
            verifier=verifier,
            timeout=5.0,
        )

        result = await validator('any-key')

        assert result.is_failure()
        error_msg = result.error_or('')
        assert 'timeout' in error_msg.lower()
        assert '5.0' in error_msg or '5' in error_msg

    @pytest.mark.asyncio
    async def it_displays_unset_when_no_timeout_specified(self) -> None:
        """Error message says 'unset' when no timeout specified."""

        # We need to trigger the TimeoutError path without timeout being set
        # The mock verifier with raise_timeout=True will sleep for 10 seconds
        # and with no timeout, we'd wait forever. Instead, let's create a
        # custom verifier that just raises TimeoutError directly.
        class DirectTimeoutVerifier:
            """Verifier that raises TimeoutError directly."""

            async def verify_key(self, _key: str) -> bool:
                raise TimeoutError('Simulated timeout')

        validator = await valid_api_key(
            api_url='https://api.example.com/validate',
            verifier=DirectTimeoutVerifier(),
            timeout=None,
        )

        result = await validator('any-key')

        assert result.is_failure()
        assert 'unset' in result.error_or('').lower()


# =============================================================================
# Tests for all_of composition function
# =============================================================================


class DescribeAllOf:
    """Tests for all_of validator composition function."""

    @pytest.mark.asyncio
    async def it_returns_success_when_all_validators_pass(self) -> None:
        """All validators passing returns Success with original value."""
        from valid8r.async_validators import all_of

        async def check_length(value: str) -> Maybe[str]:
            if len(value) >= 3:
                return Maybe.success(value)
            return Maybe.failure('Too short')

        async def check_alpha(value: str) -> Maybe[str]:
            if value.isalpha():
                return Maybe.success(value)
            return Maybe.failure('Not alphabetic')

        validator = all_of(check_length, check_alpha)
        result = await validator('hello')

        assert result.is_success()
        assert result.value_or('') == 'hello'

    @pytest.mark.asyncio
    async def it_returns_failure_when_any_validator_fails(self) -> None:
        """Any validator failing returns Failure."""
        from valid8r.async_validators import all_of

        async def always_pass(value: str) -> Maybe[str]:
            return Maybe.success(value)

        async def always_fail(_value: str) -> Maybe[str]:
            return Maybe.failure('Always fails')

        validator = all_of(always_pass, always_fail)
        result = await validator('test')

        assert result.is_failure()
        assert 'always fails' in result.error_or('').lower()

    @pytest.mark.asyncio
    async def it_runs_validators_in_parallel(self) -> None:
        """Validators run concurrently for efficiency."""
        import time

        from valid8r.async_validators import all_of

        async def slow_validator(value: str) -> Maybe[str]:
            await asyncio.sleep(0.05)
            return Maybe.success(value)

        validator = all_of(slow_validator, slow_validator, slow_validator)

        start = time.monotonic()
        result = await validator('test')
        elapsed = time.monotonic() - start

        assert result.is_success()
        # If truly parallel, should take ~0.05s, not 0.15s
        assert elapsed < 0.1

    @pytest.mark.asyncio
    async def it_returns_success_for_empty_validators(self) -> None:
        """Empty validator list returns Success with original value."""
        from valid8r.async_validators import all_of

        validator = all_of()
        result = await validator('test')

        assert result.is_success()
        assert result.value_or('') == 'test'

    @pytest.mark.asyncio
    async def it_aggregates_all_errors_when_fail_fast_is_false(self) -> None:
        """When fail_fast=False, all errors are collected."""
        from valid8r.async_validators import all_of

        async def fail_short(_value: str) -> Maybe[str]:
            return Maybe.failure('Too short')

        async def fail_numeric(_value: str) -> Maybe[str]:
            return Maybe.failure('Not numeric')

        validator = all_of(fail_short, fail_numeric, fail_fast=False)
        result = await validator('test')

        assert result.is_failure()
        error = result.error_or('')
        assert 'too short' in error.lower()
        assert 'not numeric' in error.lower()

    @pytest.mark.asyncio
    async def it_returns_first_error_when_fail_fast_is_true(self) -> None:
        """When fail_fast=True (default), returns first error encountered."""
        from valid8r.async_validators import all_of

        async def fail_first(_value: str) -> Maybe[str]:
            return Maybe.failure('First error')

        async def fail_second(_value: str) -> Maybe[str]:
            return Maybe.failure('Second error')

        validator = all_of(fail_first, fail_second, fail_fast=True)
        result = await validator('test')

        assert result.is_failure()
        # Should get the first error (order may vary with parallel execution)
        error = result.error_or('')
        assert 'error' in error.lower()


# =============================================================================
# Tests for any_of composition function
# =============================================================================


class DescribeAnyOf:
    """Tests for any_of validator composition function."""

    @pytest.mark.asyncio
    async def it_returns_success_when_at_least_one_passes(self) -> None:
        """At least one validator passing returns Success."""
        from valid8r.async_validators import any_of

        async def always_fail(_value: str) -> Maybe[str]:
            return Maybe.failure('Always fails')

        async def always_pass(value: str) -> Maybe[str]:
            return Maybe.success(value)

        validator = any_of(always_fail, always_pass)
        result = await validator('test')

        assert result.is_success()
        assert result.value_or('') == 'test'

    @pytest.mark.asyncio
    async def it_returns_failure_when_all_validators_fail(self) -> None:
        """All validators failing returns Failure."""
        from valid8r.async_validators import any_of

        async def fail_one(_value: str) -> Maybe[str]:
            return Maybe.failure('Fails one')

        async def fail_two(_value: str) -> Maybe[str]:
            return Maybe.failure('Fails two')

        validator = any_of(fail_one, fail_two)
        result = await validator('test')

        assert result.is_failure()
        error = result.error_or('')
        # Should aggregate errors when all fail
        assert 'fails' in error.lower()

    @pytest.mark.asyncio
    async def it_runs_validators_in_parallel(self) -> None:
        """Validators run concurrently for efficiency."""
        import time

        from valid8r.async_validators import any_of

        async def slow_validator(value: str) -> Maybe[str]:
            await asyncio.sleep(0.05)
            return Maybe.success(value)

        validator = any_of(slow_validator, slow_validator, slow_validator)

        start = time.monotonic()
        result = await validator('test')
        elapsed = time.monotonic() - start

        assert result.is_success()
        # If truly parallel, should take ~0.05s, not 0.15s
        assert elapsed < 0.1

    @pytest.mark.asyncio
    async def it_returns_failure_for_empty_validators(self) -> None:
        """Empty validator list returns Failure (nothing can succeed)."""
        from valid8r.async_validators import any_of

        validator = any_of()
        result = await validator('test')

        assert result.is_failure()
        assert 'no validators' in result.error_or('').lower()

    @pytest.mark.asyncio
    async def it_returns_first_success_value(self) -> None:
        """Returns value from successful validator."""
        from valid8r.async_validators import any_of

        async def fail_first(_value: str) -> Maybe[str]:
            return Maybe.failure('First fails')

        async def transform_value(value: str) -> Maybe[str]:
            return Maybe.success(f'transformed_{value}')

        validator = any_of(fail_first, transform_value)
        result = await validator('test')

        assert result.is_success()
        # Should get the value from the successful validator
        assert result.value_or('') == 'transformed_test'


# =============================================================================
# Tests for sequence composition function
# =============================================================================


class DescribeSequence:
    """Tests for sequence validator composition function."""

    @pytest.mark.asyncio
    async def it_runs_validators_in_order(self) -> None:
        """Validators are executed sequentially in order."""
        from valid8r.async_validators import sequence

        execution_order: list[str] = []

        async def validator_a(value: int) -> Maybe[int]:
            execution_order.append('a')
            return Maybe.success(value + 1)

        async def validator_b(value: int) -> Maybe[int]:
            execution_order.append('b')
            return Maybe.success(value * 2)

        async def validator_c(value: int) -> Maybe[int]:
            execution_order.append('c')
            return Maybe.success(value + 10)

        validator = sequence(validator_a, validator_b, validator_c)
        result = await validator(5)

        assert execution_order == ['a', 'b', 'c']
        # (5 + 1) * 2 + 10 = 22
        assert result.is_success()
        assert result.value_or(0) == 22

    @pytest.mark.asyncio
    async def it_stops_on_first_failure(self) -> None:
        """Chain stops executing when a validator fails."""
        from valid8r.async_validators import sequence

        execution_order: list[str] = []

        async def validator_pass(value: int) -> Maybe[int]:
            execution_order.append('pass')
            return Maybe.success(value)

        async def validator_fail(_value: int) -> Maybe[int]:
            execution_order.append('fail')
            return Maybe.failure('Validation failed')

        async def validator_never_called(value: int) -> Maybe[int]:
            execution_order.append('never')
            return Maybe.success(value)

        validator = sequence(validator_pass, validator_fail, validator_never_called)
        result = await validator(10)

        assert execution_order == ['pass', 'fail']
        assert result.is_failure()
        assert 'validation failed' in result.error_or('').lower()

    @pytest.mark.asyncio
    async def it_returns_success_for_empty_validators(self) -> None:
        """Empty validator list returns Success with original value."""
        from valid8r.async_validators import sequence

        validator = sequence()
        result = await validator(42)

        assert result.is_success()
        assert result.value_or(0) == 42

    @pytest.mark.asyncio
    async def it_passes_transformed_value_through_chain(self) -> None:
        """Each validator receives the output of the previous one."""
        from valid8r.async_validators import sequence

        async def add_prefix(value: str) -> Maybe[str]:
            return Maybe.success(f'prefix_{value}')

        async def add_suffix(value: str) -> Maybe[str]:
            return Maybe.success(f'{value}_suffix')

        validator = sequence(add_prefix, add_suffix)
        result = await validator('test')

        assert result.is_success()
        assert result.value_or('') == 'prefix_test_suffix'

    @pytest.mark.asyncio
    async def it_executes_sequentially_not_in_parallel(self) -> None:
        """Validators execute one after another, not concurrently."""
        import time

        from valid8r.async_validators import sequence

        async def slow_validator(value: str) -> Maybe[str]:
            await asyncio.sleep(0.05)
            return Maybe.success(value)

        validator = sequence(slow_validator, slow_validator, slow_validator)

        start = time.monotonic()
        result = await validator('test')
        elapsed = time.monotonic() - start

        assert result.is_success()
        # If sequential, should take ~0.15s (3 * 0.05)
        assert elapsed >= 0.14
