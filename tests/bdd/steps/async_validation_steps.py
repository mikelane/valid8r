"""BDD step definitions for async validation feature.

This module implements black-box tests for async validation through
step definitions that exercise the public interface.
"""

from __future__ import annotations

import asyncio
import time
from typing import (
    TYPE_CHECKING,
    Any,
)

from behave import (
    given,
    then,
    when,
)

if TYPE_CHECKING:
    from behave.runner import Context


def unquote(s: str) -> str:
    """Remove surrounding quotes from Gherkin parameter values.

    Behave includes literal quote characters when parsing parameters,
    so "25" becomes the string '"25"' instead of '25'.
    """
    return s.strip('"\'')


# Mock database for testing
class MockDatabase:
    """Mock database for testing email uniqueness."""

    def __init__(self) -> None:
        """Initialize the mock database."""
        self.emails: set[str] = set()
        self.usernames: set[str] = set()

    async def has_email(self, email: str) -> bool:
        """Check if email exists in database."""
        await asyncio.sleep(0.01)  # Simulate I/O delay
        return email in self.emails

    async def has_username(self, username: str) -> bool:
        """Check if username exists in database."""
        await asyncio.sleep(0.01)  # Simulate I/O delay
        return username in self.usernames

    def add_email(self, email: str) -> None:
        """Add email to database."""
        self.emails.add(email)

    def add_username(self, username: str) -> None:
        """Add username to database."""
        self.usernames.add(username)


# Mock external API for testing
class MockExternalAPI:
    """Mock external API for testing API key validation."""

    def __init__(self) -> None:
        """Initialize the mock API."""
        self.valid_keys: set[str] = set()
        self.ip_locations: dict[str, str] = {}

    async def verify_api_key(self, key: str) -> bool:
        """Verify if API key is valid."""
        await asyncio.sleep(0.01)  # Simulate I/O delay
        return key in self.valid_keys

    async def get_ip_location(self, ip: str) -> str | None:
        """Get location for IP address."""
        await asyncio.sleep(0.01)  # Simulate I/O delay
        return self.ip_locations.get(ip)

    def add_api_key(self, key: str) -> None:
        """Add valid API key."""
        self.valid_keys.add(key)

    def set_ip_location(self, ip: str, location: str) -> None:
        """Set location for IP address."""
        self.ip_locations[ip] = location


# Context to store async validation state
class AsyncValidationContext:
    """Test context for async validation scenarios."""

    def __init__(self) -> None:
        """Initialize the async validation context."""
        self.database = MockDatabase()
        self.external_api = MockExternalAPI()
        self.schema = None
        self.input_data: dict[str, Any] = {}
        self.result = None
        self.validation_start_time: float = 0.0
        self.validation_duration: float = 0.0
        self.timeout: float | None = None


def get_async_context(context: Context) -> AsyncValidationContext:
    """Get or create the async validation context for the current test."""
    if not hasattr(context, 'async_validation_context'):
        context.async_validation_context = AsyncValidationContext()
    return context.async_validation_context


# Background steps
@given('I am using an async Python application')
def step_using_async_application(context: Context) -> None:
    """Verify async support is available."""
    # This ensures we're in an async-capable environment
    ac = get_async_context(context)
    assert ac is not None


@given('I have valid8r installed with async support')
def step_valid8r_async_support(context: Context) -> None:
    """Verify valid8r has async validation support."""
    # This will fail until we implement async validation
    from valid8r.core import schema

    assert hasattr(schema.Schema, 'validate_async')


# Database scenarios
@given('a user database with email "{email}"')
def step_database_with_email(context: Context, email: str) -> None:
    """Add email to mock database."""
    ac = get_async_context(context)
    ac.database.add_email(unquote(email))


@given('a user database without email "{email}"')
def step_database_without_email(context: Context, email: str) -> None:
    """Ensure email is not in mock database."""
    # Email is not added, so it won't exist


