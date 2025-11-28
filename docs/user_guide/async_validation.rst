================
Async Validation
================

Overview
========

Valid8r supports asynchronous validation for I/O-bound validation operations such as:

- **Database checks**: Verify email uniqueness, username availability
- **External API calls**: Validate API keys, check payment methods
- **Geolocation services**: Validate IP addresses against geographic constraints
- **Remote file access**: Check file existence on remote systems
- **Any async operation**: Custom async validators for your use case

The async validation feature provides:

- **Concurrent execution**: Multiple async validators run concurrently for better performance
- **Mixed validators**: Combine sync and async validators seamlessly
- **Timeout support**: Configure timeouts to prevent hanging on slow operations
- **Error accumulation**: Collect all validation errors across all fields
- **Type safety**: Full type annotations with mypy support

When to Use Async Validation
=============================

Use async validation when your validation logic requires I/O operations:

**Good use cases:**

- Checking if an email is already registered (database query)
- Validating an API key with an external service (HTTP request)
- Verifying an IP address is from a specific country (geolocation API)
- Checking file permissions on a remote server (network I/O)

**Not recommended:**

- Simple range checks (use sync validators like ``minimum()`` and ``maximum()``)
- Regular expression matching (use sync parsers)
- Pure computational validation (use sync validators)

Quick Start
===========

Basic Async Validator
----------------------

An async validator is any async function that takes a value and returns ``Maybe[T]``:

.. code-block:: python

    import asyncio
    from valid8r.core import parsers, schema
    from valid8r.core.maybe import Maybe

    # Define an async validator
    async def check_email_unique(email: str) -> Maybe[str]:
        """Check if email is unique in database."""
        # Simulate database query
        await asyncio.sleep(0.1)  # Network delay

        # In real code, query your database
        existing_emails = {'admin@example.com', 'user@example.com'}

        if email in existing_emails:
            return Maybe.failure('Email already registered')
        return Maybe.success(email)

    # Use in a schema
    user_schema = schema.Schema(fields={
        'email': schema.Field(
            parser=parsers.parse_email,
            validators=[check_email_unique],  # Add async validator
            required=True
        ),
    })

    # Validate asynchronously
    async def main():
        result = await user_schema.validate_async({
            'email': 'new@example.com'
        })

        match result:
            case schema.Success(data):
                print(f"Valid: {data['email']}")
            case schema.Failure(errors):
                for error in errors:
                    print(f"Error: {error.message}")

    asyncio.run(main())

Schema Async Validation
========================

The ``Schema.validate_async()`` method validates data with support for async validators.

Method Signature
----------------

.. code-block:: python

    async def validate_async(
        self,
        data: dict[str, Any],
        path: str = '',
        *,
        timeout: float | None = None,
    ) -> Maybe[dict[str, Any]]:
        """Validate data asynchronously with async validators.

        Args:
            data: Input data to validate (must be dict-like)
            path: Current field path for nested validation
            timeout: Optional timeout in seconds for async operations

        Returns:
            Success[dict]: Validated data if all fields pass
            Failure[list[ValidationError]]: List of all validation errors

        Raises:
            asyncio.TimeoutError: If validation exceeds the timeout
        """

Basic Usage
-----------

.. code-block:: python

    from valid8r.core import parsers, schema, validators

    # Define schema with async validators
    api_config_schema = schema.Schema(fields={
        'api_key': schema.Field(
            parser=parsers.parse_str,
            validators=[
                validators.min_length(10),  # Sync validator
                verify_api_key_with_service,  # Async validator
            ],
            required=True
        ),
        'endpoint': schema.Field(
            parser=parsers.parse_url,
            required=True
        ),
    })

    # Validate asynchronously
    result = await api_config_schema.validate_async({
        'api_key': 'my-secret-key-123',
        'endpoint': 'https://api.example.com/v1'
    })

Multiple Async Validators
--------------------------

You can chain multiple async validators on a single field:

.. code-block:: python

    async def check_password_not_compromised(password: str) -> Maybe[str]:
        """Check password against breach database."""
        await asyncio.sleep(0.1)
        # Check haveibeenpwned.com API
        if password in ['password123', '12345678']:
            return Maybe.failure('Password found in breach database')
        return Maybe.success(password)

    async def check_password_strength(password: str) -> Maybe[str]:
        """Check password meets strength requirements."""
        await asyncio.sleep(0.05)
        if len(password) < 8:
            return Maybe.failure('Password must be at least 8 characters')
        return Maybe.success(password)

    password_schema = schema.Schema(fields={
        'password': schema.Field(
            parser=parsers.parse_str,
            validators=[
                validators.min_length(1),  # Sync: fail fast on empty
                check_password_strength,  # Async: check strength
                check_password_not_compromised,  # Async: check breaches
            ],
            required=True
        ),
    })

Execution Order
---------------

Valid8r optimizes validation execution for performance:

1. **Sync validators run first** (fail-fast)

   - Sync validators are executed sequentially
   - If any sync validator fails, async validators are skipped
   - This prevents unnecessary async operations for already-invalid data

2. **Async validators run concurrently** (performance)

   - All async validators for a field run sequentially (preserving order)
   - Async validators for different fields run concurrently
   - This maximizes throughput while maintaining deterministic order

.. code-block:: python

    # Example: 3 fields, each with sync + async validators
    schema = Schema(fields={
        'email': Field(
            parser=parse_email,
            validators=[
                min_length(1),  # Sync: runs first
                check_email_unique,  # Async: runs if sync passes
            ]
        ),
        'username': Field(
            parser=parse_str,
            validators=[
                matches_pattern(r'^[a-z0-9_]+$'),  # Sync: runs first
                check_username_available,  # Async: runs if sync passes
            ]
        ),
        'age': Field(
            parser=parse_int,
            validators=[
                minimum(13),  # Sync: runs first
                verify_age_with_service,  # Async: runs if sync passes
            ]
        ),
    })

    # Execution:
    # 1. All sync validators run (min_length, matches_pattern, minimum)
    # 2. If all sync pass, async validators run concurrently across fields
    #    (check_email_unique, check_username_available, verify_age_with_service)

Timeout Support
===============

Configure timeouts to prevent hanging on slow validators.

Setting Timeouts
----------------

.. code-block:: python

    # Set a 5-second timeout for all async operations
    result = await user_schema.validate_async(
        data={'email': 'user@example.com'},
        timeout=5.0
    )

Handling Timeouts
-----------------

Timeouts raise ``asyncio.TimeoutError``:

.. code-block:: python

    import asyncio

    try:
        result = await schema.validate_async(data, timeout=1.0)
    except asyncio.TimeoutError:
        print("Validation timed out after 1 second")
        # Handle timeout: retry, use cached result, fail gracefully

Timeout Best Practices
----------------------

1. **Set reasonable timeouts**

   - Database queries: 1-3 seconds
   - HTTP APIs: 5-10 seconds
   - External services: 10-30 seconds

2. **Handle timeouts gracefully**

   .. code-block:: python

       async def validate_with_fallback(data):
           try:
               return await schema.validate_async(data, timeout=5.0)
           except asyncio.TimeoutError:
               # Fall back to cached validation or default
               return Maybe.success(data)  # Or appropriate fallback

3. **Test timeout behavior**

   .. code-block:: python

       async def slow_validator(value: str) -> Maybe[str]:
           await asyncio.sleep(10.0)  # Intentionally slow
           return Maybe.success(value)

       # This will timeout
       try:
           await schema.validate_async(data, timeout=1.0)
       except asyncio.TimeoutError:
           pass  # Expected

Error Handling
==============

Async validation accumulates all errors across all fields.

Error Structure
---------------

Failed validation returns ``Failure[list[ValidationError]]``:

.. code-block:: python

    from valid8r.core.errors import ValidationError

    result = await schema.validate_async(data)

    match result:
        case Failure(errors):
            for error in errors:
                print(f"Field: {error.path}")
                print(f"Code: {error.code}")
                print(f"Message: {error.message}")
                print(f"Context: {error.context}")

Example Output
--------------

.. code-block:: python

    # Invalid data
    result = await user_schema.validate_async({
        'email': 'existing@example.com',
        'username': 'taken',
        'age': '10'
    })

    # Errors:
    # Field: .email, Message: Email already registered
    # Field: .username, Message: Username not available
    # Field: .age, Message: Must be at least 13

