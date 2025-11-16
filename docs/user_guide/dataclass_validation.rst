Dataclass Field Validation
===========================

The ``valid8r.integrations.dataclasses`` module provides a clean, declarative way to validate dataclass fields using Valid8r's validators and automatic type coercion.

.. contents:: Table of Contents
   :local:
   :depth: 2

Quick Start
-----------

Use the ``@validate`` decorator to add validation to your dataclasses:

.. code-block:: python

    from dataclasses import dataclass, field
    from valid8r.integrations.dataclasses import validate
    from valid8r.core.validators import minimum, maximum, length

    @validate
    @dataclass
    class Product:
        name: str = field(metadata={'validator': length(1, 100)})
        price: float = field(metadata={'validator': minimum(0.0)})
        quantity: int = field(metadata={'validator': minimum(0) & maximum(1000)})

    # Validate and construct from dictionary
    result = Product.from_dict({
        'name': 'Laptop',
        'price': '999.99',  # Automatically coerced from string
        'quantity': 5
    })

    match result:
        case Success(product):
            print(f"{product.name}: ${product.price} ({product.quantity} in stock)")
        case Failure(error):
            print(f"Validation failed: {error}")

Key Features
------------

1. **Field-Level Validation**
   - Validators specified in field metadata
   - Clear separation between data structure and validation logic

2. **Automatic Type Coercion**
   - Strings automatically parsed to ``int``, ``float``, ``bool``
   - Nested dataclasses validated recursively
   - Type-safe with full type hint support

3. **Error Aggregation**
   - All field errors collected before returning
   - Comprehensive error messages with field names
   - Fail-fast for construction errors

4. **Pattern Matching Support**
   - Returns ``Maybe[T]`` for idiomatic error handling
   - Use Python 3.10+ pattern matching with ``match/case``
   - Compatible with all Valid8r validators

Field Validation Basics
------------------------

Add validators to fields using the ``metadata`` parameter:

.. code-block:: python

    from dataclasses import dataclass, field
    from valid8r.integrations.dataclasses import validate
    from valid8r.core.validators import minimum, maximum, length, matches_regex

    @validate
    @dataclass
    class User:
        username: str = field(metadata={'validator': length(3, 20)})
        age: int = field(metadata={'validator': minimum(0) & maximum(120)})
        email: str = field(metadata={'validator': matches_regex(r'^[\w\.-]+@[\w\.-]+\.\w+$')})

Type Coercion
-------------

Valid8r automatically coerces string values to match field types:

.. code-block:: python

    @validate
    @dataclass
    class Config:
        port: int
        timeout: float
        debug: bool

    result = Config.from_dict({
        'port': '8080',      # String → int
        'timeout': '30.5',   # String → float
        'debug': 'true'      # String → bool
    })
    # Success(Config(port=8080, timeout=30.5, debug=True))

Supported type coercions:

- ``int``: Parses decimal, hex (``0x``), octal (``0o``), binary (``0b``)
- ``float``: Handles scientific notation, infinity, NaN
- ``bool``: Accepts "true", "false", "yes", "no", "1", "0" (case-insensitive)
- ``str``: No coercion needed

Nested Dataclasses
------------------

Nested dataclasses are automatically validated recursively:

.. code-block:: python

    @dataclass
    class Address:
        street: str
        city: str
        zip_code: str = field(metadata={'validator': matches_regex(r'^\d{5}$')})

    @validate
    @dataclass
    class Person:
        name: str = field(metadata={'validator': length(1, 100)})
        address: Address

    result = Person.from_dict({
        'name': 'Alice Smith',
        'address': {
            'street': '123 Main St',
            'city': 'Portland',
            'zip_code': '97201'
        }
    })

    match result:
        case Success(person):
            print(f"{person.name} lives in {person.address.city}")
        case Failure(error):
            # Error messages include nested field paths: "address.zip_code: must be 5 digits"
            print(error)

Optional Fields
---------------

Fields with default values or ``Optional`` types work as expected:

.. code-block:: python

    from typing import Optional

    @validate
    @dataclass
    class Article:
        title: str = field(metadata={'validator': length(1, 200)})
        summary: Optional[str] = None
        published: bool = False

    # All of these are valid:
    Article.from_dict({'title': 'Hello World'})  # Uses defaults
    Article.from_dict({'title': 'Hello', 'summary': None})  # Explicit None
    Article.from_dict({'title': 'Hello', 'summary': 'Brief'})  # With value

Combining Validators
--------------------

Use validator combinators to build complex validation logic:

