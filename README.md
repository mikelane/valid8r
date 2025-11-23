
### Async Validation

Validate data using async validators for I/O-bound operations like database checks, API calls, and external service validation:

```python
import asyncio
from valid8r.core import parsers, schema, validators
from valid8r.core.maybe import Success, Failure

# Define async validator
async def check_email_unique(email: str) -> Maybe[str]:
    """Check if email is unique in database."""
    # Simulate database query
    await asyncio.sleep(0.1)
    existing_emails = {'admin@example.com', 'user@example.com'}

    if email in existing_emails:
        return Maybe.failure('Email already registered')
    return Maybe.success(email)

# Create schema with async validators
user_schema = schema.Schema(fields={
    'email': schema.Field(
        parser=parsers.parse_email,
        validators=[
            validators.min_length(1),  # Sync validator (fail-fast)
            check_email_unique,  # Async validator (database check)
        ],
        required=True
    ),
    'username': schema.Field(
        parser=parsers.parse_str,
        validators=[
            validators.matches_pattern(r'^[a-z0-9_]+$'),
            check_username_available,  # Another async validator
        ],
        required=True
    ),
})

# Validate asynchronously with timeout
async def main():
    result = await user_schema.validate_async(
        {'email': 'new@example.com', 'username': 'newuser'},
        timeout=5.0
    )

    match result:
        case Success(data):
            print(f"Valid: {data}")
        case Failure(errors):
            for error in errors:
                print(f"{error.path}: {error.message}")

asyncio.run(main())
```

**Key Features:**

- Concurrent execution of async validators across fields for better performance
- Mixed sync and async validators (sync runs first for fail-fast behavior)
- Configurable timeout support to prevent hanging on slow operations
- Full error accumulation across all fields
- Works seamlessly with existing sync validators

**Common Use Cases:**

- Database uniqueness checks (email, username)
- External API validation (API keys, payment methods)
- Geolocation constraints (IP address country verification)
- Remote file access validation
- Any I/O-bound validation operation

See the [Async Validation Guide](https://valid8r.readthedocs.io/en/latest/user_guide/async_validation.html) for comprehensive examples including database integration, API validation, and performance optimization patterns.


### Async Validation

Validate data using async validators for I/O-bound operations like database checks, API calls, and external service validation:

```python
import asyncio
from valid8r.core import parsers, schema, validators
from valid8r.core.maybe import Success, Failure

# Define async validator
async def check_email_unique(email: str) -> Maybe[str]:
    """Check if email is unique in database."""
    # Simulate database query
    await asyncio.sleep(0.1)
    existing_emails = {'admin@example.com', 'user@example.com'}

    if email in existing_emails:
        return Maybe.failure('Email already registered')
    return Maybe.success(email)

# Create schema with async validators
user_schema = schema.Schema(fields={
    'email': schema.Field(
        parser=parsers.parse_email,
        validators=[
            validators.min_length(1),  # Sync validator (fail-fast)
            check_email_unique,  # Async validator (database check)
        ],
        required=True
    ),
    'username': schema.Field(
        parser=parsers.parse_str,
        validators=[
            validators.matches_pattern(r'^[a-z0-9_]+$'),
            check_username_available,  # Another async validator
        ],
        required=True
    ),
})

# Validate asynchronously with timeout
async def main():
    result = await user_schema.validate_async(
        {'email': 'new@example.com', 'username': 'newuser'},
        timeout=5.0
    )

    match result:
        case Success(data):
            print(f"Valid: {data}")
        case Failure(errors):
            for error in errors:
                print(f"{error.path}: {error.message}")

asyncio.run(main())
```

**Key Features:**

- Concurrent execution of async validators across fields for better performance
- Mixed sync and async validators (sync runs first for fail-fast behavior)
- Configurable timeout support to prevent hanging on slow operations
- Full error accumulation across all fields
- Works seamlessly with existing sync validators

**Common Use Cases:**

- Database uniqueness checks (email, username)
- External API validation (API keys, payment methods)
- Geolocation constraints (IP address country verification)
- Remote file access validation
- Any I/O-bound validation operation

See the [Async Validation Guide](https://valid8r.readthedocs.io/en/latest/user_guide/async_validation.html) for comprehensive examples including database integration, API validation, and performance optimization patterns.