Handling Exceptions in Validators
----------------------------------

If an async validator raises an exception, it's converted to a validation error:

.. code-block:: python

    async def buggy_validator(value: str) -> Maybe[str]:
        raise ValueError("Oops!")  # Unhandled exception

    # Converts to ValidationError with code='VALIDATION_ERROR'
    # Message: "Unexpected error in validator: Oops!"

Best Practice: Always return ``Maybe[T]`` from validators:

.. code-block:: python

    async def safe_validator(value: str) -> Maybe[str]:
        try:
            # Call external API
            result = await api_call(value)
            return Maybe.success(result)
        except APIError as e:
            return Maybe.failure(f"API error: {e}")
        except Exception as e:
            return Maybe.failure(f"Unexpected error: {e}")

Common Patterns
===============

Database Uniqueness Check
--------------------------

.. code-block:: python

    import asyncpg  # PostgreSQL async driver

    async def check_email_unique(
        email: str,
        db_pool: asyncpg.Pool
    ) -> Maybe[str]:
        """Check if email is unique in database."""
        async with db_pool.acquire() as conn:
            count = await conn.fetchval(
                'SELECT COUNT(*) FROM users WHERE email = $1',
                email
            )
            if count > 0:
                return Maybe.failure('Email already registered')
        return Maybe.success(email)

    # Use with dependency injection
    from functools import partial

    db_pool = await asyncpg.create_pool('postgresql://...')

    user_schema = Schema(fields={
        'email': Field(
            parser=parse_email,
            validators=[
                partial(check_email_unique, db_pool=db_pool)
            ],
            required=True
        ),
    })

External API Validation
-----------------------

.. code-block:: python

    import httpx  # Async HTTP client

    async def verify_api_key(
        api_key: str,
        client: httpx.AsyncClient
    ) -> Maybe[str]:
        """Verify API key with external service."""
        try:
            response = await client.get(
                'https://api.example.com/verify',
                headers={'Authorization': f'Bearer {api_key}'},
                timeout=5.0
            )
            if response.status_code == 200:
                return Maybe.success(api_key)
            return Maybe.failure('Invalid API key')
        except httpx.TimeoutException:
            return Maybe.failure('API verification timed out')
        except httpx.HTTPError as e:
            return Maybe.failure(f'API error: {e}')

    # Use in schema
    async with httpx.AsyncClient() as client:
        config_schema = Schema(fields={
            'api_key': Field(
                parser=parse_str,
                validators=[
                    partial(verify_api_key, client=client)
                ],
                required=True
            ),
        })

        result = await config_schema.validate_async(data)

Geolocation Validation
----------------------

.. code-block:: python

    async def check_ip_location(
        ip: str,
        allowed_countries: set[str],
        client: httpx.AsyncClient
    ) -> Maybe[str]:
        """Verify IP address is from allowed country."""
        try:
            response = await client.get(
                f'https://ipapi.co/{ip}/country',
                timeout=3.0
            )
            country = response.text.strip()

            if country in allowed_countries:
                return Maybe.success(ip)
            return Maybe.failure(
                f'IP address from {country}, must be from {allowed_countries}'
            )
        except Exception as e:
            return Maybe.failure(f'Geolocation check failed: {e}')

    # Use in schema
    allowed_countries = {'US', 'CA', 'GB'}

    security_schema = Schema(fields={
        'client_ip': Field(
            parser=parse_ip,
            validators=[
                partial(
                    check_ip_location,
                    allowed_countries=allowed_countries,
                    client=http_client
                )
            ],
            required=True
        ),
    })

Mixing Sync and Async Validators
=================================

You can freely mix sync and async validators on the same field.

Example
-------

.. code-block:: python

    from valid8r.core import validators

    user_schema = Schema(fields={
        'email': Field(
            parser=parse_email,
            validators=[
                # Sync validators (fast fail)
                validators.min_length(1),
                validators.matches_pattern(r'^[^@]+@[^@]+\.[^@]+$'),

                # Async validators (I/O operations)
                check_email_unique,
                check_email_not_disposable,
            ],
            required=True
        ),
    })

