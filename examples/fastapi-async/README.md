# FastAPI + valid8r Async Validation Example

This example demonstrates how to integrate valid8r with FastAPI for comprehensive request validation, including:

- **Request body validation** using Pydantic models with valid8r field validators
- **Query parameter validation** with Maybe pattern matching
- **Request header validation** for authentication and authorization
- **Structured error responses** with actionable feedback
- **Performance-optimized validation** patterns

## Features

### Request Body Validation

Validate complex request bodies with type-safe parsers:

```python
class UserCreate(BaseModel):
    email: EmailAddress
    age: int

    @field_validator('email', mode='before')
    @classmethod
    def validate_email(cls, v):
        return validator_from_parser(
            parsers.parse_email,
            error_prefix='Email'
        )(v)
```

### Query Parameter Validation

Validate query parameters with clear error messages:

```python
@app.get('/users/')
async def list_users(
    email: Optional[str] = Query(None)
):
    if email:
        result = parsers.parse_email(email)
        match result:
            case Success(parsed):
                email_filter = f'{parsed.local}@{parsed.domain}'
            case Failure(error):
                raise HTTPException(status_code=400, detail=error)
```

### Header Validation

Validate authentication headers and custom headers:

```python
@app.get('/protected/')
async def protected(
    authorization: Optional[str] = Header(None)
):
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='Invalid auth')

    token = authorization[7:]
    result = parsers.parse_uuid(token)
    match result:
        case Success(uuid):
            return {'authenticated': True}
        case Failure(error):
            raise HTTPException(status_code=401, detail=error)
```

## Installation

```bash
# From the project root
cd examples/fastapi-async

# Install dependencies using uv
uv pip install -r requirements.txt

# Or install directly
pip install fastapi uvicorn pydantic valid8r
```

## Running the Example

### Development Server

```bash
# From the examples/fastapi-async directory
uv run uvicorn app:app --reload

# Or from the project root
uv run uvicorn examples.fastapi-async.app:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

### Production Server

```bash
# Using uvicorn with multiple workers
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4

# Using gunicorn with uvicorn workers
gunicorn app:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Testing the API

### Create User (Request Body Validation)

```bash
# Valid request
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30,
    "website": "https://example.com"
  }'

# Response (201 Created)
{
  "name": "John Doe",
  "email": "john@example.com",
  "age": 30,
  "website": "https://example.com/"
}
```

```bash
# Invalid email
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "not-an-email",
    "age": 30
  }'

# Response (422 Unprocessable Entity)
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "email"],
      "msg": "Email: Must be a valid email address",
      "input": "not-an-email"
    }
  ]
}
```

### List Users (Query Parameter Validation)

```bash
# Valid request with email filter
curl "http://localhost:8000/users/?page=1&limit=10&email=john@example.com"

# Response (200 OK)
{
  "page": 1,
  "limit": 10,
  "email_filter": "john@example.com",
  "users": [],
  "total": 0
}
```

```bash
# Invalid email parameter
curl "http://localhost:8000/users/?email=invalid-email"

# Response (400 Bad Request)
{
  "detail": {
    "error": "Invalid email parameter",
    "message": "Must be a valid email address",
    "parameter": "email",
    "received": "invalid-email"
  }
}
```

### Protected Resource (Header Validation)

```bash
# Valid authorization header
curl http://localhost:8000/protected/ \
  -H "Authorization: Bearer 550e8400-e29b-41d4-a716-446655440000"

# Response (200 OK)
{
  "authenticated": true,
  "token": "550e8400...",
  "message": "Access granted"
}
```

```bash
# Missing authorization header
curl http://localhost:8000/protected/

# Response (401 Unauthorized)
{
  "detail": {
    "error": "Authorization required",
    "message": "Authorization header must be provided"
  }
}
```

```bash
# Invalid token format
curl http://localhost:8000/protected/ \
  -H "Authorization: Bearer invalid-token"

# Response (401 Unauthorized)
{
  "detail": {
    "error": "Invalid token",
    "message": "Must be a valid UUID",
    "hint": "Token must be a valid UUID"
  }
}
```

### Create Product (Price Validation)

```bash
# Valid request
curl -X POST http://localhost:8000/products/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Widget",
    "price": 19.99,
    "quantity": 100
  }'

# Response (201 Created)
{
  "name": "Widget",
  "price": 19.99,
  "quantity": 100,
  "sku": "SKU-WIDGET"
}
```

## Project Structure

```
examples/fastapi-async/
├── app.py              # Main FastAPI application
├── models.py           # Pydantic models with valid8r validators
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Key Patterns

### Pattern 1: Pydantic Field Validation

Use `validator_from_parser` to integrate valid8r parsers with Pydantic:

```python
from valid8r.integrations.pydantic import validator_from_parser

@field_validator('email', mode='before')
@classmethod
def validate_email(cls, v):
    return validator_from_parser(
        parsers.parse_email,
        error_prefix='Email'
    )(v)
```

### Pattern 2: Maybe Pattern Matching

Use pattern matching for explicit error handling:

```python
match parsers.parse_email(value):
    case Success(email):
        # Handle success
        return email
    case Failure(error):
        # Handle error
        raise HTTPException(status_code=400, detail=error)
```

### Pattern 3: Structured Error Responses

Return detailed error information for better client experience:

```python
raise HTTPException(
    status_code=400,
    detail={
        'error': 'Invalid email parameter',
        'message': error,
        'parameter': 'email',
        'received': email
    }
)
```

## Performance Considerations

- **Synchronous validation** is used for CPU-bound operations (parsing, regex)
- **Async endpoints** allow handling many concurrent requests efficiently
- **Validation overhead**: ~10-50 microseconds per field validation
- **FastAPI + Pydantic + valid8r**: Minimal performance impact

For more details, see the [Performance section](../../docs/guides/fastapi-async-validation.md#performance-considerations) in the full guide.

## Next Steps

- Read the [complete guide](../../docs/guides/fastapi-async-validation.md)
- Explore [models.py](./models.py) for more validation patterns
- Check out the [async validation guide](../../docs/guides/async-validation.md)
- Visit the [interactive API docs](http://localhost:8000/docs) when running locally

## Troubleshooting

### Import Errors

If you see import errors, ensure valid8r is installed:

```bash
uv pip install valid8r
# or
pip install valid8r
```

### Type Checking Errors

The examples use structured types like `EmailAddress` which may cause type checker warnings. These are expected and can be ignored with `# type: ignore[valid-type]` comments (already included in the code).

### Port Already in Use

If port 8000 is already in use:

```bash
# Use a different port
uvicorn app:app --port 8001
```

## License

This example is part of the valid8r project and uses the same license.
