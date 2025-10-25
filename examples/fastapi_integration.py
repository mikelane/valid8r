"""FastAPI + Pydantic + Valid8r Integration Example.

This example demonstrates how to use Valid8r with FastAPI and Pydantic for
robust API validation. Valid8r's Maybe monad pattern integrates seamlessly
with Pydantic's validation system.

Usage:
    1. Install dependencies: pip install -r examples/requirements.txt
    2. Run the server: uvicorn examples.fastapi_integration:app --reload
    3. Visit http://localhost:8000/docs for interactive API documentation
"""

from __future__ import annotations

from typing import Annotated

from fastapi import (
    Body,
    FastAPI,
    HTTPException,
)
from pydantic import (
    BaseModel,
    ConfigDict,
    field_validator,
)

from valid8r import (
    parsers,
    validators,
)

app = FastAPI(
    title='Valid8r + FastAPI Example',
    description='Demonstrates integration of Valid8r with FastAPI and Pydantic',
    version='1.0.0',
)


# Example 1: Using Valid8r in Pydantic field validators
# -------------------------------------------------------


class UserCreate(BaseModel):
    """User registration model with Valid8r validation."""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: str
    age: int
    website: str | None = None

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email using Valid8r's parse_email."""
        result = parsers.parse_email(v)
        if result.is_failure():
            raise ValueError(result.error_or('Invalid email address'))
        # Return the original value (Pydantic expects the field value)
        return v

    @field_validator('age')
    @classmethod
    def validate_age(cls, v: int) -> int:
        """Validate age is between 18 and 120."""
        result = validators.between(18, 120)(v)
        if result.is_failure():
            raise ValueError(result.error_or('Age must be between 18 and 120'))
        return v

    @field_validator('website')
    @classmethod
    def validate_website(cls, v: str | None) -> str | None:
        """Validate website URL if provided."""
        if v is None:
            return v

        result = parsers.parse_url(v)
        if result.is_failure():
            raise ValueError(result.error_or('Invalid website URL'))

        # Additional validation: must be http or https
        url_parts = result.value_or(None)
        if url_parts and url_parts.scheme not in ('http', 'https'):
            raise ValueError('Website must use http or https protocol')

        return v


@app.post('/users', response_model=dict, status_code=201)
async def create_user(user: UserCreate) -> dict:
    """Create a new user with validated input.

    Demonstrates Valid8r validators in Pydantic models.
    """
    return {
        'message': 'User created successfully',
        'user': {
            'email': user.email,
            'age': user.age,
            'website': user.website,
        },
    }


# Example 2: Custom validation function with Valid8r
# ---------------------------------------------------


def validate_ipv4_address(ip_str: str) -> str:
    """Validate IPv4 address using Valid8r."""
    result = parsers.parse_ipv4(ip_str)
    if result.is_failure():
        raise HTTPException(status_code=400, detail=result.error_or('Invalid IPv4 address'))
    return ip_str


@app.post('/whitelist-ip')
async def whitelist_ip(ip_address: Annotated[str, Body(embed=True)]) -> dict:
    """Add an IP to whitelist with validation.

    Demonstrates using Valid8r for dependency injection style validation.
    """
    validated_ip = validate_ipv4_address(ip_address)
    return {'message': f'IP {validated_ip} added to whitelist'}


# Example 3: Bulk validation with Valid8r parsers
# ------------------------------------------------


class BatchEmailValidation(BaseModel):
    """Model for batch email validation."""

    emails: list[str]


@app.post('/validate-emails')
async def validate_emails(batch: BatchEmailValidation) -> dict:
    """Validate multiple emails and return results.

    Demonstrates using Valid8r for batch validation with detailed results.
    """
    results = []

    for email_str in batch.emails:
        result = parsers.parse_email(email_str)
        if result.is_success():
            email = result.value_or(None)
            results.append(
                {
                    'email': email_str,
                    'valid': True,
                    'local': email.local if email else None,
                    'domain': email.domain if email else None,
                }
            )
        else:
            results.append({'email': email_str, 'valid': False, 'error': result.error_or('Unknown error')})

    valid_count = sum(1 for r in results if r['valid'])
    return {
        'total': len(batch.emails),
        'valid': valid_count,
        'invalid': len(batch.emails) - valid_count,
        'results': results,
    }