Performance Considerations
--------------------------

- **Sync validators run first**: Fast failure before expensive async operations
- **Async validators run after**: Only if sync validators pass
- **Order matters**: Place cheapest validators first

.. code-block:: python

    validators=[
        min_length(1),  # Fastest: simple check
        matches_pattern(r'...'),  # Fast: regex check
        check_local_cache,  # Medium: async cache lookup
        check_external_api,  # Slowest: HTTP request
    ]

Performance Optimization
========================

Concurrent Field Validation
---------------------------

Valid8r automatically runs async validators for different fields concurrently:

.. code-block:: python

    # These async validators run concurrently (not sequentially)
    schema = Schema(fields={
        'email': Field(validators=[check_email_unique]),  # Database
        'api_key': Field(validators=[verify_api_key]),    # HTTP API
        'ip': Field(validators=[check_ip_location]),      # Geolocation API
    })

    # Total time ≈ max(check_email, verify_api, check_ip)
    # Not sum(check_email + verify_api + check_ip)

Caching Results
---------------

Cache expensive validation results to avoid redundant operations:

.. code-block:: python

    from functools import lru_cache

    @lru_cache(maxsize=1000)
    async def check_email_unique_cached(email: str) -> Maybe[str]:
        """Cached email uniqueness check."""
        # Cache hit: return immediately
        # Cache miss: query database
        return await check_email_unique(email)

Rate Limiting with RateLimitedValidator
---------------------------------------

The ``RateLimitedValidator`` wrapper protects external APIs from excessive requests
using a token bucket algorithm. This is essential when validating against external
services that have rate limits.

.. code-block:: python

    from valid8r.async_validators import RateLimitedValidator

    # Create an async validator that calls an external API
    async def verify_api_key(key: str) -> Maybe[str]:
        """Verify API key with external service."""
        # http_client is an httpx.AsyncClient instance
        response = await http_client.get(
            'https://api.example.com/verify',
            headers={'Authorization': f'Bearer {key}'}
        )
        if response.status_code == 200:
            return Maybe.success(key)
        return Maybe.failure('Invalid API key')

    # Wrap with rate limiting: 10 calls/second, burst up to 5
    rate_limited_validator = RateLimitedValidator(
        verify_api_key,
        rate=10,    # 10 calls per second sustained rate
        burst=5     # Allow up to 5 immediate calls before rate limiting
    )

    # Use the rate-limited validator
    result = await rate_limited_validator('my-api-key')

**Token Bucket Algorithm**:

- ``rate``: Maximum calls per second (sustained throughput)
- ``burst``: Maximum immediate calls before throttling begins (defaults to ``rate``)

The algorithm allows bursts of traffic up to the ``burst`` limit, then throttles
excess calls to the sustained ``rate``. This handles bursty traffic patterns
while protecting backend services.

**Example with burst behavior**:

.. code-block:: python

    # Rate: 2 calls/second, Burst: 5
    rate_limited = RateLimitedValidator(my_validator, rate=2, burst=5)

    # First 5 calls complete immediately (burst capacity)
    for i in range(5):
        await rate_limited(f'value_{i}')  # No delay

    # Subsequent calls are rate-limited to 2/second
    await rate_limited('value_5')  # Delays ~0.5s to maintain 2/sec rate

**Concurrent validation with rate limiting**:

.. code-block:: python

    from valid8r.async_validators import RateLimitedValidator, parallel_validate

    # Wrap validator with rate limiting
    rate_limited = RateLimitedValidator(
        external_api_validator,
        rate=10,
        burst=5
    )

    # Validate many values - rate limiting prevents API overload
    values = ['value_1', 'value_2', 'value_3']  # ... more values
    results = await parallel_validate(rate_limited, values)

**Custom Rate Limiter (Advanced)**:

For more complex rate limiting scenarios, you can build your own:

