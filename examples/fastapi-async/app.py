"""Complete FastAPI + valid8r async validation example.

This example demonstrates:
- Request body validation with Pydantic integration
- Query parameter validation with Maybe pattern
- Header validation for authentication
- Structured error responses
- Performance-optimized validation patterns

Run with:
    uv run uvicorn examples.fastapi-async.app:app --reload

Test endpoints:
    # Create user with validation
    curl -X POST http://localhost:8000/users/ \
        -H "Content-Type: application/json" \
        -d '{"name": "John Doe", "email": "john@example.com", "age": 30}'

    # List users with query parameter validation
    curl "http://localhost:8000/users/?page=1&limit=10&email=john@example.com"

    # Protected endpoint with header validation
    curl http://localhost:8000/protected/ \
        -H "Authorization: Bearer 550e8400-e29b-41d4-a716-446655440000"
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
)

from fastapi import (
    FastAPI,
    Header,
    HTTPException,
    Query,
)
from pydantic import (
    BaseModel,
    field_validator,
)

from valid8r.core import (
    parsers,
    validators,
)
from valid8r.core.maybe import (
    Failure,
    Success,
)
from valid8r.integrations.pydantic import validator_from_parser

if TYPE_CHECKING:
    from valid8r.core.parsers import (
        EmailAddress,
        UrlParts,
    )

app = FastAPI(
    title='Valid8r + FastAPI Async Validation Demo',
    version='1.0.0',
    description='Comprehensive example of FastAPI integration with valid8r validation',
)


class UserCreate(BaseModel):
    """User creation request with validated fields."""

    name: str
    email: EmailAddress  # type: ignore[valid-type]
    age: int
    website: UrlParts | None = None  # type: ignore[valid-type]

    @field_validator('email', mode='before')
    @classmethod
    def validate_email(cls, v: Any) -> EmailAddress:  # noqa: ANN401
        """Validate email format and normalize domain."""
        return validator_from_parser(parsers.parse_email, error_prefix='Email')(v)

    @field_validator('age', mode='before')
    @classmethod
    def validate_age(cls, v: Any) -> int:  # noqa: ANN401
        """Validate age is between 0 and 120."""

        def age_parser(value: Any) -> validators.Maybe[int]:  # noqa: ANN401
            # Handle both string and int inputs (FastAPI may pass either from JSON)
            if isinstance(value, int):
                return validators.between(0, 120)(value)
            return parsers.parse_int(value).bind(validators.between(0, 120))

        return validator_from_parser(age_parser, error_prefix='Age')(v)

    @field_validator('website', mode='before')
    @classmethod
    def validate_website(cls, v: Any) -> UrlParts | None:  # noqa: ANN401
        """Validate website URL format if provided."""
        if v is None:
            return None
        return validator_from_parser(parsers.parse_url, error_prefix='Website')(v)


class ProductCreate(BaseModel):
    """Product creation request with price and quantity validation."""

    name: str
    price: float
    quantity: int
    sku: str | None = None

    @field_validator('price', mode='before')
    @classmethod
    def validate_price(cls, v: Any) -> float:  # noqa: ANN401
        """Validate price is positive."""

        def price_parser(value: Any) -> validators.Maybe[float]:  # noqa: ANN401
            if isinstance(value, (int, float)):
                return validators.minimum(0.01)(value)
            return parsers.parse_float(value).bind(validators.minimum(0.01))

        return validator_from_parser(price_parser, error_prefix='Price')(v)

    @field_validator('quantity', mode='before')
    @classmethod
    def validate_quantity(cls, v: Any) -> int:  # noqa: ANN401
        """Validate quantity is positive."""

        def quantity_parser(value: Any) -> validators.Maybe[int]:  # noqa: ANN401
            if isinstance(value, int):
                return validators.minimum(1)(value)
            return parsers.parse_int(value).bind(validators.minimum(1))

        return validator_from_parser(quantity_parser, error_prefix='Quantity')(v)


@app.post('/users/', status_code=201)
async def create_user(user: UserCreate) -> dict[str, str | int]:
    """Create a new user with validated fields.

    Args:
        user: User data with validated email, age, and optional website

    Returns:
        Created user data with normalized values

    Raises:
        HTTPException: 422 if validation fails (handled by FastAPI/Pydantic)

    """
    return {
        'name': user.name,
        'email': f'{user.email.local}@{user.email.domain}',
        'age': user.age,
        'website': f'{user.website.scheme}://{user.website.host}{user.website.path}' if user.website else None,
    }


@app.post('/products/', status_code=201)
async def create_product(product: ProductCreate) -> dict[str, str | int | float]:
    """Create a new product with validated price and quantity.

    Args:
        product: Product data with validated price and quantity

    Returns:
        Created product data

    Raises:
        HTTPException: 422 if validation fails

    """
    return {
        'name': product.name,
        'price': product.price,
        'quantity': product.quantity,
        'sku': product.sku or f'SKU-{product.name.upper()[:10]}',
    }


@app.get('/users/')
async def list_users(
    page: int = Query(1, ge=1, description='Page number (1-indexed)'),
    limit: int = Query(10, ge=1, le=100, description='Items per page (1-100)'),
    email: str | None = Query(None, description='Filter by email address'),
) -> dict[str, int | str | list | None]:
    """List users with pagination and optional email filter.

    Args:
        page: Page number (default: 1)
        limit: Items per page (default: 10, max: 100)
        email: Optional email address filter

    Returns:
        Paginated user list with filter information

    Raises:
        HTTPException: 400 if email parameter is invalid

    """
    email_filter = None

    if email:
        email_result = parsers.parse_email(email)
        match email_result:
            case Success(parsed_email):
                email_filter = f'{parsed_email.local}@{parsed_email.domain}'
            case Failure(error):
                raise HTTPException(
                    status_code=400,
                    detail={
                        'error': 'Invalid email parameter',
                        'message': error,
                        'parameter': 'email',
                        'received': email,
                    },
                )

    return {
        'page': page,
        'limit': limit,
        'email_filter': email_filter,
        'users': [],  # Your database query here
        'total': 0,
    }


@app.get('/products/')
async def list_products(
    min_price: str | None = Query(None, description='Minimum price filter'),
    max_price: str | None = Query(None, description='Maximum price filter'),
    sort_by: str = Query('name', description='Sort field'),
) -> dict[str, float | str | list]:
    """List products with optional price range filtering.

    Args:
        min_price: Optional minimum price filter
        max_price: Optional maximum price filter
        sort_by: Sort field (default: name)

    Returns:
        Filtered product list

    Raises:
        HTTPException: 400 if price parameters are invalid

    """
    min_price_value = 0.0
    max_price_value = float('inf')

    if min_price:
        min_result = parsers.parse_float(min_price).bind(validators.minimum(0.0))
        match min_result:
            case Success(value):
                min_price_value = value
            case Failure(error):
                raise HTTPException(
                    status_code=400,
                    detail={
                        'error': 'Invalid min_price parameter',
                        'message': error,
                        'parameter': 'min_price',
                        'received': min_price,
                        'expected': 'A positive number',
                    },
                )

    if max_price:
        max_result = parsers.parse_float(max_price).bind(validators.minimum(0.0))
        match max_result:
            case Success(value):
                max_price_value = value
            case Failure(error):
                raise HTTPException(
                    status_code=400,
                    detail={
                        'error': 'Invalid max_price parameter',
                        'message': error,
                        'parameter': 'max_price',
                        'received': max_price,
                        'expected': 'A positive number',
                    },
                )

    return {
        'min_price': min_price_value,
        'max_price': max_price_value if max_price_value != float('inf') else None,
        'sort_by': sort_by,
        'products': [],  # Your database query here
    }


@app.get('/protected/')
async def protected_resource(
    authorization: str | None = Header(None, description='Bearer token authorization'),
) -> dict[str, bool | str]:
    """Protected endpoint requiring authentication via Bearer token.

    Args:
        authorization: Authorization header with Bearer token (UUID format)

    Returns:
        Authentication confirmation

    Raises:
        HTTPException: 401 if authorization is missing or invalid

    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail={'error': 'Authorization required', 'message': 'Authorization header must be provided'},
        )

    if not authorization.startswith('Bearer '):
        raise HTTPException(
            status_code=401,
            detail={'error': 'Invalid authentication scheme', 'message': 'Authorization must use Bearer scheme'},
        )

    token = authorization[7:]  # Remove "Bearer " prefix
    token_result = parsers.parse_uuid(token)

    match token_result:
        case Success(uuid_token):
            # In production, verify token against database
            return {
                'authenticated': True,
                'token': str(uuid_token)[:8] + '...',  # Mask token in response
                'message': 'Access granted',
            }
        case Failure(error):
            raise HTTPException(
                status_code=401,
                detail={'error': 'Invalid token', 'message': error, 'hint': 'Token must be a valid UUID'},
            )