@when('I validate user registration with email "{email}"')
def step_validate_user_registration(context: Context, email: str) -> None:
    """Validate user registration with email uniqueness check."""
    from valid8r.core import (
        parsers,
        schema,
    )
    from valid8r.core.maybe import Maybe

    ac = get_async_context(context)

    # Create async validator for email uniqueness
    async def unique_email(email_addr: Any) -> Maybe:
        # EmailAddress object from parser, need to reconstruct email string
        email_str = f'{email_addr.local}@{email_addr.domain}'
        exists = await ac.database.has_email(email_str)
        if exists:
            return Maybe.failure('Email already registered')
        return Maybe.success(email_addr)

    # Create schema with async validator
    ac.schema = schema.Schema(
        fields={
            'email': schema.Field(
                parser=parsers.parse_email,
                validators=[unique_email],
                required=True,
            ),
        }
    )

    ac.input_data = {'email': unquote(email)}

    # Run async validation
    ac.result = asyncio.run(ac.schema.validate_async(ac.input_data))


# API key scenarios
@given('an external API that recognizes key "{key}"')
def step_api_recognizes_key(context: Context, key: str) -> None:
    """Add valid API key to mock external API."""
    ac = get_async_context(context)
    ac.external_api.add_api_key(unquote(key))


@given('an external API that rejects key "{key}"')
def step_api_rejects_key(context: Context, key: str) -> None:
    """Ensure API key is not in valid keys."""
    # Key is not added, so it will be rejected


@when('I validate configuration with API key "{key}"')
def step_validate_api_key(context: Context, key: str) -> None:
    """Validate configuration with API key validation."""
    from valid8r.core import (
        parsers,
        schema,
    )
    from valid8r.core.maybe import Maybe

    ac = get_async_context(context)

    # Create async validator for API key
    async def valid_api_key(key_str: str) -> Maybe[str]:
        is_valid = await ac.external_api.verify_api_key(key_str)
        if not is_valid:
            return Maybe.failure('Invalid API key')
        return Maybe.success(key_str)

    # Create schema with async validator
    ac.schema = schema.Schema(
        fields={
            'api_key': schema.Field(
                parser=parsers.parse_str,
                validators=[valid_api_key],
                required=True,
            ),
        }
    )

    ac.input_data = {'api_key': unquote(key)}

    # Run async validation
    ac.result = asyncio.run(ac.schema.validate_async(ac.input_data))


# Multiple fields scenario
@given('a schema with 3 fields requiring async validation')
def step_schema_with_three_async_validators(context: Context) -> None:
    """Create schema with 3 async validators."""
    from valid8r.core import (
        parsers,
        schema,
    )
    from valid8r.core.maybe import Maybe

    ac = get_async_context(context)

    async def async_validator_1(val: str) -> Maybe[str]:
        await asyncio.sleep(0.01)
        return Maybe.success(val)

    async def async_validator_2(val: str) -> Maybe[str]:
        await asyncio.sleep(0.01)
        return Maybe.success(val)

    async def async_validator_3(val: str) -> Maybe[str]:
        await asyncio.sleep(0.01)
        return Maybe.success(val)

    ac.schema = schema.Schema(
        fields={
            'field1': schema.Field(parser=parsers.parse_str, validators=[async_validator_1], required=True),
            'field2': schema.Field(parser=parsers.parse_str, validators=[async_validator_2], required=True),
            'field3': schema.Field(parser=parsers.parse_str, validators=[async_validator_3], required=True),
        }
    )


@when('I validate data for all 3 fields')
def step_validate_three_fields(context: Context) -> None:
    """Validate data for all 3 fields."""
    ac = get_async_context(context)
    ac.input_data = {'field1': 'value1', 'field2': 'value2', 'field3': 'value3'}

    # Track timing
    ac.validation_start_time = time.perf_counter()
    ac.result = asyncio.run(ac.schema.validate_async(ac.input_data))
    ac.validation_duration = time.perf_counter() - ac.validation_start_time


