"""Pydantic models demonstrating valid8r integration patterns.

This module shows various patterns for integrating valid8r parsers
and validators with Pydantic models for FastAPI request validation.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
)

from pydantic import (
    BaseModel,
    field_validator,
)

from valid8r.core import (
    parsers,
    validators,
)
from valid8r.integrations.pydantic import validator_from_parser

if TYPE_CHECKING:
    from valid8r.core.parsers import (
        EmailAddress,
        PhoneNumber,
        UrlParts,
    )


class UserBase(BaseModel):
    """Base user model with core fields."""

    name: str
    email: EmailAddress  # type: ignore[valid-type]

    @field_validator('email', mode='before')
    @classmethod
    def validate_email(cls, v: Any) -> EmailAddress:  # noqa: ANN401
        """Validate and normalize email address."""
        return validator_from_parser(parsers.parse_email, error_prefix='Email')(v)


class UserCreate(UserBase):
    """User creation model with additional required fields."""

    age: int
    phone: PhoneNumber | None = None  # type: ignore[valid-type]
    website: UrlParts | None = None  # type: ignore[valid-type]

    @field_validator('age', mode='before')
    @classmethod
    def validate_age(cls, v: Any) -> int:  # noqa: ANN401
        """Validate age is between 0 and 120."""

        def age_parser(value: Any) -> validators.Maybe[int]:  # noqa: ANN401
            if isinstance(value, int):
                return validators.between(0, 120)(value)
            return parsers.parse_int(value).bind(validators.between(0, 120))

        return validator_from_parser(age_parser, error_prefix='Age')(v)

    @field_validator('phone', mode='before')
    @classmethod
    def validate_phone(cls, v: Any) -> PhoneNumber | None:  # noqa: ANN401
        """Validate phone number format (NANP)."""
        if v is None:
            return None
        return validator_from_parser(parsers.parse_phone, error_prefix='Phone')(v)

    @field_validator('website', mode='before')
    @classmethod
    def validate_website(cls, v: Any) -> UrlParts | None:  # noqa: ANN401
        """Validate website URL format."""
        if v is None:
            return None
        return validator_from_parser(parsers.parse_url, error_prefix='Website')(v)


class UserResponse(UserBase):
    """User response model with computed fields."""

    id: int
    age: int
    phone: str | None = None
    website: str | None = None

    class Config:
        """Pydantic model configuration."""

        from_attributes = True


class ProductBase(BaseModel):
    """Base product model with core fields."""

    name: str
    description: str | None = None


class ProductCreate(ProductBase):
    """Product creation model with price and quantity validation."""

    price: float
    quantity: int
    sku: str | None = None

    @field_validator('price', mode='before')
    @classmethod
    def validate_price(cls, v: Any) -> float:  # noqa: ANN401
        """Validate price is positive and reasonable."""

        def price_parser(value: Any) -> validators.Maybe[float]:  # noqa: ANN401
            if isinstance(value, (int, float)):
                # Price must be at least $0.01
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


class ProductResponse(ProductBase):
    """Product response model."""

    id: int
    price: float
    quantity: int
    sku: str

    class Config:
        """Pydantic model configuration."""

        from_attributes = True


class OrderCreate(BaseModel):
    """Order creation model with item validation."""

    user_email: EmailAddress  # type: ignore[valid-type]
    product_id: int
    quantity: int
    shipping_address: str

    @field_validator('user_email', mode='before')
    @classmethod
    def validate_email(cls, v: Any) -> EmailAddress:  # noqa: ANN401
        """Validate user email."""
        return validator_from_parser(parsers.parse_email, error_prefix='User email')(v)

    @field_validator('product_id', mode='before')
    @classmethod
    def validate_product_id(cls, v: Any) -> int:  # noqa: ANN401
        """Validate product ID is positive."""

        def id_parser(value: Any) -> validators.Maybe[int]:  # noqa: ANN401
            if isinstance(value, int):
                return validators.minimum(1)(value)
            return parsers.parse_int(value).bind(validators.minimum(1))

        return validator_from_parser(id_parser, error_prefix='Product ID')(v)

    @field_validator('quantity', mode='before')
    @classmethod
    def validate_quantity(cls, v: Any) -> int:  # noqa: ANN401
        """Validate order quantity (1-1000)."""

        def quantity_parser(value: Any) -> validators.Maybe[int]:  # noqa: ANN401
            if isinstance(value, int):
                return validators.between(1, 1000)(value)
            return parsers.parse_int(value).bind(validators.between(1, 1000))

        return validator_from_parser(quantity_parser, error_prefix='Quantity')(v)


class OrderResponse(BaseModel):
    """Order response model."""

    id: int
    user_email: str
    product_id: int
    quantity: int
    total_price: float
    status: str

    class Config:
        """Pydantic model configuration."""

        from_attributes = True
