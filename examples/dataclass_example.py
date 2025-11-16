"""Example demonstrating dataclass field validation with Valid8r.

This example shows how to use the @validate decorator to add validation
to Python dataclasses with automatic type coercion and error aggregation.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import (
    dataclass,
    field,
)

from valid8r.core.maybe import (
    Failure,
    Maybe,
    Success,
)
from valid8r.core.validators import (
    length,
    matches_regex,
    maximum,
    minimum,
)
from valid8r.integrations.dataclasses import validate


# Example 1: Basic validation with type coercion
@validate
@dataclass
class Product:
    """A product with validated fields."""

    name: str = field(metadata={'validator': length(1, 100)})
    price: float = field(metadata={'validator': minimum(0.0)})
    quantity: int = field(metadata={'validator': minimum(0) & maximum(10000)})


def example_basic_validation() -> None:
    """Demonstrate basic field validation with type coercion."""
    print('=== Example 1: Basic Validation ===\n')

    # Valid product with string-to-number coercion
    result = Product.from_dict({'name': 'Laptop', 'price': '999.99', 'quantity': '5'})

    match result:
        case Success(product):
            print(f'✓ Created: {product.name} - ${product.price} ({product.quantity} in stock)')
        case Failure(error):
            print(f'✗ Error: {error}')

    # Invalid product (multiple errors)
    result = Product.from_dict({'name': '', 'price': '-10.0', 'quantity': '999999'})

    match result:
        case Success(product):
            print(f'✓ Created: {product}')
        case Failure(error):
            print(f'✗ Validation errors: {error}')

    print()


# Example 2: Nested dataclasses
@dataclass
class Address:
    """Address with validated zip code."""

    street: str
    city: str
    zip_code: str = field(metadata={'validator': matches_regex(r'^\d{5}(-\d{4})?$')})


@validate
@dataclass
class Person:
    """Person with name and validated address."""

    name: str = field(metadata={'validator': length(1, 100)})
    age: int = field(metadata={'validator': minimum(0) & maximum(120)})
    address: Address


def example_nested_dataclasses() -> None:
    """Demonstrate nested dataclass validation."""
    print('=== Example 2: Nested Dataclasses ===\n')

    # Valid nested structure
    result = Person.from_dict(
        {
            'name': 'Alice Smith',
            'age': '30',
            'address': {'street': '123 Main St', 'city': 'Portland', 'zip_code': '97201'},
        }
    )

    match result:
        case Success(person):
            print(f'✓ Created: {person.name}, age {person.age}')
            print(f'  Address: {person.address.street}, {person.address.city} {person.address.zip_code}')
        case Failure(error):
            print(f'✗ Error: {error}')

    # Invalid zip code in nested structure
    result = Person.from_dict(
        {
            'name': 'Bob Jones',
            'age': '25',
            'address': {'street': '456 Oak Ave', 'city': 'Seattle', 'zip_code': '123'},  # Invalid
        }
    )

    match result:
        case Success(person):
            print(f'✓ Created: {person}')
        case Failure(error):
            print(f'✗ Nested validation error: {error}')

    print()


# Example 3: Optional fields with defaults
@validate
@dataclass
class BlogPost:
    """Blog post with optional summary field."""

    title: str = field(metadata={'validator': length(1, 200)})
    content: str = field(metadata={'validator': length(1, 10000)})
    summary: str | None = None
    published: bool = False


def example_optional_fields() -> None:
    """Demonstrate optional fields and defaults."""
    print('=== Example 3: Optional Fields ===\n')

    # Minimal post (uses defaults)
    result = BlogPost.from_dict({'title': 'Hello World', 'content': 'This is my first post!'})

    match result:
        case Success(post):
            print(f'✓ Created: "{post.title}"')
            print(f'  Published: {post.published}, Summary: {post.summary}')
        case Failure(error):
            print(f'✗ Error: {error}')

    # Full post
    result = BlogPost.from_dict(
        {
            'title': 'Advanced Python',
            'content': 'Deep dive into...',
            'summary': 'Learn advanced Python techniques',
            'published': 'true',
        }
    )

    match result:
        case Success(post):
            print(f'✓ Created: "{post.title}"')
            print(f'  Published: {post.published}, Summary: "{post.summary}"')
        case Failure(error):
            print(f'✗ Error: {error}')

    print()


# Example 4: Complex validators
@validate
@dataclass
class UserAccount:
    """User account with complex password requirements."""

    username: str = field(metadata={'validator': length(3, 20) & matches_regex(r'^[a-zA-Z0-9_]+$')})
    email: str = field(metadata={'validator': matches_regex(r'^[\w\.-]+@[\w\.-]+\.\w+$')})
    password: str = field(
        metadata={
            'validator': (
                length(8, 128)
                & matches_regex(r'[A-Z]')  # Has uppercase
                & matches_regex(r'[a-z]')  # Has lowercase
                & matches_regex(r'[0-9]')  # Has digit
            )
        }
    )


def example_complex_validators() -> None:
    """Demonstrate complex validation rules."""
    print('=== Example 4: Complex Validators ===\n')

    # Valid account
    result = UserAccount.from_dict(
        {
            'username': 'alice_123',
            'email': 'alice@example.com',
            'password': 'SecurePass123',
        }
    )

    match result:
        case Success(account):
            print(f'✓ Created account: {account.username} ({account.email})')
        case Failure(error):
            print(f'✗ Error: {error}')

    # Invalid username (special chars)
    result = UserAccount.from_dict(
        {
            'username': 'alice@home',
            'email': 'alice@example.com',
            'password': 'SecurePass123',
        }
    )

    match result:
        case Success(account):
            print(f'✓ Created account: {account.username}')
        case Failure(error):
            print(f'✗ Username validation failed: {error}')

    # Weak password (missing uppercase)
    result = UserAccount.from_dict(
        {
            'username': 'bob_456',
            'email': 'bob@example.com',
            'password': 'weakpass123',
        }
    )

    match result:
        case Success(account):
            print(f'✓ Created account: {account.username}')
        case Failure(error):
            print(f'✗ Password validation failed: {error}')

    print()


# Example 5: Custom validator
def validate_price_range(min_price: float, max_price: float) -> Callable[[float], Maybe[float]]:
    """Create a validator for price ranges.

    Returns:
        A validator function that checks if a price is within range.

    """

    def validator(price: float) -> Maybe[float]:
        if not (min_price <= price <= max_price):
            return Maybe.failure(f'must be between ${min_price} and ${max_price}')
        return Maybe.success(price)

    return validator


@validate
@dataclass
class SaleItem:
    """Sale item with custom price validator."""

    name: str = field(metadata={'validator': length(1, 100)})
    price: float = field(metadata={'validator': validate_price_range(0.99, 99.99)})
    discount_percent: int = field(metadata={'validator': minimum(0) & maximum(100)})


def example_custom_validator() -> None:
    """Demonstrate custom validators."""
    print('=== Example 5: Custom Validators ===\n')

    # Valid sale item
    result = SaleItem.from_dict({'name': 'Widget', 'price': '19.99', 'discount_percent': '20'})

    match result:
        case Success(item):
            final_price = item.price * (1 - item.discount_percent / 100)
            print(f'✓ Created: {item.name} - ${item.price} ({item.discount_percent}% off = ${final_price:.2f})')
        case Failure(error):
            print(f'✗ Error: {error}')

    # Price too high
    result = SaleItem.from_dict({'name': 'Expensive Item', 'price': '150.00', 'discount_percent': '10'})

    match result:
        case Success(item):
            print(f'✓ Created: {item}')
        case Failure(error):
            print(f'✗ Price validation failed: {error}')

    print()


# Main execution
if __name__ == '__main__':
    example_basic_validation()
    example_nested_dataclasses()
    example_optional_fields()
    example_complex_validators()
    example_custom_validator()

    print('=== Summary ===')
    print('The @validate decorator adds a from_dict() classmethod that:')
    print('  1. Coerces strings to target types (int, float, bool)')
    print('  2. Validates fields using validators from metadata')
    print('  3. Aggregates all errors before returning')
    print('  4. Returns Maybe[T] for pattern matching')
