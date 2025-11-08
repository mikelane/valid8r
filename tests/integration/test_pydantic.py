"""Integration tests for Pydantic integration with valid8r parsers.

These tests verify that valid8r parsers work seamlessly with Pydantic models,
including nested models, lists, dicts, and complex validation scenarios.
"""

from __future__ import annotations

import pytest
from pydantic import (
    BaseModel,
    ValidationError,
    field_validator,
)

from valid8r.core import (
    parsers,
    validators,
)
from valid8r.core.parsers import (
    EmailAddress,
    PhoneNumber,
)
from valid8r.integrations.pydantic import validator_from_parser


class DescribePydanticNestedValidation:
    """Test nested model validation with valid8r parsers."""

    def it_validates_nested_model_with_phone_parser(self) -> None:
        """Validate nested User -> Address -> phone model."""

        class Address(BaseModel):
            phone: PhoneNumber

            @field_validator('phone', mode='before')
            @classmethod
            def validate_phone(cls, v):  # noqa: ANN001, ANN206
                return validator_from_parser(parsers.parse_phone)(v)

        class User(BaseModel):
            name: str
            address: Address

        # Valid nested model
        user = User(name='Alice', address={'phone': '(206) 234-5678'})
        assert user.name == 'Alice'
        assert isinstance(user.address.phone, PhoneNumber)
        assert user.address.phone.area_code == '206'

    def it_includes_field_path_in_nested_validation_errors(self) -> None:
        """Verify nested validation errors include full field path."""

        class Address(BaseModel):
            phone: PhoneNumber

            @field_validator('phone', mode='before')
            @classmethod
            def validate_phone(cls, v):  # noqa: ANN001, ANN206
                return validator_from_parser(parsers.parse_phone)(v)

        class User(BaseModel):
            address: Address

        # Invalid phone number should include field path
        with pytest.raises(ValidationError) as exc_info:
            User(address={'phone': 'invalid'})

        errors = exc_info.value.errors()
        assert len(errors) == 1
        # Field path should be ('address', 'phone')
        assert errors[0]['loc'] == ('address', 'phone')
        # Error message should contain valid8r parser error
        assert 'phone' in str(exc_info.value).lower() or 'invalid' in str(exc_info.value).lower()

    def it_validates_list_of_models_with_parser(self) -> None:
        """Validate list[Model] with per-item validation."""

        class LineItem(BaseModel):
            quantity: int

            @field_validator('quantity', mode='before')
            @classmethod
            def validate_quantity(cls, v):  # noqa: ANN001, ANN206
                parser = lambda value: parsers.parse_int(value).bind(validators.minimum(1))  # noqa: E731
                return validator_from_parser(parser)(v)

        class Order(BaseModel):
            items: list[LineItem]

        # Valid order
        order = Order(items=[{'quantity': '5'}, {'quantity': '10'}])
        assert len(order.items) == 2
        assert order.items[0].quantity == 5
        assert order.items[1].quantity == 10

        # Invalid: quantity less than minimum
        with pytest.raises(ValidationError) as exc_info:
            Order(items=[{'quantity': '5'}, {'quantity': '0'}])

        errors = exc_info.value.errors()
        assert len(errors) == 1
        # Field path should include list index
        assert errors[0]['loc'] == ('items', 1, 'quantity')
        assert 'minimum' in str(exc_info.value).lower() or 'least' in str(exc_info.value).lower()

    def it_validates_dict_values_with_parser(self) -> None:
        """Validate dict[str, T] with per-value validation."""

        class Config(BaseModel):
            ports: dict[str, int]

            @field_validator('ports', mode='before')
            @classmethod
            def validate_ports(cls, v):  # noqa: ANN001, ANN206
                if not isinstance(v, dict):
                    msg = 'ports must be a dict'
                    raise TypeError(msg)
                return {k: validator_from_parser(parsers.parse_int)(val) for k, val in v.items()}

        # Valid config
        config = Config(ports={'http': '80', 'https': '443'})
        assert config.ports == {'http': 80, 'https': 443}

        # Invalid: non-integer value
        with pytest.raises(ValidationError) as exc_info:
            Config(ports={'http': '80', 'https': 'invalid'})

        assert 'ports' in str(exc_info.value).lower()

    def it_handles_optional_nested_models(self) -> None:
        """Handle Optional[Model] with None values."""

        class Address(BaseModel):
            phone: PhoneNumber

            @field_validator('phone', mode='before')
            @classmethod
            def validate_phone(cls, v):  # noqa: ANN001, ANN206
                return validator_from_parser(parsers.parse_phone)(v)

        class User(BaseModel):
            name: str
            address: Address | None = None

        # User with address
        user1 = User(name='Alice', address={'phone': '(206) 234-5678'})
        assert user1.address is not None
        assert isinstance(user1.address.phone, PhoneNumber)

        # User without address
        user2 = User(name='Bob', address=None)
        assert user2.address is None

        # User with missing address (uses default)
        user3 = User(name='Charlie')
        assert user3.address is None

    def it_validates_deeply_nested_models(self) -> None:
        """Validate three-level nested Company -> Department -> Employee -> email."""

        class Employee(BaseModel):
            email: EmailAddress

            @field_validator('email', mode='before')
            @classmethod
            def validate_email(cls, v):  # noqa: ANN001, ANN206
                return validator_from_parser(parsers.parse_email)(v)

        class Department(BaseModel):
            lead: Employee

        class Company(BaseModel):
            engineering: Department

        # Valid deeply nested model
        company = Company(engineering={'lead': {'email': 'cto@example.com'}})
        assert isinstance(company.engineering.lead.email, EmailAddress)
        assert company.engineering.lead.email.local == 'cto'
        assert company.engineering.lead.email.domain == 'example.com'

    def it_preserves_field_path_in_deep_nesting_errors(self) -> None:
        """Verify field paths are preserved in deeply nested validation errors."""

        class Employee(BaseModel):
            email: EmailAddress

            @field_validator('email', mode='before')
            @classmethod
            def validate_email(cls, v):  # noqa: ANN001, ANN206
                return validator_from_parser(parsers.parse_email)(v)

        class Department(BaseModel):
            lead: Employee

        class Company(BaseModel):
            engineering: Department

        # Invalid email in deeply nested structure
        with pytest.raises(ValidationError) as exc_info:
            Company(engineering={'lead': {'email': 'not-an-email'}})

        errors = exc_info.value.errors()
        assert len(errors) == 1
        # Field path should be ('engineering', 'lead', 'email')
        assert errors[0]['loc'] == ('engineering', 'lead', 'email')
        assert 'email' in str(exc_info.value).lower() or 'invalid' in str(exc_info.value).lower()

    def it_combines_nested_validation_with_chained_validators(self) -> None:
        """Combine nested models with chained valid8r validators."""

        class Product(BaseModel):
            name: str
            price: int

            @field_validator('price', mode='before')
            @classmethod
            def validate_price(cls, v):  # noqa: ANN001, ANN206
                # Parse as int and validate range
                parser = lambda value: parsers.parse_int(value).bind(validators.between(1, 10000))  # noqa: E731
                return validator_from_parser(parser)(v)

        class CartItem(BaseModel):
            product: Product
            quantity: int

            @field_validator('quantity', mode='before')
            @classmethod
            def validate_quantity(cls, v):  # noqa: ANN001, ANN206
                parser = lambda value: parsers.parse_int(value).bind(validators.minimum(1))  # noqa: E731
                return validator_from_parser(parser)(v)

        class Cart(BaseModel):
            items: list[CartItem]

        # Valid cart
        cart = Cart(
            items=[
                {'product': {'name': 'Widget', 'price': '100'}, 'quantity': '2'},
                {'product': {'name': 'Gadget', 'price': '50'}, 'quantity': '1'},
            ]
        )
        assert len(cart.items) == 2
        assert cart.items[0].product.price == 100
        assert cart.items[0].quantity == 2

        # Invalid: price out of range
        with pytest.raises(ValidationError) as exc_info:
            Cart(items=[{'product': {'name': 'Expensive', 'price': '99999'}, 'quantity': '1'}])

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]['loc'] == ('items', 0, 'product', 'price')