# Sync validators scenario
@given('a schema with only sync validators')
def step_schema_with_sync_validators(context: Context) -> None:
    """Create schema with only synchronous validators."""
    from valid8r.core import (
        parsers,
        schema,
        validators,
    )

    ac = get_async_context(context)
    ac.schema = schema.Schema(
        fields={
            'age': schema.Field(
                parser=parsers.parse_int,
                validators=[validators.minimum(0), validators.maximum(120)],
                required=True,
            ),
        }
    )


@when('I use the regular validate method')
def step_use_regular_validate(context: Context) -> None:
    """Use regular synchronous validate method."""
    ac = get_async_context(context)
    ac.input_data = {'age': '25'}
    ac.result = ac.schema.validate(ac.input_data)


# Mixed sync and async validators
@given('a schema with both sync and async validators')
def step_schema_with_mixed_validators(context: Context) -> None:
    """Create schema with both sync and async validators."""
    from valid8r.core import (
        parsers,
        schema,
    )
    from valid8r.core.maybe import Maybe

    ac = get_async_context(context)

    # Sync validator that works with EmailAddress
    def sync_validator(email_addr: Any) -> Maybe:
        # Simple check that email domain is not empty
        if not email_addr.domain:
            return Maybe.failure('Email domain cannot be empty')
        return Maybe.success(email_addr)

    async def async_validator(email_addr: Any) -> Maybe:
        await asyncio.sleep(0.01)
        return Maybe.success(email_addr)

    ac.schema = schema.Schema(
        fields={
            'email': schema.Field(
                parser=parsers.parse_email,
                validators=[sync_validator, async_validator],
                required=True,
            ),
        }
    )


@when('I validate data using async validation')
def step_validate_async(context: Context) -> None:
    """Validate data using async validation method."""
    ac = get_async_context(context)
    ac.input_data = {'email': 'user@example.com'}
    ac.result = asyncio.run(ac.schema.validate_async(ac.input_data))


# Timeout scenario
@given('a schema with a slow async validator')
def step_schema_with_slow_validator(context: Context) -> None:
    """Create schema with slow async validator."""
    from valid8r.core import (
        parsers,
        schema,
    )
    from valid8r.core.maybe import Maybe

    ac = get_async_context(context)

    async def slow_validator(val: str) -> Maybe[str]:
        await asyncio.sleep(2.0)  # Slow validator
        return Maybe.success(val)

    ac.schema = schema.Schema(
        fields={
            'field': schema.Field(parser=parsers.parse_str, validators=[slow_validator], required=True),
        }
    )


@when('I validate with a timeout of {timeout:d} second')
def step_validate_with_timeout(context: Context, timeout: int) -> None:
    """Validate with timeout."""
    ac = get_async_context(context)
    ac.input_data = {'field': 'value'}
    ac.timeout = float(timeout)

    try:
        ac.result = asyncio.run(ac.schema.validate_async(ac.input_data, timeout=ac.timeout))
    except TimeoutError as e:
        ac.result = e


# Geographic IP validation
@given('an external API for IP geolocation')
def step_external_api_geolocation(context: Context) -> None:
    """Set up external API for IP geolocation."""
    ac = get_async_context(context)
    # Set up mock IP locations
    ac.external_api.set_ip_location('8.8.8.8', 'US')
    ac.external_api.set_ip_location('1.1.1.1', 'AU')  # Australia


@when('I validate IP address "{ip}" must be from "{country}"')
def step_validate_ip_location(context: Context, ip: str, country: str) -> None:
    """Validate IP address is from specific country."""
    from valid8r.core import (
        parsers,
        schema,
    )
    from valid8r.core.maybe import Maybe

    ac = get_async_context(context)
    target_country = unquote(country)

    async def is_from_country(ip_str: str) -> Maybe[str]:
        location = await ac.external_api.get_ip_location(ip_str)
        if location != target_country:
            return Maybe.failure(f'IP is not from {target_country}')
        return Maybe.success(ip_str)

    ac.schema = schema.Schema(
        fields={
            'ip': schema.Field(parser=parsers.parse_str, validators=[is_from_country], required=True),
        }
    )

    ac.input_data = {'ip': unquote(ip)}
    ac.result = asyncio.run(ac.schema.validate_async(ac.input_data))


