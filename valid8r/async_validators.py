"""Async validator library for I/O-bound validation operations.

This module provides validators for operations that require async I/O,
such as database queries, API calls, and DNS lookups.

All validators return `Maybe[T]` and follow the same composable pattern
as synchronous validators. This allows for efficient validation against
external systems without blocking the event loop.

Key Features:
    - Database validation (unique_in_db, exists_in_db)
    - API validation (valid_api_key, valid_oauth_token)
    - Email deliverability (valid_email_deliverable)
    - Rate limiting (RateLimitedValidator)
    - Batch validation (parallel_validate)
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

import asyncio
import random
import time
from collections.abc import (
    Awaitable,
    Callable,
    Sequence,
)
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Protocol,
    TypeVar,
)

from valid8r.core.maybe import Maybe

if TYPE_CHECKING:
    from valid8r.core.parsers import EmailAddress

# Type variables
T = TypeVar('T')

# Type alias for async validators
AsyncValidator = Callable[[Any], Awaitable[Maybe[Any]]]


class AsyncCache(Protocol):
    """Protocol for async cache implementations."""

    async def get(self, key: str) -> Any | None:  # noqa: ANN401
        """Get value from cache."""
        ...

    async def set(self, key: str, value: Any) -> None:  # noqa: ANN401
        """Set value in cache."""
        ...


class DNSResolver(Protocol):
    """Protocol for DNS resolver implementations."""

    async def resolve_mx(self, domain: str) -> list[str]:
        """Resolve MX records for domain."""
        ...


class APIVerifier(Protocol):
    """Protocol for API key verification."""

    async def verify_key(self, key: str) -> bool:
        """Verify an API key."""
        ...


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


async def valid_api_key(  # noqa: C901
    *,
    api_url: str,
    timeout: float | None = None,  # noqa: ASYNC109
    verifier: APIVerifier | None = None,
    cache: AsyncCache | None = None,
) -> AsyncValidator:
    """Create a validator that checks if an API key is valid against an external service.

    This validator calls an external API endpoint to validate API keys. Use this
    when validating API keys before processing requests that require authentication.

    Args:
        api_url: The URL of the API endpoint to validate keys against
        timeout: Optional timeout in seconds for the API call
        verifier: Optional custom API verifier (for testing/mocking)
        cache: Optional async cache for storing validation results

    Returns:
        An async validator function that:
            - Accepts an API key to validate
            - Returns Maybe[str]: Success(key) if valid, Failure(error_msg) if not
            - Returns Failure for network errors or timeouts

    Example:
        >>> import asyncio
        >>> from valid8r.async_validators import valid_api_key
        >>>
        >>> async def validate_key():
        ...     validator = await valid_api_key(
        ...         api_url='https://api.example.com/validate',
        ...         timeout=5.0
        ...     )
        ...     result = await validator('my-api-key-123')
        ...     if result.is_success():
        ...         print("API key is valid!")
        ...     else:
        ...         print(f"Invalid: {result.error_or('')}")

    """

    async def validator(key: str) -> Maybe[str]:  # noqa: C901, PLR0912
        """Validate an API key against the external service."""
        cache_key = f'api_key_{key}'

        # Check cache first
        if cache is not None:
            cached = await cache.get(cache_key)
            if cached is not None:
                return Maybe.success(key)

        try:
            if verifier is not None:
                # Use injected verifier (for testing)
                if timeout:
                    is_valid = await asyncio.wait_for(
                        verifier.verify_key(key),
                        timeout=timeout,
                    )
                else:
                    is_valid = await verifier.verify_key(key)

                if is_valid:
                    # Cache the result
                    if cache is not None:
                        await cache.set(cache_key, True)  # noqa: FBT003
                    return Maybe.success(key)
                return Maybe.failure('Invalid API key')

            # Default implementation using aiohttp (if available)
            try:
                import aiohttp  # noqa: PLC0415

                http_ok = 200
                async with aiohttp.ClientSession() as session:
                    headers = {'Authorization': f'Bearer {key}'}
                    async with session.get(
                        api_url,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=timeout),
                    ) as response:
                        if response.status == http_ok:
                            if cache is not None:
                                await cache.set(cache_key, True)  # noqa: FBT003
                            return Maybe.success(key)
                        return Maybe.failure('Invalid API key')
            except ImportError:
                # aiohttp not available, return error
                return Maybe.failure('aiohttp required for API validation')

        except TimeoutError:
            timeout_val = timeout if timeout else 'unset'
            return Maybe.failure(f'Validation timeout after {timeout_val} seconds')
        except ConnectionError as e:
            return Maybe.failure(f'Network error: {e}')
        except Exception as e:  # noqa: BLE001
            return Maybe.failure(f'API validation error: {e}')

    return validator


async def valid_oauth_token(  # noqa: C901
    *,
    token_endpoint: str,
    cache: AsyncCache | None = None,
    verifier: APIVerifier | None = None,
) -> AsyncValidator:
    """Create a validator that checks if an OAuth token is valid.

    This validator calls an OAuth token endpoint to validate tokens. Optionally
    supports caching to avoid redundant API calls for the same token.

    Args:
        token_endpoint: The URL of the OAuth token validation endpoint
        cache: Optional async cache for storing validation results
        verifier: Optional custom API verifier (for testing/mocking)

    Returns:
        An async validator function that:
            - Accepts an OAuth token to validate
            - Returns Maybe[str]: Success(token) if valid, Failure(error_msg) if not
            - Uses cache if provided to avoid redundant calls

    Example:
        >>> import asyncio
        >>> from valid8r.async_validators import valid_oauth_token
        >>>
        >>> async def validate_token():
        ...     validator = await valid_oauth_token(
        ...         token_endpoint='https://oauth.example.com/token'
        ...     )
        ...     result = await validator('bearer-token-123')
        ...     if result.is_success():
        ...         print("Token is valid!")

    """

    async def validator(token: str) -> Maybe[str]:  # noqa: C901
        """Validate an OAuth token."""
        cache_key = f'oauth_token_{token}'

        # Check cache first
        if cache is not None:
            cached = await cache.get(cache_key)
            if cached is not None:
                return Maybe.success(token)

        try:
            if verifier is not None:
                # Use injected verifier (for testing)
                is_valid = await verifier.verify_key(token)

                if is_valid:
                    # Cache the result
                    if cache is not None:
                        await cache.set(cache_key, True)  # noqa: FBT003
                    return Maybe.success(token)
                return Maybe.failure('Invalid OAuth token')

            # Default implementation using aiohttp
            try:
                import aiohttp  # noqa: PLC0415

                http_ok = 200
                async with aiohttp.ClientSession() as session:
                    headers = {'Authorization': f'Bearer {token}'}
                    async with session.get(token_endpoint, headers=headers) as response:
                        if response.status == http_ok:
                            if cache is not None:
                                await cache.set(cache_key, True)  # noqa: FBT003
                            return Maybe.success(token)
                        return Maybe.failure('Invalid OAuth token')
            except ImportError:
                return Maybe.failure('aiohttp required for OAuth validation')

        except ConnectionError as e:
            return Maybe.failure(f'Network error: {e}')
        except Exception as e:  # noqa: BLE001
            return Maybe.failure(f'OAuth validation error: {e}')

    return validator


async def valid_email_deliverable(  # noqa: C901
    *,
    resolver: DNSResolver | None = None,
) -> AsyncValidator:
    """Create a validator that checks if an email address is deliverable.

    This validator checks if the email domain has valid MX records, indicating
    that the domain can receive email. Use this for validating email addresses
    beyond just format checking.

    Args:
        resolver: Optional DNS resolver (for testing/mocking)

    Returns:
        An async validator function that:
            - Accepts an email address (string or EmailAddress object)
            - Returns Maybe[EmailAddress]: Success if deliverable, Failure if not

    Example:
        >>> import asyncio
        >>> from valid8r.async_validators import valid_email_deliverable
        >>>
        >>> async def check_email():
        ...     validator = await valid_email_deliverable()
        ...     result = await validator('user@example.com')
        ...     if result.is_success():
        ...         print("Email domain can receive mail!")

    """

    async def validator(email: str | EmailAddress) -> Maybe[Any]:  # noqa: C901
        """Validate email deliverability via MX record lookup."""
        # Extract domain from email
        if hasattr(email, 'domain'):
            # EmailAddress object
            domain = email.domain
            email_value = email
        else:
            # String email
            if '@' not in str(email):
                return Maybe.failure('Invalid email format')
            domain = str(email).split('@')[1]
            email_value = email

        try:
            if resolver is not None:
                # Use injected resolver (for testing)
                mx_records = await resolver.resolve_mx(domain)
                if not mx_records:
                    return Maybe.failure(f'No mail server found for domain {domain}')
                return Maybe.success(email_value)

            # Default implementation using aiodns
            try:
                import aiodns  # noqa: PLC0415

                dns_resolver = aiodns.DNSResolver()
                try:
                    mx_records = await dns_resolver.query(domain, 'MX')
                    if mx_records:
                        return Maybe.success(email_value)
                    return Maybe.failure(f'No mail server found for domain {domain}')
                except aiodns.error.DNSError as e:
                    if 'NXDOMAIN' in str(e):
                        return Maybe.failure(f'Domain {domain} does not exist')
                    return Maybe.failure(f'DNS error: {e}')
            except ImportError:
                return Maybe.failure('aiodns required for email deliverability check')

        except ValueError as e:
            if 'does not exist' in str(e).lower() or 'nxdomain' in str(e).lower():
                return Maybe.failure(f'Domain {domain} does not exist')
            return Maybe.failure(f'DNS lookup error: {e}')
        except Exception as e:  # noqa: BLE001
            return Maybe.failure(f'Email deliverability check failed: {e}')

    return validator


class RateLimitedValidator(Generic[T]):
    """A wrapper that adds rate limiting to async validators.

    Uses a token bucket algorithm to limit the rate of validation calls.
    This is useful for protecting external services from being overwhelmed.

    Args:
        validator: The async validator function to wrap
        rate: Maximum number of calls per second
        burst: Maximum burst size (defaults to rate)

    Example:
        >>> import asyncio
        >>> from valid8r.async_validators import RateLimitedValidator
        >>>
        >>> async def my_validator(value):
        ...     return Maybe.success(value)
        >>>
        >>> rate_limited = RateLimitedValidator(my_validator, rate=10, burst=5)
        >>> result = await rate_limited('test')

    """

    def __init__(
        self,
        validator: AsyncValidator,
        *,
        rate: int,
        burst: int | None = None,
    ) -> None:
        """Initialize the rate-limited validator.

        Args:
            validator: The async validator function to wrap
            rate: Maximum number of calls per second
            burst: Maximum burst size (defaults to rate)

        """
        self._validator = validator
        self._rate = rate
        self._burst = burst if burst is not None else rate
        self._tokens = float(self._burst)
        self._last_update = time.monotonic()
        self._lock = asyncio.Lock()

    async def _acquire_token(self) -> float:
        """Acquire a token from the bucket, returning wait time if needed."""
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_update
            self._last_update = now

            # Add tokens based on elapsed time
            self._tokens = min(self._burst, self._tokens + elapsed * self._rate)

            if self._tokens >= 1:
                self._tokens -= 1
                return 0.0

            # Calculate wait time
            return (1 - self._tokens) / self._rate

    async def __call__(self, value: T) -> Maybe[T]:
        """Validate a value with rate limiting.

        Args:
            value: The value to validate

        Returns:
            Maybe[T]: The validation result

        """
        wait_time = await self._acquire_token()
        if wait_time > 0:
            await asyncio.sleep(wait_time)
            # After waiting, we have our token
            async with self._lock:
                self._tokens = max(0, self._tokens - 1)

        return await self._validator(value)


class RetryValidator(Generic[T]):
    """A wrapper that adds retry logic to async validators.

    Retries validation on transient failures with configurable backoff.

    Args:
        validator: The async validator function to wrap
        max_retries: Maximum number of retry attempts (default: 3)
        base_delay: Base delay in seconds for exponential backoff (default: 0.1)
        exponential: Use exponential backoff if True (default: True)

    Example:
        >>> import asyncio
        >>> from valid8r.async_validators import RetryValidator
        >>>
        >>> retry_validator = RetryValidator(my_validator, max_retries=3)
        >>> result = await retry_validator('test')

    """

    def __init__(
        self,
        validator: AsyncValidator,
        *,
        max_retries: int = 3,
        base_delay: float = 0.1,
        exponential: bool = True,
    ) -> None:
        """Initialize the retry validator.

        Args:
            validator: The async validator function to wrap
            max_retries: Maximum number of retry attempts
            base_delay: Base delay in seconds for backoff
            exponential: Use exponential backoff if True

        """
        self._validator = validator
        self._max_retries = max_retries
        self._base_delay = base_delay
        self._exponential = exponential
        self.retry_count = 0
        self.retry_delays: list[float] = []

    async def __call__(self, value: T) -> Maybe[T]:
        """Validate a value with retry logic.

        Args:
            value: The value to validate

        Returns:
            Maybe[T]: The validation result

        """
        self.retry_count = 0
        self.retry_delays = []
        last_error = ''

        for attempt in range(self._max_retries + 1):
            try:
                result = await self._validator(value)

                # If validation succeeded, return immediately
                if result.is_success():
                    return result

                # If it's a logical failure (not a transient error), don't retry
                error_msg = result.error_or('')
                if 'transient' not in error_msg.lower() and attempt == 0:
                    # First attempt with non-transient error
                    return result

                last_error = error_msg
                self.retry_count += 1

            except Exception as e:  # noqa: BLE001
                last_error = str(e)
                self.retry_count += 1

            # Calculate delay for next retry
            if attempt < self._max_retries:
                delay = self._base_delay * (2**attempt) if self._exponential else self._base_delay
                self.retry_delays.append(delay)
                await asyncio.sleep(delay)

        return Maybe.failure(f'Validation failed after max retries exceeded: {last_error}')


class RetryingValidator(Generic[T]):
    """Wrap async validator with retry logic and exponential backoff.

    This validator wrapper adds robust retry handling for transient failures
    with configurable exponential backoff and optional jitter. Use this to
    make async validators resilient to temporary network issues, rate limits,
    or service unavailability.

    The retry logic:
    1. Attempts the validation
    2. On failure, waits with exponential backoff before retrying
    3. Optionally adds jitter to prevent thundering herd problems
    4. Caps delay at max_delay to prevent excessive waits
    5. After max_retries exhausted, returns failure with last error

    Args:
        validator: The async validator function to wrap. Must be a callable
            that takes a value and returns Awaitable[Maybe[T]].
        max_retries: Maximum number of retry attempts after the initial call.
            Default: 3 (4 total attempts including initial).
        base_delay: Base delay in seconds for exponential backoff. The actual
            delay is base_delay * exponential_base^attempt. Default: 1.0.
        max_delay: Maximum delay in seconds. Delays are capped at this value
            to prevent excessive waiting. Default: 60.0.
        exponential_base: Base for exponential backoff calculation. A value
            of 2.0 doubles the delay each retry. Default: 2.0.
        jitter: If True, adds random jitter to delays to prevent thundering
            herd when multiple validators retry simultaneously. Default: True.

    Attributes:
        retry_count: Number of retries performed in the last validation call.
        retry_delays: List of actual delays (in seconds) used between retries.

    Example:
        >>> import asyncio
        >>> from valid8r.async_validators import RetryingValidator
        >>> from valid8r.core.maybe import Maybe
        >>>
        >>> async def flaky_api_validator(value: str) -> Maybe[str]:
        ...     # Simulates a validator that might fail transiently
        ...     import random
        ...     if random.random() < 0.5:
        ...         return Maybe.failure('Transient: service unavailable')
        ...     return Maybe.success(value)
        >>>
        >>> async def main():
        ...     # Wrap with retry logic
        ...     robust_validator = RetryingValidator(
        ...         flaky_api_validator,
        ...         max_retries=3,
        ...         base_delay=0.5,
        ...         max_delay=5.0,
        ...         jitter=True
        ...     )
        ...     result = await robust_validator('test-value')
        ...     print(f'Success: {result.is_success()}')
        >>>
        >>> asyncio.run(main())

    Notes:
        - All failures are retried, not just those containing "transient"
        - Exceptions during validation are caught and converted to retries
        - The retry_count and retry_delays attributes are reset on each call

    """

    def __init__(  # noqa: PLR0913
        self,
        validator: Callable[[T], Awaitable[Maybe[T]]],
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        *,
        jitter: bool = True,
    ) -> None:
        """Initialize the retrying validator.

        Args:
            validator: The async validator function to wrap
            max_retries: Maximum number of retry attempts (default: 3)
            base_delay: Base delay in seconds for backoff (default: 1.0)
            max_delay: Maximum delay in seconds (default: 60.0)
            exponential_base: Base for exponential calculation (default: 2.0)
            jitter: Add random jitter to delays (default: True)

        """
        self._validator = validator
        self._max_retries = max_retries
        self._base_delay = base_delay
        self._max_delay = max_delay
        self._exponential_base = exponential_base
        self._jitter = jitter
        self.retry_count = 0
        self.retry_delays: list[float] = []

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for the given attempt with optional jitter.

        Args:
            attempt: Zero-based attempt number (0 for first retry)

        Returns:
            Delay in seconds, capped at max_delay

        """
        base = self._base_delay * (self._exponential_base**attempt)
        delay = min(base, self._max_delay)

        if self._jitter:
            # S311: random is sufficient for jitter (not cryptographic)
            delay = random.uniform(0, delay)  # noqa: S311

        return delay

    async def __call__(self, value: T) -> Maybe[T]:
        """Validate a value with retry logic.

        Attempts validation up to max_retries times on failure, using
        exponential backoff between attempts.

        Args:
            value: The value to validate

        Returns:
            Maybe[T]: Success with validated value, or Failure with error
                message including "max retries exceeded" if all attempts fail

        """
        self.retry_count = 0
        self.retry_delays = []
        last_error = ''

        for attempt in range(self._max_retries + 1):
            try:
                result = await self._validator(value)

                if result.is_success():
                    return result

                last_error = result.error_or('')

            except Exception as e:  # noqa: BLE001
                last_error = str(e)

            if attempt < self._max_retries:
                delay = self._calculate_delay(attempt)
                self.retry_delays.append(delay)
                await asyncio.sleep(delay)
                self.retry_count += 1

        return Maybe.failure(f'Max retries exceeded: {last_error}')


