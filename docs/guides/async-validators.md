# Async Validators Guide

This guide covers the async validator library in valid8r, which provides non-blocking validators for I/O-bound validation operations.

## Overview

Async validators enable efficient validation against external systems (databases, APIs, DNS) without blocking the event loop. They follow the same Maybe monad pattern as synchronous validators, making them composable and easy to integrate into existing validation pipelines.

## Key Features

- **Non-blocking**: All validators use async/await for efficient I/O
- **Maybe monad**: Returns `Success[T]` or `Failure[T]` for composable error handling
- **Database validation**: Check uniqueness and foreign key constraints
- **Type-safe**: Full type annotations and mypy compliance

## Installation

The async validators module is included with valid8r:

```bash
pip install valid8r
```

For database validation, you'll also need an async database library:

```bash
# PostgreSQL
pip install asyncpg

# MySQL
pip install aiomysql

# SQLite
pip install aiosqlite
```

## Database Validators (MVP)

### `unique_in_db` - Uniqueness Validation

Validates that a value is unique in a database table. Use this for checking email addresses, usernames, or any field that must be unique.

**Example:**

```python
import asyncio
import asyncpg
from valid8r.async_validators import unique_in_db

async def register_user(email: str):
    # Connect to database
    conn = await asyncpg.connect('postgresql://localhost/mydb')

    # Create validator
    email_validator = await unique_in_db(
        field='email',
        table='users',
        connection=conn
    )

    # Validate email uniqueness
    result = await email_validator(email)

    match result:
        case Success(value):
            print(f"Email {value} is available!")
            # Proceed with user registration
        case Failure(error):
            print(f"Email is taken: {error}")

    await conn.close()

asyncio.run(register_user('new@example.com'))
```

**Parameters:**
- `field` (str): Database column to check (e.g., 'email', 'username')
- `table` (str): Database table to query (e.g., 'users', 'accounts')
- `connection` (Any): Async database connection with `execute()` method

**Returns:**
- `Success(value)` if the value is unique
- `Failure(error_msg)` if the value already exists or database error occurs

### `exists_in_db` - Foreign Key Validation

Validates that a value exists in a database table. Use this for validating foreign keys or ensuring referenced entities exist.

**Example:**

```python
import asyncio
import asyncpg
from valid8r.async_validators import exists_in_db

async def create_product(category_id: str):
    # Connect to database
    conn = await asyncpg.connect('postgresql://localhost/mydb')

    # Create validator
    category_validator = await exists_in_db(
        field='id',
        table='categories',
        connection=conn
    )

    # Validate that category exists
    result = await category_validator(category_id)

    match result:
        case Success(value):
            print(f"Category {value} exists")
            # Proceed with product creation
        case Failure(error):
            print(f"Invalid category: {error}")

    await conn.close()

asyncio.run(create_product('electronics'))
```

**Parameters:**
- `field` (str): Database column to check (e.g., 'id', 'category_id')
- `table` (str): Database table to query (e.g., 'categories', 'products')
- `connection` (Any): Async database connection with `execute()` method

**Returns:**
- `Success(value)` if the value exists
- `Failure(error_msg)` if the value doesn't exist or database error occurs

## Usage Patterns

### Concurrent Validation

Validate multiple values in parallel for maximum efficiency:

```python
async def validate_batch(emails: list[str]):
    conn = await asyncpg.connect('postgresql://localhost/mydb')
    validator = await unique_in_db(field='email', table='users', connection=conn)

    # Run validations concurrently
    results = await asyncio.gather(*[validator(email) for email in emails])

    # Process results
    for email, result in zip(emails, results, strict=False):
        if result.is_success():
            print(f"{email}: Available")
        else:
            print(f"{email}: {result.error_or('')}")

    await conn.close()
```

### Integration with Async Frameworks

Async validators work seamlessly with FastAPI, aiohttp, and other async frameworks:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncpg

app = FastAPI()

class UserRegistration(BaseModel):
    email: str
    password: str

@app.post("/register")
async def register(user: UserRegistration):
    conn = await asyncpg.connect('postgresql://localhost/mydb')

    # Validate email uniqueness
    validator = await unique_in_db(field='email', table='users', connection=conn)
    result = await validator(user.email)

    if result.is_failure():
        await conn.close()
        raise HTTPException(status_code=400, detail=result.error_or(''))

    # Create user...
    await conn.close()
    return {"message": "User registered successfully"}