class DescribePydanticErrorMessages:
    """Test error message quality for Pydantic validation failures."""

    def it_provides_clear_error_messages_for_nested_failures(self) -> None:
        """Verify clear error messages for nested validation failures."""

        class Contact(BaseModel):
            email: EmailAddress

            @field_validator('email', mode='before')
            @classmethod
            def validate_email(cls, v):  # noqa: ANN001, ANN206
                return validator_from_parser(parsers.parse_email)(v)

        class User(BaseModel):
            name: str
            contact: Contact

        # Invalid email
        with pytest.raises(ValidationError) as exc_info:
            User(name='Alice', contact={'email': 'invalid-email'})

        error_str = str(exc_info.value)
        # Error should mention email validation
        assert 'email' in error_str.lower() or 'invalid' in error_str.lower()
        # Field path should be clear
        errors = exc_info.value.errors()
        assert errors[0]['loc'] == ('contact', 'email')

    def it_uses_custom_error_prefix_in_nested_models(self) -> None:
        """Use custom error prefix from validator_from_parser."""

        class Settings(BaseModel):
            port: int

            @field_validator('port', mode='before')
            @classmethod
            def validate_port(cls, v):  # noqa: ANN001, ANN206
                return validator_from_parser(parsers.parse_int, error_prefix='Port number')(v)

        # Invalid port
        with pytest.raises(ValidationError) as exc_info:
            Settings(port='invalid')

        error_str = str(exc_info.value)
        # Custom error prefix should be present
        assert 'Port number' in error_str or 'port' in error_str.lower()