async def parallel_validate(
    validator: AsyncValidator,
    values: Sequence[T],
) -> list[Maybe[T]]:
    """Validate multiple values concurrently.

    This helper function validates a sequence of values in parallel,
    returning all results (both successes and failures).

    Args:
        validator: The async validator function to use
        values: Sequence of values to validate

    Returns:
        List of Maybe[T] results in the same order as input values

    Example:
        >>> import asyncio
        >>> from valid8r.async_validators import parallel_validate
        >>>
        >>> async def validate_emails():
        ...     emails = ['a@example.com', 'b@example.com', 'c@example.com']
        ...     results = await parallel_validate(email_validator, emails)
        ...     successes = [r for r in results if r.is_success()]
        ...     failures = [r for r in results if r.is_failure()]

    """
    tasks = [validator(value) for value in values]
    return await asyncio.gather(*tasks)


async def sequential_validate(
    validators: Sequence[AsyncValidator],
    value: T,
) -> Maybe[T]:
    """Run validators sequentially, stopping on first failure.

    This helper function runs a sequence of validators one after another,
    passing the value through each validator. Stops on first failure.

    Args:
        validators: Sequence of async validators to run
        value: The value to validate

    Returns:
        Maybe[T]: Success if all validators pass, first Failure otherwise

    Example:
        >>> import asyncio
        >>> from valid8r.async_validators import sequential_validate
        >>>
        >>> async def validate_user():
        ...     validators = [format_validator, uniqueness_validator, auth_validator]
        ...     result = await sequential_validate(validators, user_data)

    """
    current_value: Any = value
    for validator in validators:
        result = await validator(current_value)
        if result.is_failure():
            return result
        current_value = result.value_or(current_value)
    return Maybe.success(current_value)