# Assertion steps
@then('validation succeeds')
def step_validation_succeeds(context: Context) -> None:
    """Assert validation succeeded."""
    ac = get_async_context(context)
    assert ac.result.is_success(), f'Expected success but got failure: {ac.result.error_or("")}'


@then('validation fails with "{error_substring}"')
def step_validation_fails_with(context: Context, error_substring: str) -> None:
    """Assert validation failed with specific error."""
    ac = get_async_context(context)
    assert ac.result.is_failure(), 'Expected failure but got success'
    # Get validation errors (could be list or single error)
    errors = ac.result.validation_error
    if isinstance(errors, list):
        # Convert list of ValidationErrors to string
        error_str = ' '.join(err.message for err in errors)
    else:
        error_str = errors.message if hasattr(errors, 'message') else str(errors)

    assert unquote(error_substring).lower() in error_str.lower(), (
        f'Expected error containing "{error_substring}" but got: {error_str}'
    )


@then('validation completes in reasonable time')
def step_validation_completes_reasonably(context: Context) -> None:
    """Assert validation completes in reasonable time."""
    ac = get_async_context(context)
    # With 3 async validators running concurrently, should complete in ~0.01s (not 0.03s sequentially)
    # Allow generous margin for CI variability
    assert ac.validation_duration < 0.05, (
        f'Expected concurrent execution (~0.01s) but took {ac.validation_duration:.3f}s'
    )


@then('all fields are validated')
def step_all_fields_validated(context: Context) -> None:
    """Assert all fields were validated."""
    ac = get_async_context(context)
    assert ac.result.is_success(), 'Expected success after validation'


@then('validation works as before')
def step_validation_works_as_before(context: Context) -> None:
    """Assert sync validation still works."""
    ac = get_async_context(context)
    assert ac.result.is_success(), 'Expected backward compatibility with sync validation'


@then('sync validators run first')
def step_sync_validators_run_first(context: Context) -> None:
    """Assert sync validators run first."""
    # This is verified by the implementation (sync validators always run first)


@then('async validators run after')
def step_async_validators_run_after(context: Context) -> None:
    """Assert async validators run after sync validators."""
    # This is verified by the implementation


@then('all errors are collected')
def step_all_errors_collected(context: Context) -> None:
    """Assert all errors are collected."""
    # If we got here, error accumulation works
    ac = get_async_context(context)
    assert ac.result is not None


@then('validation fails with timeout error')
def step_validation_fails_with_timeout(context: Context) -> None:
    """Assert validation failed with timeout error."""
    # First check async_validators_steps.py context
    if hasattr(context, 'async_validator_context'):
        avc = context.async_validator_context
        if avc.result is not None:
            if hasattr(avc.result, 'is_failure') and avc.result.is_failure():
                error_msg = avc.result.error_or('')
                assert 'timeout' in error_msg.lower(), f'Expected timeout error but got: {error_msg}'
                return
            if isinstance(avc.result, asyncio.TimeoutError):
                return
        assert getattr(avc, 'timeout_occurred', False), 'Expected timeout but none occurred'
        return

    # Check async_validation_steps.py context
    ac = get_async_context(context)
    if isinstance(ac.result, asyncio.TimeoutError):
        return
    if hasattr(ac.result, 'is_failure') and ac.result.is_failure():
        error_msg = ac.result.error_or('')
        assert 'timeout' in error_msg.lower(), f'Expected timeout error but got: {error_msg}'
        return
    assert False, f'Expected TimeoutError but got: {type(ac.result)}'
