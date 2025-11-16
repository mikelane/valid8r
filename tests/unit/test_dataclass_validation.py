"""Unit tests for dataclass validation.

This module tests the dataclass integration feature, including:
- Field validation decorators
- Automatic parser generation from field types
- Error aggregation across fields
- Match/case pattern for validation result handling
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from valid8r.core.maybe import Failure, Success
from valid8r.core.validators import length, maximum, minimum


class DescribeValidateDecorator:
    """Tests for the @validate decorator."""

    def it_validates_simple_dataclass_with_valid_data(self) -> None:
        """Validate a simple dataclass with valid field values."""
        # This test will fail (RED) until we implement the validate decorator
        from valid8r.integrations.dataclasses import validate

        @validate
        @dataclass
        class Person:
            name: str
            age: int

        # Create test data
        data = {'name': 'Alice', 'age': 30}

        # Attempt validation - should return Success with dataclass instance
        result = Person.from_dict(data)  # type: ignore[attr-defined]

        # Pattern matching per requirements
        match result:
            case Success(person):
                assert person.name == 'Alice'
                assert person.age == 30
            case Failure(error):
                pytest.fail(f'Expected Success, got Failure: {error}')

    def it_validates_dataclass_with_field_validators(self) -> None:
        """Validate a dataclass with field-level validators."""
        from valid8r.integrations.dataclasses import validate

        @validate
        @dataclass
        class Product:
            name: str = field(metadata={'validator': length(1, 100)})
            price: float = field(metadata={'validator': minimum(0.0)})

        data = {'name': 'Laptop', 'price': 999.99}
        result = Product.from_dict(data)  # type: ignore[attr-defined]

        match result:
            case Success(product):
                assert product.name == 'Laptop'
                assert product.price == 999.99
            case Failure(error):
                pytest.fail(f'Expected Success, got Failure: {error}')

    def it_rejects_invalid_field_values(self) -> None:
        """Reject dataclass creation when field validation fails."""
        from valid8r.integrations.dataclasses import validate

        @validate
        @dataclass
        class Product:
            name: str = field(metadata={'validator': length(1, 100)})
            price: float = field(metadata={'validator': minimum(0.0)})

        # Invalid: empty name
        data = {'name': '', 'price': 999.99}
        result = Product.from_dict(data)  # type: ignore[attr-defined]

        match result:
            case Failure(error):
                assert 'name' in error.lower()
            case Success(value):
                pytest.fail(f'Expected Failure, got Success: {value}')

    def it_aggregates_multiple_field_errors(self) -> None:
        """Aggregate errors from multiple invalid fields."""
        from valid8r.integrations.dataclasses import validate

        @validate
        @dataclass
        class Product:
            name: str = field(metadata={'validator': length(1, 100)})
            price: float = field(metadata={'validator': minimum(0.0) & maximum(10000.0)})

        # Invalid: empty name AND negative price
        data = {'name': '', 'price': -10.0}
        result = Product.from_dict(data)  # type: ignore[attr-defined]

        match result:
            case Failure(error):
                # Error should contain both field names
                assert 'name' in error.lower()
                assert 'price' in error.lower()
            case Success(value):
                pytest.fail(f'Expected Failure, got Success: {value}')

    def it_handles_optional_fields(self) -> None:
        """Handle Optional fields correctly (None is valid)."""
        from valid8r.integrations.dataclasses import validate

        @validate
        @dataclass
        class Person:
            name: str
            nickname: str | None = None

        # None should be valid for Optional[str]
        data = {'name': 'Alice', 'nickname': None}
        result = Person.from_dict(data)  # type: ignore[attr-defined]

        match result:
            case Success(person):
                assert person.name == 'Alice'
                assert person.nickname is None
            case Failure(error):
                pytest.fail(f'Expected Success, got Failure: {error}')


# Module-level dataclasses for nested validation tests
@dataclass
class TestAddress:
    """Test Address dataclass for nested validation."""

    street: str
    city: str
    zip_code: str = field(metadata={'validator': length(5, 5)})


@dataclass
class TestPerson:
    """Test Person dataclass for nested validation."""

    name: str
    address: TestAddress


class DescribeValidateDataclass:
    """Tests for the validate_dataclass function."""

    def it_validates_dataclass_from_dict(self) -> None:
        """Validate a dataclass instance from a dictionary."""
        from valid8r.integrations.dataclasses import validate_dataclass

        @dataclass
        class Person:
            name: str
            age: int

        data = {'name': 'Bob', 'age': 25}
        result = validate_dataclass(Person, data)

        match result:
            case Success(person):
                assert isinstance(person, Person)
                assert person.name == 'Bob'
                assert person.age == 25
            case Failure(error):
                pytest.fail(f'Expected Success, got Failure: {error}')

    def it_validates_with_field_metadata(self) -> None:
        """Use field metadata to apply validators."""
        from valid8r.integrations.dataclasses import validate_dataclass

        @dataclass
        class Product:
            name: str = field(metadata={'validator': length(1, 50)})
            price: float = field(metadata={'validator': minimum(0.0)})

        data = {'name': 'Widget', 'price': 19.99}
        result = validate_dataclass(Product, data)

        match result:
            case Success(product):
                assert product.name == 'Widget'
                assert product.price == 19.99
            case Failure(error):
                pytest.fail(f'Expected Success, got Failure: {error}')

    def it_returns_failure_for_invalid_data(self) -> None:
        """Return Failure when validation fails."""
        from valid8r.integrations.dataclasses import validate_dataclass

        @dataclass
        class Product:
            name: str = field(metadata={'validator': length(1, 50)})
            price: float = field(metadata={'validator': minimum(0.0)})

        # Price is negative
        data = {'name': 'Widget', 'price': -5.0}
        result = validate_dataclass(Product, data)

        match result:
            case Failure(error):
                assert 'price' in error.lower()
            case Success(value):
                pytest.fail(f'Expected Failure, got Success: {value}')

    def it_validates_nested_dataclasses(self) -> None:
        """Validate nested dataclass structures."""
        from valid8r.integrations.dataclasses import validate_dataclass

        # Use module-level classes (defined above) for type hint resolution
        data = {
            'name': 'Alice',
            'address': {
                'street': '123 Main St',
                'city': 'Portland',
                'zip_code': '97201',
            },
        }

        result = validate_dataclass(TestPerson, data)

        match result:
            case Success(person):
                assert person.name == 'Alice'
                assert person.address.street == '123 Main St'
                assert person.address.zip_code == '97201'
            case Failure(error):
                pytest.fail(f'Expected Success, got Failure: {error}')

    def it_reports_errors_in_nested_structures(self) -> None:
        """Report validation errors in nested dataclasses."""
        from valid8r.integrations.dataclasses import validate_dataclass

        # Use module-level classes (defined above) for type hint resolution
        # Invalid zip_code (too short)
        data = {
            'name': 'Alice',
            'address': {
                'street': '123 Main St',
                'city': 'Portland',
                'zip_code': '123',  # Invalid - should be 5 digits
            },
        }

        result = validate_dataclass(TestPerson, data)

        match result:
            case Failure(error):
                assert 'zip_code' in error.lower() or 'address' in error.lower()
            case Success(value):
                pytest.fail(f'Expected Failure, got Success: {value}')


class DescribeTypeCoercion:
    """Tests for automatic type coercion from strings."""

    def it_parses_string_to_int(self) -> None:
        """Parse string values to int fields."""
        from valid8r.integrations.dataclasses import validate_dataclass

        @dataclass
        class Person:
            name: str
            age: int

        # Age provided as string
        data = {'name': 'Charlie', 'age': '35'}
        result = validate_dataclass(Person, data)

        match result:
            case Success(person):
                assert person.age == 35
                assert isinstance(person.age, int)
            case Failure(error):
                pytest.fail(f'Expected Success, got Failure: {error}')

    def it_parses_string_to_float(self) -> None:
        """Parse string values to float fields."""
        from valid8r.integrations.dataclasses import validate_dataclass

        @dataclass
        class Product:
            name: str
            price: float

        data = {'name': 'Gadget', 'price': '29.99'}
        result = validate_dataclass(Product, data)

        match result:
            case Success(product):
                assert product.price == 29.99
                assert isinstance(product.price, float)
            case Failure(error):
                pytest.fail(f'Expected Success, got Failure: {error}')

    def it_parses_string_to_bool(self) -> None:
        """Parse string values to bool fields."""
        from valid8r.integrations.dataclasses import validate_dataclass

        @dataclass
        class Product:
            name: str
            in_stock: bool

        data = {'name': 'Widget', 'in_stock': 'true'}
        result = validate_dataclass(Product, data)

        match result:
            case Success(product):
                assert product.in_stock is True
                assert isinstance(product.in_stock, bool)
            case Failure(error):
                pytest.fail(f'Expected Success, got Failure: {error}')

    def it_rejects_unparseable_strings(self) -> None:
        """Return Failure for strings that cannot be parsed."""
        from valid8r.integrations.dataclasses import validate_dataclass

        @dataclass
        class Person:
            name: str
            age: int

        # Invalid age string
        data = {'name': 'Dan', 'age': 'not-a-number'}
        result = validate_dataclass(Person, data)

        match result:
            case Failure(error):
                assert 'age' in error.lower()
            case Success(value):
                pytest.fail(f'Expected Failure, got Success: {value}')


class DescribeErrorAggregation:
    """Tests for error aggregation across multiple fields."""

    def it_collects_all_field_errors(self) -> None:
        """Collect errors from all fields before returning."""
        from valid8r.integrations.dataclasses import validate_dataclass

        @dataclass
        class Product:
            name: str = field(metadata={'validator': length(1, 50)})
            price: float = field(metadata={'validator': minimum(0.0)})
            quantity: int = field(metadata={'validator': minimum(1)})

        # All three fields invalid
        data = {'name': '', 'price': -10.0, 'quantity': 0}
        result = validate_dataclass(Product, data)

        match result:
            case Failure(error):
                # Should mention all three fields
                error_lower = error.lower()
                assert 'name' in error_lower
                assert 'price' in error_lower
                assert 'quantity' in error_lower
            case Success(value):
                pytest.fail(f'Expected Failure, got Success: {value}')

    def it_provides_descriptive_error_messages(self) -> None:
        """Provide clear error messages for each failed field."""
        from valid8r.integrations.dataclasses import validate_dataclass

        @dataclass
        class Person:
            name: str = field(metadata={'validator': length(2, 100)})
            age: int = field(metadata={'validator': minimum(0) & maximum(150)})

        data = {'name': 'X', 'age': 200}  # Both invalid
        result = validate_dataclass(Person, data)

        match result:
            case Failure(error):
                # Error should be descriptive
                assert len(error) > 10  # Not just a generic message
                assert 'name' in error.lower()
                assert 'age' in error.lower()
            case Success(value):
                pytest.fail(f'Expected Failure, got Success: {value}')


class DescribePatternMatching:
    """Tests verifying match/case usage throughout implementation."""

    def it_uses_match_case_for_validation_results(self) -> None:
        """Validate that implementation uses match/case for Maybe results."""
        from valid8r.integrations.dataclasses import validate_dataclass

        @dataclass
        class Simple:
            value: int = field(metadata={'validator': minimum(0)})

        # This test verifies the pattern matching works correctly
        result = validate_dataclass(Simple, {'value': 42})

        # Use pattern matching to verify
        match result:
            case Success(instance):
                assert instance.value == 42
            case Failure(_):
                pytest.fail('Expected Success')

        # Also test failure path
        result_fail = validate_dataclass(Simple, {'value': -1})

        match result_fail:
            case Success(_):
                pytest.fail('Expected Failure')
            case Failure(error):
                assert 'value' in error.lower() or 'minimum' in error.lower()