async def compose_parallel(
    validators: Sequence[AsyncValidator],
    value: T,
) -> Maybe[T]:
    """Run validators in parallel and combine results.

    All validators run concurrently. Returns Success if all pass,
    or the first Failure encountered.

    Args:
        validators: Sequence of async validators to run in parallel
        value: The value to validate

    Returns:
        Maybe[T]: Success if all validators pass, first Failure otherwise

    """
    results = await asyncio.gather(*[v(value) for v in validators])

    for result in results:
        if result.is_failure():
            return result

    return Maybe.success(value)


def all_of(
    *validators: AsyncValidator,
    fail_fast: bool = True,
) -> Callable[[T], Awaitable[Maybe[T]]]:
    """Create a composed validator that requires all validators to pass.

    Runs all validators in parallel for efficiency. All validators must succeed
    for the overall validation to succeed. This is useful when you have multiple
    independent validation rules that must all be satisfied.

    Args:
        *validators: Variable number of async validators to compose
        fail_fast: If True (default), returns the first error encountered.
            If False, collects all errors and returns them joined together.

    Returns:
        A callable async validator that:
            - Accepts a value to validate
            - Returns Maybe[T]: Success(value) if all validators pass,
              Failure(error) if any validator fails

    Example:
        >>> import asyncio
        >>> from valid8r.async_validators import all_of
        >>> from valid8r.core.maybe import Maybe
        >>>
        >>> async def check_length(value: str) -> Maybe[str]:
        ...     if len(value) >= 3:
        ...         return Maybe.success(value)
        ...     return Maybe.failure('Too short')
        >>>
        >>> async def check_alpha(value: str) -> Maybe[str]:
        ...     if value.isalpha():
        ...         return Maybe.success(value)
        ...     return Maybe.failure('Not alphabetic')
        >>>
        >>> async def main():
        ...     validator = all_of(check_length, check_alpha)
        ...     result = await validator('hello')
        ...     print(f'Success: {result.is_success()}')
        >>>
        >>> asyncio.run(main())

    Notes:
        - Validators run in parallel using asyncio.gather
        - Empty validator list returns Success with the original value
        - When fail_fast=False, errors are joined with '; '

    """

    async def validator(value: T) -> Maybe[T]:
        """Run all validators in parallel and require all to succeed."""
        if not validators:
            return Maybe.success(value)

        results = await asyncio.gather(*[v(value) for v in validators])

        failures = [r for r in results if r.is_failure()]

        if failures:
            if fail_fast:
                return failures[0]
            errors = [r.error_or('') for r in failures]
            return Maybe.failure('; '.join(errors))

        return Maybe.success(value)

    return validator