# Example 4: Configuration parsing with Valid8r
# ----------------------------------------------


class ServerConfig(BaseModel):
    """Server configuration with rich validation."""

    model_config = ConfigDict(str_strip_whitespace=True)

    host: str
    port: int
    max_connections: int
    timeout_seconds: int | None = None

    @field_validator('host')
    @classmethod
    def validate_host(cls, v: str) -> str:
        """Validate host is a valid IP address or hostname."""
        # Try parsing as IPv4
        ipv4_result = parsers.parse_ipv4(v)
        if ipv4_result.is_success():
            return v

        # Try parsing as IPv6
        ipv6_result = parsers.parse_ipv6(v)
        if ipv6_result.is_success():
            return v

        # Accept hostname (basic validation)
        if not v or '/' in v or '@' in v:
            raise ValueError('Invalid host: must be IP address or hostname')

        return v

    @field_validator('port')
    @classmethod
    def validate_port(cls, v: int) -> int:
        """Validate port is in valid range."""
        result = validators.between(1, 65535)(v)
        if result.is_failure():
            raise ValueError('Port must be between 1 and 65535')
        return v

    @field_validator('max_connections')
    @classmethod
    def validate_max_connections(cls, v: int) -> int:
        """Validate max connections is positive."""
        result = validators.minimum(1)(v)
        if result.is_failure():
            raise ValueError('Max connections must be positive')
        return v

    @field_validator('timeout_seconds')
    @classmethod
    def validate_timeout(cls, v: int | None) -> int | None:
        """Validate timeout if provided."""
        if v is None:
            return v

        result = validators.minimum(1)(v)
        if result.is_failure():
            raise ValueError('Timeout must be positive')
        return v


@app.post('/configure')
async def configure_server(config: ServerConfig) -> dict:
    """Configure server with validated settings.

    Demonstrates comprehensive validation with Valid8r validators.
    """
    return {
        'message': 'Server configured successfully',
        'config': {
            'host': config.host,
            'port': config.port,
            'max_connections': config.max_connections,
            'timeout_seconds': config.timeout_seconds,
        },
    }


# Example 5: Chaining Valid8r validators
# ----------------------------------------


class ProductCreate(BaseModel):
    """Product creation with chained validation."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str
    price: float
    quantity: int

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate product name: 3-100 chars, non-empty."""
        # Validate length using Valid8r's length validator
        result = validators.length(3, 100)(v)

        if result.is_failure():
            raise ValueError(result.error_or('Invalid product name'))
        return v

    @field_validator('price')
    @classmethod
    def validate_price(cls, v: float) -> float:
        """Validate price is positive."""
        result = validators.predicate(lambda x: x > 0, 'Price must be positive')(v)
        if result.is_failure():
            raise ValueError('Price must be positive')
        return v

    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        """Validate quantity is between 1 and 10000."""
        result = validators.between(1, 10000)(v)
        if result.is_failure():
            raise ValueError('Quantity must be between 1 and 10000')
        return v


@app.post('/products')
async def create_product(product: ProductCreate) -> dict:
    """Create a product with chained validation.

    Demonstrates chaining Valid8r validators with bind().
    """
    return {
        'message': 'Product created successfully',
        'product': {'name': product.name, 'price': product.price, 'quantity': product.quantity},
    }


# Health check endpoint
# ---------------------


@app.get('/')
async def root() -> dict:
    """Root endpoint with usage information."""
    return {
        'message': 'Valid8r + FastAPI Integration Example',
        'docs': '/docs',
        'endpoints': {
            'POST /users': 'Create user with email/age/website validation',
            'POST /whitelist-ip': 'Whitelist IPv4 address',
            'POST /validate-emails': 'Batch email validation',
            'POST /configure': 'Configure server with validated settings',
            'POST /products': 'Create product with chained validators',
        },
    }


if __name__ == '__main__':
    import uvicorn

    print('Starting FastAPI server...')
    print('Visit http://localhost:8000/docs for interactive documentation')
    uvicorn.run(app, host='127.0.0.1', port=8000)