.. code-block:: python

    from valid8r.core.validators import minimum, maximum, length, matches_regex

    @validate
    @dataclass
    class Password:
        value: str = field(metadata={
            'validator': (
                length(8, 128) &  # Must be 8-128 characters
                matches_regex(r'[A-Z]') &  # Must have uppercase
                matches_regex(r'[a-z]') &  # Must have lowercase
                matches_regex(r'[0-9]')    # Must have digit
            )
        })

Error Handling
--------------

All field errors are aggregated and returned together:

.. code-block:: python

    @validate
    @dataclass
    class Product:
        name: str = field(metadata={'validator': length(1, 100)})
        price: float = field(metadata={'validator': minimum(0.0)})

    result = Product.from_dict({
        'name': '',        # Too short
        'price': '-10.0'   # Negative
    })

    # Failure('name: must have length between 1 and 100; price: must be >= 0.0')

Custom Validators
-----------------

Any function that returns ``Maybe[T]`` can be used as a validator:

.. code-block:: python

    from valid8r.core.maybe import Maybe

    def validate_email_domain(allowed_domain: str):
        """Create a validator that checks email domain."""
        def validator(email: str) -> Maybe[str]:
            if email.endswith(f'@{allowed_domain}'):
                return Maybe.success(email)
            return Maybe.failure(f'must be {allowed_domain} email')
        return validator

    @validate
    @dataclass
    class Employee:
        email: str = field(metadata={'validator': validate_email_domain('company.com')})

    Employee.from_dict({'email': 'alice@company.com'})  # Success
    Employee.from_dict({'email': 'bob@gmail.com'})     # Failure

Working with Collections
-------------------------

Validate list and dict fields using custom validators:

.. code-block:: python

    from typing import List
    from valid8r.core.validators import unique_items

    @validate
    @dataclass
    class Team:
        members: List[str] = field(metadata={'validator': unique_items()})

    Team.from_dict({'members': ['Alice', 'Bob', 'Carol']})  # Success
    Team.from_dict({'members': ['Alice', 'Bob', 'Alice']})  # Failure: duplicates

Direct Validation Function
---------------------------

For cases where you don't want to modify the dataclass definition, use ``validate_dataclass`` directly:

.. code-block:: python

    from dataclasses import dataclass, field
    from valid8r.integrations.dataclasses import validate_dataclass
    from valid8r.core.validators import minimum

    @dataclass
    class Point:
        x: int = field(metadata={'validator': minimum(0)})
        y: int = field(metadata={'validator': minimum(0)})

    result = validate_dataclass(Point, {'x': 10, 'y': 20})

Integration with from_type (Future)
------------------------------------

.. note::
   This feature depends on PR #196 (from_type integration) and is not yet available.

Once PR #196 merges, the dataclass integration will automatically use ``from_type()``
for type coercion instead of the limited built-in parsers. This will enable:

- Automatic coercion for all types supported by ``from_type()``
- Network types: IPv4, IPv6, CIDR, URL, email
- Date/time types: datetime, date, time
- UUID types with version validation
- Enum types
- Complex and Decimal numbers

Example (after #196 merges):

.. code-block:: python

    from datetime import datetime
    from ipaddress import IPv4Address
    from uuid import UUID

    @validate
    @dataclass
    class Request:
        timestamp: datetime  # Will auto-parse ISO 8601 strings
        client_ip: IPv4Address  # Will parse "192.168.1.1"
        request_id: UUID  # Will parse UUID strings

Best Practices
--------------

1. **Order decorators correctly**: ``@validate`` must come before ``@dataclass``

   .. code-block:: python

       @validate  # First
       @dataclass  # Second
       class MyClass:
           ...

2. **Use specific validators**: Be explicit about constraints

   .. code-block:: python

       # Good: Clear constraints
       age: int = field(metadata={'validator': minimum(0) & maximum(120)})

       # Less clear: No constraints
       age: int

3. **Validate at boundaries**: Use ``from_dict()`` when receiving untrusted input

   .. code-block:: python

       def create_user(request_data: dict):
           result = User.from_dict(request_data)
           match result:
               case Success(user):
                   # Save to database
                   return user
               case Failure(error):
                   # Return 400 Bad Request
                   raise ValueError(error)

4. **Combine with Pydantic for APIs**: Use dataclasses for domain models, Pydantic for API schemas

5. **Test validators separately**: Unit test custom validators before using in dataclasses

API Reference
-------------

.. autofunction:: valid8r.integrations.dataclasses.validate
.. autofunction:: valid8r.integrations.dataclasses.validate_dataclass

See Also
--------

- :doc:`/user_guide/validators` - Available validators
- :doc:`/user_guide/pattern_matching` - Using Maybe with match/case
- :doc:`/api/integrations` - Full API documentation