def any_of(
    *validators: AsyncValidator,
) -> Callable[[T], Awaitable[Maybe[T]]]:
    """Create a composed validator where at least one validator must pass.

    Runs all validators in parallel for efficiency. At least one validator must
    succeed for the overall validation to succeed. This is useful for alternative
    validation paths or fallback validation logic.

    Args:
        *validators: Variable number of async validators to compose

    Returns:
        A callable async validator that:
            - Accepts a value to validate
            - Returns Maybe[T]: Success(value) if any validator passes,
              Failure(error) if all validators fail

    Example:
        >>> import asyncio
        >>> from valid8r.async_validators import any_of
        >>> from valid8r.core.maybe import Maybe
        >>>
        >>> async def check_email(value: str) -> Maybe[str]:
        ...     if '@' in value:
        ...         return Maybe.success(value)
        ...     return Maybe.failure('Not an email')
        >>>
        >>> async def check_username(value: str) -> Maybe[str]:
        ...     if value.isalnum():
        ...         return Maybe.success(value)
        ...     return Maybe.failure('Not a valid username')
        >>>
        >>> async def main():
        ...     validator = any_of(check_email, check_username)
        ...     # Either email or username format is acceptable
        ...     result = await validator('user123')
        ...     print(f'Success: {result.is_success()}')
        >>>
        >>> asyncio.run(main())

    Notes:
        - Validators run in parallel using asyncio.gather
        - Empty validator list returns Failure (nothing can succeed)
        - Returns the result from the first successful validator
        - If all fail, errors are joined with '; '

    """

    async def validator(value: T) -> Maybe[T]:
        """Run all validators in parallel, require at least one to succeed."""
        if not validators:
            return Maybe.failure('No validators provided')

        results = await asyncio.gather(*[v(value) for v in validators])

        for result in results:
            if result.is_success():
                return result

        errors = [r.error_or('') for r in results if r.is_failure()]
        return Maybe.failure('; '.join(errors))

    return validator