```

### Error Handling

All async validators catch database errors and return them as `Failure` results:

```python
# Database connection fails
validator = await unique_in_db(field='email', table='users', connection=bad_conn)
result = await validator('test@example.com')

if result.is_failure():
    error = result.error_or('')
    if 'Database error' in error:
        # Handle database connection issues
        print("Database unavailable, try again later")
```

## Database Compatibility

The async validators are compatible with any async database library that provides:
- An `execute()` method that accepts a query string and parameters
- A result object with a `scalar()` method

**Tested with:**
- `asyncpg` (PostgreSQL)
- `aiomysql` (MySQL)
- `aiosqlite` (SQLite)

## Performance Considerations

1. **Connection Pooling**: Use connection pools for production applications
2. **Query Optimization**: Ensure indexed columns for uniqueness checks
3. **Concurrent Limits**: Use `asyncio.Semaphore` to limit concurrent database queries
4. **Timeout Handling**: Wrap validators with `asyncio.wait_for()` for timeout control

Example with timeout:

```python
try:
    result = await asyncio.wait_for(
        validator('test@example.com'),
        timeout=5.0  # 5 second timeout
    )
except asyncio.TimeoutError:
    print("Validation timed out")
```

## Validator Composition

Valid8r provides powerful composition functions to combine multiple async validators into complex validation pipelines.

### `all_of` - Parallel AND Composition

Runs all validators in parallel. All must succeed for validation to pass.

```python
import asyncio
from valid8r.async_validators import all_of
from valid8r.core.maybe import Maybe

async def check_length(value: str) -> Maybe[str]:
    if len(value) >= 3:
        return Maybe.success(value)
    return Maybe.failure('Too short')

async def check_alpha(value: str) -> Maybe[str]:
    if value.isalpha():
        return Maybe.success(value)
    return Maybe.failure('Must be alphabetic')

async def check_not_reserved(value: str) -> Maybe[str]:
    reserved = ['admin', 'root', 'system']
    if value.lower() not in reserved:
        return Maybe.success(value)
    return Maybe.failure('Reserved word')

async def validate_username(username: str):
    # All three validators run in parallel
    validator = all_of(check_length, check_alpha, check_not_reserved)
    result = await validator(username)

    if result.is_success():
        print(f"Username '{result.value_or('')}' is valid!")
    else:
        print(f"Validation failed: {result.error_or('')}")

asyncio.run(validate_username('JohnDoe'))
```

**Parameters:**
- `*validators`: Variable number of async validators
- `fail_fast` (bool): If `True` (default), returns first error. If `False`, collects all errors.

**With error aggregation:**
```python
# Collect all errors when fail_fast=False
validator = all_of(check_length, check_alpha, fail_fast=False)
result = await validator('x1')
# Error: "Too short; Must be alphabetic"
```

### `any_of` - Parallel OR Composition

Runs all validators in parallel. At least one must succeed.

```python
import asyncio
from valid8r.async_validators import any_of
from valid8r.core.maybe import Maybe

async def check_email_format(value: str) -> Maybe[str]:
    if '@' in value and '.' in value.split('@')[-1]:
        return Maybe.success(value)
    return Maybe.failure('Not a valid email')

async def check_phone_format(value: str) -> Maybe[str]:
    digits = ''.join(c for c in value if c.isdigit())
    if len(digits) >= 10:
        return Maybe.success(value)
    return Maybe.failure('Not a valid phone number')

async def validate_contact(contact: str):
    # Either email OR phone format is acceptable
    validator = any_of(check_email_format, check_phone_format)
    result = await validator(contact)

    if result.is_success():
        print(f"Contact '{result.value_or('')}' is valid!")
    else:
        print(f"Validation failed: {result.error_or('')}")

asyncio.run(validate_contact('user@example.com'))  # Valid as email
asyncio.run(validate_contact('555-123-4567'))      # Valid as phone
```

**Notes:**
- Empty validator list returns Failure (nothing can succeed)
- Returns the first successful result's value

### `sequence` - Sequential Composition

Runs validators one after another, passing each result to the next. Stops on first failure.

```python
import asyncio
from valid8r.async_validators import sequence
from valid8r.core.maybe import Maybe

async def trim_whitespace(value: str) -> Maybe[str]:
    return Maybe.success(value.strip())

