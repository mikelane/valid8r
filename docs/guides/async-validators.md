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

## Future Features

This MVP release includes database validators only. Future releases will add:

- **API Validators**: Validate API keys and OAuth tokens
- **Email Deliverability**: Check MX records and SMTP validation
- **Rate Limiting**: Built-in rate limiting for external service calls
- **Retry Logic**: Exponential backoff for transient failures
- **Validator Composition**: Parallel and sequential validator chaining
- **Caching**: Reduce redundant external calls with TTL-based caching

See the GitHub milestones for upcoming features.

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