.. code-block:: python

    import asyncio
    from datetime import datetime, timedelta

    class RateLimiter:
        def __init__(self, max_calls: int, period: timedelta):
            self.max_calls = max_calls
            self.period = period
            self.calls: list[datetime] = []
            self.lock = asyncio.Lock()

        async def acquire(self):
            async with self.lock:
                now = datetime.now()
                # Remove old calls
                self.calls = [
                    call for call in self.calls
                    if now - call < self.period
                ]

                if len(self.calls) >= self.max_calls:
                    # Wait until we can make another call
                    oldest_call = min(self.calls)
                    wait_time = (oldest_call + self.period - now).total_seconds()
                    await asyncio.sleep(max(0, wait_time))

                self.calls.append(now)

    # Use rate limiter
    rate_limiter = RateLimiter(max_calls=10, period=timedelta(seconds=1))

    async def rate_limited_validator(value: str) -> Maybe[str]:
        await rate_limiter.acquire()
        return await expensive_api_call(value)

Retry Logic with Exponential Backoff
-------------------------------------

Use ``RetryingValidator`` to automatically retry async validators on transient failures.
This is essential for handling network hiccups, temporary service unavailability, and
rate-limited APIs.

.. code-block:: python

    from valid8r.async_validators import RetryingValidator
    from valid8r.core.maybe import Maybe

    # Define an async validator that might fail transiently
    async def validate_with_api(value: str) -> Maybe[str]:
        """Validate value against external API."""
        try:
            response = await httpx_client.post(
                'https://api.example.com/validate',
                json={'value': value}
            )
            if response.status_code == 200:
                return Maybe.success(value)
            if response.status_code >= 500:
                # Server error - transient failure
                return Maybe.failure('Transient: server error')
            return Maybe.failure('Validation failed')
        except httpx.ConnectError:
            return Maybe.failure('Transient: connection error')

    # Wrap with retry logic
    robust_validator = RetryingValidator(
        validate_with_api,
        max_retries=3,        # Retry up to 3 times
        base_delay=1.0,       # Start with 1 second delay
        max_delay=60.0,       # Never wait more than 60 seconds
        exponential_base=2.0, # Double delay each retry
        jitter=True,          # Add randomness to prevent thundering herd
    )

    # Use the wrapped validator
    result = await robust_validator('my-value')

RetryingValidator Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``validator``
    The async validator function to wrap. Must return ``Maybe[T]``.

``max_retries`` (default: 3)
    Maximum number of retry attempts after the initial call fails.
    Total attempts = initial + max_retries = 4 by default.

``base_delay`` (default: 1.0)
    Base delay in seconds for exponential backoff.
    Delay formula: ``base_delay * exponential_base^attempt``

``max_delay`` (default: 60.0)
    Maximum delay cap in seconds. Prevents excessively long waits.

``exponential_base`` (default: 2.0)
    Base for exponential backoff calculation. With 2.0, delays double
    each retry: 1s -> 2s -> 4s -> 8s...

``jitter`` (default: True)
    Add random jitter to delays (0 to calculated_delay).
    Prevents thundering herd when multiple validators retry simultaneously.

Retry Behavior
^^^^^^^^^^^^^^^

- **All failures are retried**: Any ``Failure`` result triggers a retry
- **Exceptions are caught**: Exceptions during validation are caught and retried
- **Last error preserved**: Final failure includes the last error message
- **State tracking**: ``retry_count`` and ``retry_delays`` attributes available after call

Example: Tracking Retry Metrics
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    validator = RetryingValidator(
        flaky_api_validator,
        max_retries=5,
        base_delay=0.5,
        jitter=False,  # Disable for deterministic testing
    )

    result = await validator('test-value')

    # Check retry metrics
    print(f"Retries performed: {validator.retry_count}")
    print(f"Delays used: {validator.retry_delays}")

    # Output might be:
    # Retries performed: 2
    # Delays used: [0.5, 1.0]  # Two retries with exponential backoff

Best Practices for Retry Logic
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. **Set reasonable max_retries**

   - Database operations: 2-3 retries
   - HTTP APIs: 3-5 retries
   - Critical operations: Consider circuit breaker pattern instead

2. **Use jitter in production**

   .. code-block:: python

       # Good: jitter prevents thundering herd
       RetryingValidator(validator, jitter=True)

       # Only for testing: disable jitter for deterministic tests
       RetryingValidator(validator, jitter=False)