@app.get('/api/data')
async def api_data(
    x_api_key: str | None = Header(None, alias='X-API-Key', description='API key for authentication'),
) -> dict[str, str | list]:
    """API endpoint requiring API key in custom header.

    Args:
        x_api_key: API key in X-API-Key header (UUID format)

    Returns:
        API data

    Raises:
        HTTPException: 401 if API key is missing or invalid

    """
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail={'error': 'API key required', 'message': 'X-API-Key header must be provided'},
        )

    key_result = parsers.parse_uuid(x_api_key)
    match key_result:
        case Success(api_key):
            # In production, verify API key against database
            return {'api_key': str(api_key)[:8] + '...', 'data': []}
        case Failure(error):
            raise HTTPException(
                status_code=401,
                detail={'error': 'Invalid API key', 'message': error, 'hint': 'API key must be a valid UUID'},
            )


@app.get('/')
async def root() -> dict[str, str | dict[str, str]]:
    """Root endpoint with API information and documentation links."""
    return {
        'message': 'Valid8r + FastAPI Async Validation Demo',
        'version': '1.0.0',
        'endpoints': {
            'POST /users/': 'Create user (body validation)',
            'POST /products/': 'Create product (body validation)',
            'GET /users/': 'List users (query validation)',
            'GET /products/': 'List products (query validation)',
            'GET /protected/': 'Protected resource (header validation)',
            'GET /api/data': 'API data (custom header validation)',
            'GET /docs': 'Interactive API documentation',
            'GET /redoc': 'Alternative API documentation',
        },
        'examples': {
            'create_user': {
                'method': 'POST',
                'url': '/users/',
                'body': {'name': 'John Doe', 'email': 'john@example.com', 'age': 30},
            },
            'list_users': {
                'method': 'GET',
                'url': '/users/?page=1&limit=10&email=john@example.com',
            },
            'protected': {
                'method': 'GET',
                'url': '/protected/',
                'headers': {'Authorization': 'Bearer 550e8400-e29b-41d4-a716-446655440000'},
            },
        },
    }


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)  # noqa: S104