async def to_lowercase(value: str) -> Maybe[str]:
    return Maybe.success(value.lower())

async def validate_not_empty(value: str) -> Maybe[str]:
    if value:
        return Maybe.success(value)
    return Maybe.failure('Value cannot be empty')

async def check_unique_in_db(value: str) -> Maybe[str]:
    # Simulating database check
    existing = ['admin', 'user', 'test']
    if value not in existing:
        return Maybe.success(value)
    return Maybe.failure(f'Username "{value}" already exists')

async def process_username(raw_input: str):
    # Each validator transforms and passes to the next
    validator = sequence(
        trim_whitespace,
        to_lowercase,
        validate_not_empty,
        check_unique_in_db
    )

    result = await validator(raw_input)

    if result.is_success():
        print(f"Processed username: {result.value_or('')}")
    else:
        print(f"Processing failed: {result.error_or('')}")

asyncio.run(process_username('  JohnDoe  '))  # -> 'johndoe'
```

**Key difference from `all_of`:**
- Runs sequentially, not in parallel
- Each validator receives the output of the previous one
- Use when validators have dependencies or transform data

### Mixed Composition

Combine composition types for complex validation logic:

```python
import asyncio
from valid8r.async_validators import all_of, any_of, sequence
from valid8r.core.maybe import Maybe

# Define individual validators
async def check_min_length(value: str) -> Maybe[str]:
    if len(value) >= 8:
        return Maybe.success(value)
    return Maybe.failure('Must be at least 8 characters')

async def check_has_digit(value: str) -> Maybe[str]:
    if any(c.isdigit() for c in value):
        return Maybe.success(value)
    return Maybe.failure('Must contain a digit')

async def check_has_uppercase(value: str) -> Maybe[str]:
    if any(c.isupper() for c in value):
        return Maybe.success(value)
    return Maybe.failure('Must contain uppercase')

async def check_has_special(value: str) -> Maybe[str]:
    special = '!@#$%^&*'
    if any(c in special for c in value):
        return Maybe.success(value)
    return Maybe.failure('Must contain special character')

async def hash_password(value: str) -> Maybe[str]:
    # Simulated hashing
    return Maybe.success(f'hashed_{value}')

async def validate_password(password: str):
    # Complex validation: all requirements + hashing
    validator = sequence(
        # First: validate all password requirements (parallel)
        all_of(
            check_min_length,
            check_has_digit,
            check_has_uppercase,
            check_has_special,
            fail_fast=False  # Collect all missing requirements
        ),
        # Then: hash the valid password
        hash_password
    )

    result = await validator(password)

    if result.is_success():
        print(f"Password valid and hashed: {result.value_or('')}")
    else:
        print(f"Password requirements not met: {result.error_or('')}")

asyncio.run(validate_password('MyP@ss123'))  # Valid
asyncio.run(validate_password('weak'))       # All errors listed
```

### Performance Comparison

| Function | Execution | Use Case |
|----------|-----------|----------|
| `all_of` | Parallel | Independent checks, all must pass |
| `any_of` | Parallel | Alternative formats, one must pass |
| `sequence` | Sequential | Dependent validators, data transformation |

**Timing example with 3 validators, each taking 0.1s:**
- `all_of`: ~0.1s (parallel)
- `any_of`: ~0.1s (parallel)
- `sequence`: ~0.3s (sequential)

## Future Features

This module continues to evolve. Upcoming features include:

- **More validators**: Additional API validators and service integrations
- **Enhanced caching**: TTL-based caching with invalidation
- **Circuit breaker**: Prevent cascade failures in external services

## Examples

Complete working examples are available in `examples/async-validation/`:

- `database_example.py`: Database validation examples with mock connection

## Troubleshooting

### "Database error: connection refused"
Ensure your database is running and the connection string is correct.

### "Query takes too long"
Check that your database columns are indexed, especially for uniqueness checks.

### "AttributeError: 'Connection' object has no attribute 'execute'"
Verify you're using an async database library (not sync). Use `asyncpg` not `psycopg2`.

## Related Documentation

- [Maybe Monad Pattern](../core/maybe.md)
- [Validator Composition](../core/validators.md)
- [Database Integration Examples](../../examples/async-validation/)

## Support

For questions or issues:
- GitHub Issues: https://github.com/mikelane/valid8r/issues
- Documentation: https://valid8r.readthedocs.io