3. **Distinguish transient vs permanent failures**

   .. code-block:: python

       async def smart_validator(value: str) -> Maybe[str]:
           try:
               response = await api_call(value)
               if response.status_code == 200:
                   return Maybe.success(value)
               if response.status_code >= 500:
                   # Transient: will be retried
                   return Maybe.failure('Transient: server error')
               # Permanent: 4xx errors, will be retried but likely to fail
               return Maybe.failure('Validation failed')
           except ConnectionError:
               # Transient: network issues
               return Maybe.failure('Transient: network error')

4. **Combine with timeouts**

   .. code-block:: python

       import asyncio

       async def validate_with_timeout(value):
           validator = RetryingValidator(
               api_validator,
               max_retries=3,
               base_delay=1.0,
           )
           try:
               return await asyncio.wait_for(
                   validator(value),
                   timeout=30.0  # Overall timeout for all retries
               )
           except asyncio.TimeoutError:
               return Maybe.failure('Validation timed out')

Testing Async Validators
=========================

Unit Testing
------------

Test async validators using ``pytest-asyncio``:

.. code-block:: python

    import pytest
    from valid8r.testing import assert_maybe_success, assert_maybe_failure

    @pytest.mark.asyncio
    async def test_check_email_unique_success():
        """Unique email passes validation."""
        result = await check_email_unique('new@example.com')
        assert assert_maybe_success(result, 'new@example.com')

    @pytest.mark.asyncio
    async def test_check_email_unique_failure():
        """Existing email fails validation."""
        result = await check_email_unique('existing@example.com')
        assert assert_maybe_failure(result, 'already registered')

Mocking Async Dependencies
---------------------------

Mock database and API calls for testing:

.. code-block:: python

    from unittest.mock import AsyncMock, patch

    @pytest.mark.asyncio
    async def test_verify_api_key_success():
        """Valid API key passes validation."""
        mock_client = AsyncMock()
        mock_client.get.return_value.status_code = 200

        result = await verify_api_key('valid-key', mock_client)
        assert assert_maybe_success(result, 'valid-key')

    @pytest.mark.asyncio
    async def test_verify_api_key_failure():
        """Invalid API key fails validation."""
        mock_client = AsyncMock()
        mock_client.get.return_value.status_code = 401

        result = await verify_api_key('invalid-key', mock_client)
        assert assert_maybe_failure(result, 'Invalid API key')

Integration Testing
-------------------

Test with real async operations (database, API):

.. code-block:: python

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_schema_validation_with_database(test_db_pool):
        """Full schema validation with real database."""
        schema = Schema(fields={
            'email': Field(
                parser=parse_email,
                validators=[
                    partial(check_email_unique, db_pool=test_db_pool)
                ],
                required=True
            ),
        })

        # Test with test database
        result = await schema.validate_async({
            'email': 'test@example.com'
        })
        assert result.is_success()

Migration from Sync to Async
=============================

If you have existing sync validators, migrate gradually:

Step 1: Keep Sync Validators
-----------------------------

.. code-block:: python

    # Existing sync validation
    schema = Schema(fields={
        'email': Field(
            parser=parse_email,
            validators=[check_format],  # Sync validator
            required=True
        ),
    })

    # Still works with validate()
    result = schema.validate(data)

Step 2: Add Async Validators
-----------------------------

.. code-block:: python

    # Add async validators alongside sync
    schema = Schema(fields={
        'email': Field(
            parser=parse_email,
            validators=[
                check_format,  # Sync: format check
                check_email_unique,  # Async: database check
            ],
            required=True
        ),
    })

    # Use validate_async() for async support
    result = await schema.validate_async(data)

Step 3: Gradually Replace
--------------------------

.. code-block:: python

    # Eventually replace sync with async where appropriate
    schema = Schema(fields={
        'email': Field(
            parser=parse_email,
            validators=[
                check_email_unique,  # Async only
            ],
            required=True
        ),
    })

Backward Compatibility
----------------------

- ``validate()`` method still works (skips async validators)
- ``validate_async()`` method supports both sync and async validators
- No breaking changes to existing code

See Also
========

- :doc:`schema` - Schema validation basics
- :doc:`validators` - Built-in validator functions
- :doc:`maybe_monad` - Understanding Maybe monad
- :doc:`error_handling` - Error handling patterns
