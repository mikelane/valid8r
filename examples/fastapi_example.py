r"""FastAPI example demonstrating valid8r Pydantic integration.

This example shows how to use valid8r parsers as Pydantic field validators
in a FastAPI application.

Run with:
    uv run uvicorn examples.fastapi_example:app --reload

Test endpoints:
    curl -X POST http://localhost:8000/users/ \
        -H "Content-Type: application/json" \
        -d '{"name": "John Doe", "age": "30", "email": "john@example.com"}'
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import FastAPI
from pydantic import (
    BaseModel,
    field_validator,
)

from valid8r.core import (
    parsers,
    validators,
)
from valid8r.core.maybe import Maybe
from valid8r.core.parsers import EmailAddress  # noqa: TC001
from valid8r.integrations.pydantic import validator_from_parser

if TYPE_CHECKING:
    from typing import Any

app = FastAPI(title='Valid8r + FastAPI Example', version='1.0.0')


class UserCreate(BaseModel):
    """User creation request model."""

    name: str
    age: int
    email: EmailAddress

    @field_validator('age', mode='before')
    @classmethod
    def validate_age(cls, v: Any) -> int:  # noqa: ANN401
        """Validate age is between 0 and 120."""

        def age_parser(value: Any) -> Maybe[int]:  # noqa: ANN401
            # Handle both string and int inputs (FastAPI may pass either from JSON)
            if isinstance(value, int):
                return Maybe.success(value).bind(validators.between(0, 120))
            return parsers.parse_int(value).bind(validators.between(0, 120))

        return validator_from_parser(age_parser, error_prefix='Age')(v)

    @field_validator('email', mode='before')
    @classmethod
    def validate_email(cls, v: Any) -> EmailAddress:  # noqa: ANN401
        """Validate email format."""
        return validator_from_parser(parsers.parse_email, error_prefix='Email')(v)


@app.post('/users/', status_code=201)
def create_user(user: UserCreate) -> dict[str, str | int]:
    """Create a new user.

    Args:
        user: User data with validated fields

    Returns:
        Created user data with normalized email

    """
    return {
        'name': user.name,
        'age': user.age,
        'email': f'{user.email.local}@{user.email.domain}',
    }


@app.get('/')
def read_root() -> dict[str, str | dict[str, str]]:
    """Root endpoint with API information."""
    return {
        'message': 'Valid8r + FastAPI Integration Example',
        'endpoints': {
            'POST /users/': 'Create a user with validated age and email',
            'GET /docs': 'Interactive API documentation',
        },
        'example_request': {
            'name': 'John Doe',
            'age': '30',
            'email': 'john@example.com',
        },
    }


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)  # noqa: S104
