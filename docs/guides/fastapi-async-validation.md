# FastAPI Async Validation Guide

This guide demonstrates how to integrate valid8r with FastAPI to build robust, type-safe REST APIs with comprehensive validation for request bodies, query parameters, and headers.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Request Body Validation](#request-body-validation)
- [Query Parameter Validation](#query-parameter-validation)
- [Request Header Validation](#request-header-validation)
- [Error Handling](#error-handling)
- [Performance Considerations](#performance-considerations)
- [Complete Example](#complete-example)

## Prerequisites

- Python 3.9+
- FastAPI installed (`pip install fastapi`)
- uvicorn for running the server (`pip install uvicorn`)
- valid8r with async support

## Installation

```bash
# Install valid8r with async support
pip install valid8r

# Install FastAPI and dependencies
pip install fastapi uvicorn
```

## Quick Start

valid8r integrates seamlessly with FastAPI through Pydantic validation. The key pattern is using `validator_from_parser` to convert valid8r parsers into Pydantic field validators:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from valid8r.core import parsers, validators
from valid8r.integrations.pydantic import validator_from_parser

app = FastAPI()

class UserCreate(BaseModel):
    email: str
    age: int

    @field_validator('email', mode='before')
    @classmethod
    def validate_email(cls, v):
        return validator_from_parser(
            parsers.parse_email,
            error_prefix='Email'
        )(v)

    @field_validator('age', mode='before')
    @classmethod
    def validate_age(cls, v):
        def age_parser(value):
            if isinstance(value, int):
                return validators.between(0, 120)(value)
            return parsers.parse_int(value).bind(
                validators.between(0, 120)
            )
        return validator_from_parser(age_parser, error_prefix='Age')(v)

@app.post('/users/', status_code=201)
def create_user(user: UserCreate):
    return {'email': user.email, 'age': user.age}
```

## Request Body Validation

FastAPI automatically validates request bodies using Pydantic models. valid8r enhances this with powerful parsers and validators that return `Maybe[T]` results.

### Basic Request Body Validation

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from typing import Any
from valid8r.core import parsers, validators
from valid8r.core.maybe import Maybe, Success, Failure
from valid8r.integrations.pydantic import validator_from_parser

app = FastAPI()

class ProductCreate(BaseModel):
    """Product creation request."""
    name: str
    price: float
    quantity: int
    url: str | None = None

    @field_validator('price', mode='before')
    @classmethod
    def validate_price(cls, v: Any):
        """Validate price is positive and reasonable."""
        def price_parser(value: Any):
            if isinstance(value, (int, float)):
                return validators.minimum(0.0)(value)
            return parsers.parse_float(value).bind(
                validators.minimum(0.0)
            )
        return validator_from_parser(price_parser, error_prefix='Price')(v)

    @field_validator('url', mode='before')
    @classmethod
    def validate_url(cls, v: Any):
        """Validate URL format if provided."""
        if v is None:
            return None
        return validator_from_parser(
            parsers.parse_url,
            error_prefix='URL'
        )(v)

@app.post('/products/', status_code=201)
async def create_product(product: ProductCreate):
    """Create a new product with validated fields."""
    return {
        'name': product.name,
        'price': product.price,
        'quantity': product.quantity,
        'url': str(product.url) if product.url else None
    }
```

### Invalid Requests Are Rejected Automatically

When validation fails, FastAPI automatically returns a **422 Unprocessable Entity** response with detailed error information:

```bash
# Invalid request
curl -X POST http://localhost:8000/products/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Widget", "price": "-10", "quantity": "5"}'

# Response (422 status code)
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "price"],
      "msg": "Price: must be at least 0",
      "input": "-10"
    }
  ]
}
```

### Clients Receive Clear Error Messages

The `validator_from_parser` function with `error_prefix` ensures error messages are clear and actionable:

```python
# When using Failure from Maybe
result = parsers.parse_email("invalid-email")
match result:
    case Success(email):
        # Process valid email
        pass
    case Failure(error):
        # Error message: "Must be a valid email address"
        raise HTTPException(status_code=400, detail=error)
```

### Valid Requests Proceed to Handler

When validation succeeds, the `Success` case extracts the validated value and passes it to your endpoint handler:

```python
@app.post('/validate/')
async def validate_data(raw_data: dict):
    """Manually validate request data using Maybe pattern matching."""
    email_result = parsers.parse_email(raw_data.get('email'))

    match email_result:
        case Success(email):
            # Valid email - proceed with business logic
            return {'email': f'{email.local}@{email.domain}', 'valid': True}
        case Failure(error):
            # Invalid email - return 400 error
            raise HTTPException(status_code=400, detail=error)
```

## Query Parameter Validation

Query parameters in FastAPI can be validated using dependency injection with valid8r parsers.

### Basic Query Parameter Validation

```python
from fastapi import FastAPI, HTTPException, Query
from typing import Optional
from valid8r.core import parsers, validators
from valid8r.core.maybe import Success, Failure

app = FastAPI()

@app.get('/users/')
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    email: Optional[str] = Query(None)
):
    """List users with pagination and optional email filter."""

    # Validate email if provided
    if email:
        email_result = parsers.parse_email(email)
        match email_result:
            case Success(parsed_email):
                email_filter = f'{parsed_email.local}@{parsed_email.domain}'
            case Failure(error):
                raise HTTPException(
                    status_code=400,
                    detail=f'Invalid email parameter: {error}'
                )
    else:
        email_filter = None

    return {
        'page': page,
        'limit': limit,
        'email_filter': email_filter,
        'users': []  # Your database query here
    }
```

### Missing Parameters Are Handled Gracefully

Use FastAPI's `Optional` type and default values to handle missing parameters:

```python
from typing import Optional

@app.get('/search/')
async def search(
    query: str = Query(...),  # Required - will return 422 if missing
    sort_by: Optional[str] = Query(None),  # Optional with None default
    page: int = Query(1, ge=1)  # Optional with default value
):
    """Search with required and optional parameters."""
    return {
        'query': query,
        'sort_by': sort_by or 'relevance',
        'page': page
    }
```

### Invalid Parameter Values Are Rejected

Combine FastAPI's built-in validation with valid8r for comprehensive parameter validation:

```python
@app.get('/products/')
async def get_products(
    min_price: Optional[str] = Query(None),
    max_price: Optional[str] = Query(None)
):
    """Get products with optional price range filtering."""

    # Validate min_price if provided
    if min_price:
        min_result = parsers.parse_float(min_price).bind(
            validators.minimum(0.0)
        )
        match min_result:
            case Success(value):
                min_price_value = value
            case Failure(error):
                raise HTTPException(
                    status_code=400,
                    detail=f'Invalid min_price: {error}'
                )
    else:
        min_price_value = 0.0

    # Similar validation for max_price...

    return {'min_price': min_price_value, 'products': []}
```

### Error Messages Explain What Went Wrong

Always provide context in error messages so clients understand what went wrong:

```python
@app.get('/items/{item_id}')
async def get_item(item_id: str, quantity: Optional[str] = Query(None)):
    """Get item with optional quantity parameter."""

    if quantity:
        qty_result = parsers.parse_int(quantity).bind(
            validators.between(1, 1000)
        )
        match qty_result:
            case Success(value):
                quantity_value = value
            case Failure(error):
                # Provide clear, actionable error message
                raise HTTPException(
                    status_code=400,
                    detail={
                        'error': 'Invalid quantity parameter',
                        'message': error,
                        'parameter': 'quantity',
                        'received': quantity
                    }
                )

    return {'item_id': item_id, 'quantity': quantity_value}
```

## Request Header Validation

Headers often contain authentication tokens, API keys, or custom metadata that requires validation.

### Basic Header Validation

```python
from fastapi import FastAPI, HTTPException, Header
from typing import Optional
from valid8r.core import parsers
from valid8r.core.maybe import Success, Failure

app = FastAPI()

@app.get('/protected/')
async def protected_resource(
    authorization: Optional[str] = Header(None)
):
    """Protected endpoint requiring authentication."""

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail='Authorization header required'
        )

    # Extract token from "Bearer <token>" format
    if not authorization.startswith('Bearer '):
        raise HTTPException(
            status_code=401,
            detail='Authorization header must use Bearer scheme'
        )

    token = authorization[7:]  # Remove "Bearer " prefix

    # Validate token format (example: UUID token)
    token_result = parsers.parse_uuid(token)
    match token_result:
        case Success(uuid_token):
            # Valid token - proceed with authentication
            return {'token': str(uuid_token), 'authenticated': True}
        case Failure(error):
            raise HTTPException(
                status_code=401,
                detail=f'Invalid token format: {error}'
            )
```

### Authentication Token Verification

```python
@app.get('/api/data')
async def get_data(
    x_api_key: Optional[str] = Header(None, alias='X-API-Key')
):
    """API endpoint requiring API key in custom header."""

    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail='X-API-Key header required'
        )

    # Validate API key format (example: UUID)
    key_result = parsers.parse_uuid(x_api_key)
    match key_result:
        case Success(api_key):
            # Look up API key in database
            # For this example, we just validate format
            return {'api_key': str(api_key)[:8] + '...', 'data': []}
        case Failure(error):
            raise HTTPException(
                status_code=401,
                detail=f'Invalid API key: {error}'
            )
```

### Custom Header Format Validation

```python
@app.post('/webhook')
async def webhook_endpoint(
    x_webhook_signature: Optional[str] = Header(None, alias='X-Webhook-Signature')
):
    """Webhook endpoint with signature verification."""

    if not x_webhook_signature:
        raise HTTPException(
            status_code=401,
            detail='X-Webhook-Signature header required'
        )

    # Validate signature format (example: hex string)
    # In production, you'd verify the actual signature
    if not all(c in '0123456789abcdef' for c in x_webhook_signature.lower()):
        raise HTTPException(
            status_code=401,
            detail='Invalid signature format: must be hexadecimal'
        )

    return {'signature_verified': True}
```

### Unauthorized Requests Are Rejected Appropriately

Use appropriate HTTP status codes for authentication and authorization failures:

- **401 Unauthorized**: Missing or invalid credentials
- **403 Forbidden**: Valid credentials but insufficient permissions

```python
@app.get('/admin/users')
async def admin_users(
    authorization: Optional[str] = Header(None)
):
    """Admin-only endpoint."""

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail='Authentication required'
        )

    # Extract and validate token
    if not authorization.startswith('Bearer '):
        raise HTTPException(
            status_code=401,
            detail='Invalid authentication scheme'
        )

    token = authorization[7:]
    token_result = parsers.parse_uuid(token)

    match token_result:
        case Success(uuid_token):
            # Check if user has admin role (example)
            user_role = 'user'  # Look up from database
            if user_role != 'admin':
                raise HTTPException(
                    status_code=403,
                    detail='Insufficient permissions: admin role required'
                )
            return {'users': []}
        case Failure(error):
            raise HTTPException(
                status_code=401,
                detail=f'Invalid token: {error}'
            )
```

## Error Handling

Proper error handling ensures clients receive actionable feedback when validation fails.

### Returning Appropriate HTTP Status Codes

Use semantic HTTP status codes to indicate different error types:

```python
from fastapi import FastAPI, HTTPException
from valid8r.core import parsers
from valid8r.core.maybe import Success, Failure

app = FastAPI()

@app.post('/validate')
async def validate_input(data: dict):
    """Demonstrate different HTTP status codes for errors."""

    # 400 Bad Request - Client sent invalid data
    if 'email' not in data:
        raise HTTPException(
            status_code=400,
            detail='Email field is required'
        )

    email_result = parsers.parse_email(data['email'])
    match email_result:
        case Success(email):
            return {'email': f'{email.local}@{email.domain}'}
        case Failure(error):
            # 422 Unprocessable Entity - Validation failed
            raise HTTPException(
                status_code=422,
                detail=f'Email validation failed: {error}'
            )
```

Common status codes for validation errors:

- **400 Bad Request**: Missing required fields, malformed JSON
- **422 Unprocessable Entity**: Valid syntax but validation failed
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Authenticated but not authorized
- **500 Internal Server Error**: Unexpected server errors

### Structured Error Responses

Provide structured error responses for better client-side error handling:

```python
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    """Structured error response."""
    error: str
    message: str
    field: Optional[str] = None
    code: Optional[str] = None

@app.post('/users')
async def create_user(data: dict):
    """Create user with structured error responses."""

    email_result = parsers.parse_email(data.get('email', ''))
    match email_result:
        case Success(email):
            return {'email': f'{email.local}@{email.domain}'}
        case Failure(error):
            # Return structured error
            raise HTTPException(
                status_code=422,
                detail={
                    'error': 'Validation failed',
                    'message': error,
                    'field': 'email',
                    'code': 'INVALID_EMAIL'
                }
            )
```

### Clients Receive Actionable Feedback

Error messages should tell clients exactly what's wrong and how to fix it:

```python
@app.post('/products')
async def create_product(data: dict):
    """Create product with actionable error messages."""

    price_result = parsers.parse_float(data.get('price', '')).bind(
        validators.minimum(0.01)
    )

    match price_result:
        case Success(price):
            return {'price': price}
        case Failure(error):
            # Provide actionable guidance
            raise HTTPException(
                status_code=422,
                detail={
                    'error': 'Invalid price',
                    'message': error,
                    'field': 'price',
                    'received': data.get('price'),
                    'expected': 'A positive number greater than 0.01',
                    'examples': ['9.99', '19.95', '100.00']
                }
            )
```

## Performance Considerations

### When Is Async Validation Beneficial?

Async validation provides benefits in these scenarios:

1. **I/O-Bound Validation**: Database lookups, API calls, file operations
2. **High Concurrency**: Many simultaneous requests that would benefit from async/await
3. **External Service Integration**: Validating against external APIs or services

### Synchronous vs Async Validation Performance

For CPU-bound validation (parsing, regex, type checking), synchronous validation is often faster due to lower overhead:

**Synchronous Validation (Recommended for most cases)**:
```python
from valid8r.core import parsers

def validate_email(email: str) -> bool:
    """Fast synchronous validation."""
    result = parsers.parse_email(email)
    return result.is_success()

# Benchmark: ~10-20 microseconds per validation
```

**Async Validation (For I/O-bound operations)**:
```python
from valid8r.async_validation import validate_async

async def validate_email_with_mx_check(email: str) -> bool:
    """Async validation with MX record lookup."""
    result = await validate_async(
        parsers.parse_email,
        email,
        check_mx_record=True  # I/O-bound operation
    )
    return result.is_success()

# Benchmark: ~50-100 milliseconds (network latency)
```

### Performance Comparison

| Validation Type | Use Case | Typical Latency | Throughput |
|----------------|----------|----------------|------------|
| Sync parsing | Email format, integers, URLs | 10-50 μs | 20,000-100,000 ops/sec |
| Sync with validation | Range checks, regex patterns | 50-200 μs | 5,000-20,000 ops/sec |
| Async I/O | Database lookups, API calls | 10-100 ms | 100-1,000 ops/sec |
| Async batch | Multiple external validations | 50-500 ms | 10-100 ops/sec |

### Best Practices for Performance

1. **Use sync validation for CPU-bound operations** (parsing, regex, type checking)
2. **Use async validation for I/O-bound operations** (database, API, network)
3. **Batch async validations** when possible to reduce overhead
4. **Cache validation results** for frequently validated values
5. **Use FastAPI dependency injection** to share validators across endpoints

### Making Informed Architecture Decisions

**Choose synchronous validation when**:
- Validating request format (JSON structure, data types)
- Checking value ranges (min/max, length)
- Pattern matching (email format, phone numbers, UUIDs)
- Pure CPU-bound operations

**Choose async validation when**:
- Looking up values in database
- Calling external APIs for validation
- Checking file existence or reading files
- Performing network operations

**Recommendation**: Start with synchronous validation and only introduce async when you have I/O-bound validation requirements. Profile your application to identify actual bottlenecks before optimizing.

## Complete Example

Here's a complete FastAPI application demonstrating all validation patterns:

```python
"""Complete FastAPI + valid8r example."""
from __future__ import annotations

from typing import Optional, Any
from fastapi import FastAPI, HTTPException, Query, Header
from pydantic import BaseModel, field_validator

from valid8r.core import parsers, validators
from valid8r.core.maybe import Success, Failure
from valid8r.integrations.pydantic import validator_from_parser

app = FastAPI(title='Valid8r + FastAPI Demo', version='1.0.0')


class UserCreate(BaseModel):
    """User creation with validated fields."""
    name: str
    email: str
    age: int
    website: Optional[str] = None

    @field_validator('email', mode='before')
    @classmethod
    def validate_email(cls, v: Any):
        return validator_from_parser(
            parsers.parse_email,
            error_prefix='Email'
        )(v)

    @field_validator('age', mode='before')
    @classmethod
    def validate_age(cls, v: Any):
        def age_parser(value: Any):
            if isinstance(value, int):
                return validators.between(0, 120)(value)
            return parsers.parse_int(value).bind(
                validators.between(0, 120)
            )
        return validator_from_parser(age_parser, error_prefix='Age')(v)

    @field_validator('website', mode='before')
    @classmethod
    def validate_website(cls, v: Any):
        if v is None:
            return None
        return validator_from_parser(
            parsers.parse_url,
            error_prefix='Website'
        )(v)


@app.post('/users/', status_code=201)
async def create_user(user: UserCreate):
    """Create user with request body validation."""
    return {
        'name': user.name,
        'email': user.email,
        'age': user.age,
        'website': str(user.website) if user.website else None
    }


@app.get('/users/')
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    email: Optional[str] = Query(None)
):
    """List users with query parameter validation."""
    if email:
        email_result = parsers.parse_email(email)
        match email_result:
            case Success(parsed):
                email_filter = f'{parsed.local}@{parsed.domain}'
            case Failure(error):
                raise HTTPException(
                    status_code=400,
                    detail=f'Invalid email: {error}'
                )
    else:
        email_filter = None

    return {
        'page': page,
        'limit': limit,
        'email_filter': email_filter,
        'users': []
    }


@app.get('/protected/')
async def protected_resource(
    authorization: Optional[str] = Header(None)
):
    """Protected endpoint with header validation."""
    if not authorization:
        raise HTTPException(status_code=401, detail='Authorization required')

    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='Invalid auth scheme')

    token = authorization[7:]
    token_result = parsers.parse_uuid(token)

    match token_result:
        case Success(uuid):
            return {'authenticated': True, 'token': str(uuid)[:8] + '...'}
        case Failure(error):
            raise HTTPException(status_code=401, detail=f'Invalid token: {error}')


@app.get('/')
async def root():
    """API documentation."""
    return {
        'message': 'Valid8r + FastAPI Integration',
        'endpoints': {
            'POST /users/': 'Create user (body validation)',
            'GET /users/': 'List users (query validation)',
            'GET /protected/': 'Protected resource (header validation)',
            'GET /docs': 'Interactive API docs'
        }
    }


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
```

Run the example:
```bash
cd examples/fastapi-async
uv run uvicorn app:app --reload
```

Visit `http://localhost:8000/docs` for interactive API documentation.

## Next Steps

- Explore the [async validation guide](async-validation.md) for advanced async patterns
- Check out [examples/fastapi-async/](../../examples/fastapi-async/) for more examples
- Read the [Pydantic integration docs](../integrations/pydantic.md) for advanced use cases
- Learn about [custom validators](custom-validators.md) for domain-specific validation
