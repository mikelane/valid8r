# Pydantic Integration

The Pydantic integration enables seamless use of valid8r parsers with [Pydantic](https://docs.pydantic.dev/) models, allowing you to leverage valid8r's powerful parsing and validation capabilities in FastAPI applications, data validation workflows, and anywhere Pydantic is used.

## Why Integrate valid8r with Pydantic?

**Reusable Validation Logic**: Use the same valid8r parsers across CLI prompts, API validation, configuration parsing, and data processing without duplicating validation logic.

**Type-Safe Parsing**: Valid8r's `Maybe[T]` pattern ensures type safety and explicit error handling, which integrates naturally with Pydantic's validation framework.

**Rich Error Messages**: valid8r provides user-friendly, detailed error messages that flow through to Pydantic's `ValidationError`, helping users understand what went wrong.

**Complex Nested Structures**: Full support for nested models, lists of models, dict values, and deeply nested hierarchies with complete field path reporting.

## Installation

valid8r's Pydantic integration is included in the main package:

```bash
pip install valid8r pydantic
```

Or with uv:

```bash
uv add valid8r pydantic
```

## Quick Start

### Basic Field Validation

```python
from pydantic import BaseModel, field_validator
from valid8r.core import parsers, validators
from valid8r.integrations.pydantic import validator_from_parser

class User(BaseModel):
    age: int
    email: str

    @field_validator('age', mode='before')
    @classmethod
    def validate_age(cls, v):
        return validator_from_parser(
            parsers.parse_int & validators.between(0, 120)
        )(v)

    @field_validator('email', mode='before')
    @classmethod
    def validate_email(cls, v):
        return validator_from_parser(parsers.parse_email)(v)

# Valid user
user = User(age='25', email='alice@example.com')
print(user.age)  # 25 (parsed from string)
print(user.email)  # EmailAddress(local='alice', domain='example.com')

# Invalid age (out of range)
try:
    User(age='200', email='alice@example.com')
except ValidationError as e:
    print(e)  # Error message includes "between 0 and 120"
```

## Core API

### `validator_from_parser()`

Convert a valid8r parser into a Pydantic field validator.

```python
def validator_from_parser(
    parser: Callable[[Any], Maybe[T]],
    *,
    error_prefix: str | None = None,
) -> Callable[[Any], T]:
    """Convert a valid8r parser into a Pydantic field validator."""
```

**Parameters**:
- `parser`: Any valid8r parser function that returns `Maybe[T]`
- `error_prefix` (optional): Custom prefix to prepend to error messages

**Returns**: A validator function suitable for use with `@field_validator`

**Example**:
```python
from pydantic import BaseModel, field_validator
from valid8r.core import parsers
from valid8r.integrations.pydantic import validator_from_parser

class Config(BaseModel):
    port: int

    @field_validator('port', mode='before')
    @classmethod
    def validate_port(cls, v):
        return validator_from_parser(
            parsers.parse_int,
            error_prefix='Server port'
        )(v)

# Custom error prefix appears in validation errors
try:
    Config(port='invalid')
except ValidationError as e:
    print(e)  # "Server port: ..."
```

## Nested Model Validation

### Two-Level Nesting

Valid8r parsers work seamlessly with nested Pydantic models. Pydantic automatically includes the full field path in validation errors.

```python
from pydantic import BaseModel, field_validator
from valid8r.core import parsers
from valid8r.core.parsers import PhoneNumber
from valid8r.integrations.pydantic import validator_from_parser

class Address(BaseModel):
    street: str
    phone: PhoneNumber

    @field_validator('phone', mode='before')
    @classmethod
    def validate_phone(cls, v):
        return validator_from_parser(parsers.parse_phone)(v)

class User(BaseModel):
    name: str
    address: Address

# Valid nested model
user = User(
    name='Alice',
    address={'street': '123 Main St', 'phone': '(206) 234-5678'}
)
print(user.address.phone.area_code)  # '206'

# Invalid phone number - error includes field path
try:
    User(name='Bob', address={'street': '456 Elm St', 'phone': 'invalid'})
except ValidationError as e:
    errors = e.errors()
    print(errors[0]['loc'])  # ('address', 'phone')
    print(errors[0]['msg'])  # Contains valid8r error message
```

### Three-Level+ Nesting

Deep nesting works without modification. Field paths are preserved through all levels.

```python
from pydantic import BaseModel, field_validator
from valid8r.core import parsers
from valid8r.core.parsers import EmailAddress
from valid8r.integrations.pydantic import validator_from_parser

class Employee(BaseModel):
    email: EmailAddress

    @field_validator('email', mode='before')
    @classmethod
    def validate_email(cls, v):
        return validator_from_parser(parsers.parse_email)(v)

class Department(BaseModel):
    lead: Employee

class Company(BaseModel):
    engineering: Department

# Valid deeply nested model
company = Company(
    engineering={'lead': {'email': 'cto@example.com'}}
)
print(company.engineering.lead.email.local)  # 'cto'

# Invalid email - field path includes all levels
try:
    Company(engineering={'lead': {'email': 'not-an-email'}})
except ValidationError as e:
    errors = e.errors()
    print(errors[0]['loc'])  # ('engineering', 'lead', 'email')
```

### Optional Nested Models

Use `Optional[Model]` or `Model | None` for optional nested fields.

```python
from pydantic import BaseModel, field_validator
from valid8r.core import parsers
from valid8r.core.parsers import PhoneNumber
from valid8r.integrations.pydantic import validator_from_parser

class Address(BaseModel):
    phone: PhoneNumber

    @field_validator('phone', mode='before')
    @classmethod
    def validate_phone(cls, v):
        return validator_from_parser(parsers.parse_phone)(v)

class User(BaseModel):
    name: str
    address: Address | None = None

# User with address
user1 = User(name='Alice', address={'phone': '(206) 234-5678'})
print(user1.address.phone)  # PhoneNumber object

# User without address
user2 = User(name='Bob', address=None)
print(user2.address)  # None

# User with missing address (uses default)
user3 = User(name='Charlie')
print(user3.address)  # None
```

## Collection Validation

### List of Models

Validate lists of models with per-item validation. Pydantic reports errors with list indices.

```python
from pydantic import BaseModel, field_validator
from valid8r.core import parsers, validators
from valid8r.integrations.pydantic import validator_from_parser

class LineItem(BaseModel):
    product_name: str
    quantity: int

    @field_validator('quantity', mode='before')
    @classmethod
    def validate_quantity(cls, v):
        parser = lambda value: parsers.parse_int(value).bind(validators.minimum(1))
        return validator_from_parser(parser)(v)

class Order(BaseModel):
    items: list[LineItem]

# Valid order
order = Order(items=[
    {'product_name': 'Widget', 'quantity': '5'},
    {'product_name': 'Gadget', 'quantity': '10'}
])
print(order.items[0].quantity)  # 5

# Invalid: quantity below minimum
try:
    Order(items=[
        {'product_name': 'Widget', 'quantity': '5'},
        {'product_name': 'Gadget', 'quantity': '0'}  # Invalid
    ])
except ValidationError as e:
    errors = e.errors()
    print(errors[0]['loc'])  # ('items', 1, 'quantity')
    print(errors[0]['msg'])  # Contains "minimum" or "at least"
```

### Dict Value Validation

Validate dictionary values using valid8r parsers.

```python
from pydantic import BaseModel, field_validator
from valid8r.core import parsers
from valid8r.integrations.pydantic import validator_from_parser

class Config(BaseModel):
    ports: dict[str, int]

    @field_validator('ports', mode='before')
    @classmethod
    def validate_ports(cls, v):
        if not isinstance(v, dict):
            raise TypeError('ports must be a dict')
        return {k: validator_from_parser(parsers.parse_int)(val) for k, val in v.items()}

# Valid config
config = Config(ports={'http': '80', 'https': '443', 'ssh': '22'})
print(config.ports)  # {'http': 80, 'https': 443, 'ssh': 22}

# Invalid: non-integer value
try:
    Config(ports={'http': '80', 'https': 'invalid'})
except ValidationError as e:
    print(e)  # Error mentions parsing failure
```

## Advanced Patterns

### Chained Validators in Nested Models

Combine multiple valid8r validators in deeply nested structures.

```python
from pydantic import BaseModel, field_validator
from valid8r.core import parsers, validators
from valid8r.integrations.pydantic import validator_from_parser

class Product(BaseModel):
    name: str
    price: int

    @field_validator('price', mode='before')
    @classmethod
    def validate_price(cls, v):
        # Parse as int and validate range (price in cents: $0.01 - $100.00)
        parser = lambda value: parsers.parse_int(value).bind(validators.between(1, 10000))
        return validator_from_parser(parser)(v)

class CartItem(BaseModel):
    product: Product
    quantity: int

    @field_validator('quantity', mode='before')
    @classmethod
    def validate_quantity(cls, v):
        parser = lambda value: parsers.parse_int(value).bind(validators.minimum(1))
        return validator_from_parser(parser)(v)

class Cart(BaseModel):
    items: list[CartItem]

# Valid cart with nested validation
cart = Cart(items=[
    {'product': {'name': 'Widget', 'price': '999'}, 'quantity': '2'},
    {'product': {'name': 'Gadget', 'price': '499'}, 'quantity': '1'}
])

# Invalid: price out of range
try:
    Cart(items=[
        {'product': {'name': 'Expensive', 'price': '999999'}, 'quantity': '1'}
    ])
except ValidationError as e:
    errors = e.errors()
    print(errors[0]['loc'])  # ('items', 0, 'product', 'price')
    print(errors[0]['msg'])  # Contains "between 1 and 10000"
```

### Custom Error Messages

Use the `error_prefix` parameter to customize error messages for better user feedback.

```python
from pydantic import BaseModel, field_validator
from valid8r.core import parsers
from valid8r.integrations.pydantic import validator_from_parser

class ServerConfig(BaseModel):
    host: str
    port: int
    max_connections: int

    @field_validator('port', mode='before')
    @classmethod
    def validate_port(cls, v):
        return validator_from_parser(
            parsers.parse_int,
            error_prefix='Port number'
        )(v)

    @field_validator('max_connections', mode='before')
    @classmethod
    def validate_max_connections(cls, v):
        return validator_from_parser(
            parsers.parse_int,
            error_prefix='Max connections'
        )(v)

# Errors include custom prefixes
try:
    ServerConfig(host='localhost', port='invalid', max_connections='100')
except ValidationError as e:
    print(e)  # "Port number: ..." appears in error
```

## FastAPI Integration

Use valid8r parsers in FastAPI request validation for consistent validation across your API.

```python
from fastapi import FastAPI
from pydantic import BaseModel, field_validator
from valid8r.core import parsers, validators
from valid8r.core.parsers import EmailAddress, PhoneNumber
from valid8r.integrations.pydantic import validator_from_parser

app = FastAPI()

class Address(BaseModel):
    street: str
    city: str
    phone: PhoneNumber

    @field_validator('phone', mode='before')
    @classmethod
    def validate_phone(cls, v):
        return validator_from_parser(parsers.parse_phone)(v)

class UserCreate(BaseModel):
    name: str
    email: EmailAddress
    age: int
    address: Address

    @field_validator('email', mode='before')
    @classmethod
    def validate_email(cls, v):
        return validator_from_parser(parsers.parse_email)(v)

    @field_validator('age', mode='before')
    @classmethod
    def validate_age(cls, v):
        parser = lambda value: parsers.parse_int(value).bind(validators.between(0, 120))
        return validator_from_parser(parser)(v)

@app.post('/users/')
async def create_user(user: UserCreate):
    return {
        'name': user.name,
        'email': str(user.email),
        'age': user.age,
        'phone': str(user.address.phone)
    }

# FastAPI automatically validates requests:
# POST /users/
# {
#   "name": "Alice",
#   "email": "alice@example.com",
#   "age": "25",
#   "address": {
#     "street": "123 Main St",
#     "city": "Seattle",
#     "phone": "(206) 234-5678"
#   }
# }
# → Success

# Invalid phone number returns 422 with field path:
# POST /users/
# {
#   "name": "Bob",
#   "email": "bob@example.com",
#   "age": "30",
#   "address": {
#     "street": "456 Elm St",
#     "city": "Portland",
#     "phone": "invalid"
#   }
# }
# → 422 Unprocessable Entity
# {
#   "detail": [{
#     "loc": ["body", "address", "phone"],
#     "msg": "...",
#     "type": "value_error"
#   }]
# }
```

## Error Handling

### Field Path Reporting

Pydantic automatically includes the full field path in validation errors, making it easy to identify which field failed validation in nested structures.

```python
from pydantic import ValidationError

# Field paths for different nesting levels:
# 'phone' → Top-level field
# ('address', 'phone') → Nested one level
# ('items', 0, 'quantity') → List item field
# ('engineering', 'lead', 'email') → Three levels deep

try:
    Company(engineering={'lead': {'email': 'invalid'}})
except ValidationError as e:
    for error in e.errors():
        print(f"Field: {'.'.join(str(p) for p in error['loc'])}")
        print(f"Error: {error['msg']}")
        print(f"Type: {error['type']}")
```

### Extracting Error Messages

```python
from pydantic import ValidationError

try:
    user = User(age='999', email='invalid')
except ValidationError as e:
    # Get all errors
    errors = e.errors()

    # Pretty-print for debugging
    print(e)

    # JSON format for API responses
    print(e.json())

    # Dict format for programmatic access
    for error in errors:
        field = '.'.join(str(part) for part in error['loc'])
        message = error['msg']
        print(f'{field}: {message}')
```

## Best Practices

### 1. Use `mode='before'` for Parsers

Always use `mode='before'` with `@field_validator` when using valid8r parsers. This ensures the parser receives the raw input (usually a string) before Pydantic's type coercion.

```python
class User(BaseModel):
    age: int

    @field_validator('age', mode='before')  # ← Important!
    @classmethod
    def validate_age(cls, v):
        return validator_from_parser(parsers.parse_int)(v)
```

### 2. Return Parsed Values, Not Maybe

`validator_from_parser()` handles the `Maybe` unwrapping for you. The validator function returns the parsed value directly or raises `ValueError` on failure.

```python
# Good - validator_from_parser handles Maybe
@field_validator('age', mode='before')
@classmethod
def validate_age(cls, v):
    return validator_from_parser(parsers.parse_int)(v)

# Bad - don't manually unwrap Maybe
@field_validator('age', mode='before')
@classmethod
def validate_age(cls, v):
    result = parsers.parse_int(v)
    if result.is_success():
        return result.value_or(None)
    raise ValueError(result.error_or('Unknown error'))
```

### 3. Use Type Hints for Structured Types

Use valid8r's structured types (`EmailAddress`, `PhoneNumber`, `UrlParts`) as type hints to make the structure explicit.

```python
from valid8r.core.parsers import EmailAddress, PhoneNumber

class Contact(BaseModel):
    email: EmailAddress  # ← Clear type hint
    phone: PhoneNumber   # ← Clear type hint

    @field_validator('email', mode='before')
    @classmethod
    def validate_email(cls, v):
        return validator_from_parser(parsers.parse_email)(v)

    @field_validator('phone', mode='before')
    @classmethod
    def validate_phone(cls, v):
        return validator_from_parser(parsers.parse_phone)(v)
```

### 4. Combine Validators Using Bind

Use valid8r's monadic `bind` for chaining parsers and validators.

```python
@field_validator('age', mode='before')
@classmethod
def validate_age(cls, v):
    # Parse and validate in one pipeline
    parser = lambda value: parsers.parse_int(value).bind(validators.between(0, 120))
    return validator_from_parser(parser)(v)
```

### 5. Provide Meaningful Error Prefixes

Use `error_prefix` to make error messages more user-friendly.

```python
class Config(BaseModel):
    db_port: int
    redis_port: int

    @field_validator('db_port', mode='before')
    @classmethod
    def validate_db_port(cls, v):
        return validator_from_parser(
            parsers.parse_int,
            error_prefix='Database port'
        )(v)

    @field_validator('redis_port', mode='before')
    @classmethod
    def validate_redis_port(cls, v):
        return validator_from_parser(
            parsers.parse_int,
            error_prefix='Redis port'
        )(v)
```

## Comparison with Native Pydantic Validators

### valid8r Advantages

1. **Reusable Parsers**: Write once, use everywhere (CLI, API, config files)
2. **Explicit Error Handling**: `Maybe` pattern makes success/failure explicit
3. **Functional Composition**: Chain validators using monadic operations
4. **Structured Types**: Rich result types (`EmailAddress`, `PhoneNumber`, etc.)
5. **Comprehensive Parsers**: Phone numbers, URLs, UUIDs with version validation, etc.

### When to Use Native Pydantic

- Simple type coercion (string to int, etc.)
- Pydantic-specific features (computed fields, serialization)
- When you don't need valid8r's additional validation logic

### Hybrid Approach

Mix native Pydantic validators with valid8r for best results:

```python
class User(BaseModel):
    username: str  # Native Pydantic (simple string)
    email: EmailAddress  # valid8r parser (complex validation)

    # Native Pydantic validator
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        return v

    # valid8r parser
    @field_validator('email', mode='before')
    @classmethod
    def validate_email(cls, v):
        return validator_from_parser(parsers.parse_email)(v)
```

## Troubleshooting

### "Expected X, got Y" Type Errors

Make sure to use `mode='before'` so the parser receives raw input:

```python
# Problem: mode='after' causes type errors
@field_validator('age', mode='after')  # ← Wrong
@classmethod
def validate_age(cls, v):
    return validator_from_parser(parsers.parse_int)(v)

# Solution: mode='before' to parse raw input
@field_validator('age', mode='before')  # ← Correct
@classmethod
def validate_age(cls, v):
    return validator_from_parser(parsers.parse_int)(v)
```

### ValidationError Not Raised

Ensure the validator function returns a value (success) or raises `ValueError` (failure). `validator_from_parser()` handles this automatically.

```python
# validator_from_parser handles error raising
@field_validator('age', mode='before')
@classmethod
def validate_age(cls, v):
    return validator_from_parser(parsers.parse_int)(v)  # ← Correct
```

### Field Path Missing in Errors

Pydantic automatically includes field paths. If paths seem wrong, check your model structure and validator placement.

## API Reference

See the [API documentation](../api/integrations/pydantic.html) for detailed information about `validator_from_parser()` and all parameters.

## Further Reading

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [valid8r Parsers](../api/parsers.html)
- [valid8r Validators](../api/validators.html)