def sequence(
    *validators: AsyncValidator,
) -> Callable[[T], Awaitable[Maybe[T]]]:
    """Create a composed validator that runs validators sequentially.

    Runs validators one after another, passing the result of each validator
    to the next. Stops on first failure. This is useful when validators have
    dependencies or when the output of one validator feeds into the next.

    Args:
        *validators: Variable number of async validators to compose

    Returns:
        A callable async validator that:
            - Accepts a value to validate
            - Returns Maybe[T]: Success(final_value) if all validators pass,
              Failure(error) on first failure

    Example:
        >>> import asyncio
        >>> from valid8r.async_validators import sequence
        >>> from valid8r.core.maybe import Maybe
        >>>
        >>> async def trim_whitespace(value: str) -> Maybe[str]:
        ...     return Maybe.success(value.strip())
        >>>
        >>> async def to_lowercase(value: str) -> Maybe[str]:
        ...     return Maybe.success(value.lower())
        >>>
        >>> async def validate_length(value: str) -> Maybe[str]:
        ...     if len(value) >= 3:
        ...         return Maybe.success(value)
        ...     return Maybe.failure('Too short')
        >>>
        >>> async def main():
        ...     validator = sequence(trim_whitespace, to_lowercase, validate_length)
        ...     result = await validator('  HELLO  ')
        ...     print(f'Result: {result.value_or("")}')  # 'hello'
        >>>
        >>> asyncio.run(main())

    Notes:
        - Validators run sequentially, NOT in parallel
        - Each validator receives the SUCCESS value from the previous one
        - Stops execution on first Failure
        - Empty validator list returns Success with the original value

    """

    async def validator(value: T) -> Maybe[T]:
        """Run validators sequentially, passing output to next validator."""
        current_value: Any = value
        for v in validators:
            result = await v(current_value)
            if result.is_failure():
                return result
            current_value = result.value_or(current_value)
        return Maybe.success(current_value)

    return validator


# Export all public symbols
__all__ = [
    'AsyncCache',
    'AsyncValidator',
    'DNSResolver',
    'RateLimitedValidator',
    'RetryValidator',
    'RetryingValidator',
    'all_of',
    'any_of',
    'compose_parallel',
    'exists_in_db',
    'parallel_validate',
    'sequence',
    'sequential_validate',
    'unique_in_db',
    'valid_api_key',
    'valid_email_deliverable',
    'valid_oauth_token',
]
