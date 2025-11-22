=======================
Type-Based Parsers
=======================

Overview
========

Valid8r provides automatic parser generation from Python type annotations using the ``from_type()`` function.
This enables type-safe parsing with minimal boilerplate, leveraging Python's type system to automatically
create appropriate parser functions.

The ``from_type()`` function uses pattern matching to introspect type annotations and automatically generate
parsers that return ``Maybe[T]`` results, maintaining the same error handling philosophy as the rest of Valid8r.

Basic Usage
===========

Simple Types
------------

Generate parsers for basic Python types::

    from valid8r.core.type_adapters import from_type

    # Integer parser
    int_parser = from_type(int)
    result = int_parser('42')
    # Success(42)

    # String parser
    str_parser = from_type(str)
    result = str_parser('hello')
    # Success('hello')

    # Float parser
    float_parser = from_type(float)
    result = float_parser('3.14')
    # Success(3.14)

    # Boolean parser
    bool_parser = from_type(bool)
    result = bool_parser('true')
    # Success(True)

Optional Types
--------------

Handle optional values elegantly with automatic ``None`` handling::

    from typing import Optional

    # Optional integer parser
    parser = from_type(Optional[int])

    # Parse valid integer
    result = parser('42')
    # Success(42)

    # Empty string becomes None
    result = parser('')
    # Success(None)

    # Invalid input still fails
    result = parser('invalid')
    # Failure('Expected a valid integer')

Collection Types
================

Lists
-----

Parse and validate JSON arrays with element type checking::

    # List of integers
    parser = from_type(list[int])
    result = parser('[1, 2, 3, 4, 5]')
    # Success([1, 2, 3, 4, 5])

    # Validates each element
    result = parser('[1, "invalid", 3]')
    # Failure('Failed to parse element 2: Expected a valid integer')

    # Nested lists
    parser = from_type(list[list[int]])
    result = parser('[[1, 2], [3, 4]]')
    # Success([[1, 2], [3, 4]])

Dictionaries
------------

Parse and validate JSON objects with typed keys and values::

    # String keys, integer values
    parser = from_type(dict[str, int])
    result = parser('{"age": 30, "count": 5}')
    # Success({'age': 30, 'count': 5})

    # Validates both keys and values
    result = parser('{"age": "thirty"}')
    # Failure('Failed to parse value for key "age": Expected a valid integer')

    # Nested structures
    parser = from_type(dict[str, list[int]])
    result = parser('{"scores": [95, 87, 92]}')
    # Success({'scores': [95, 87, 92]})

Sets
----

Parse JSON arrays and convert to Python sets::

    parser = from_type(set[str])
    result = parser('["a", "b", "c", "a"]')
    # Success({'a', 'b', 'c'})  # Duplicates removed

Union Types
===========

Try multiple types in order until one succeeds::

    from typing import Union

    # Try int, then float, then str
    parser = from_type(Union[int, float, str])

    result = parser('42')
    # Success(42)  # Parsed as int

    result = parser('3.14')
    # Success(3.14)  # Parsed as float

    result = parser('hello')
    # Success('hello')  # Parsed as str

Literal Types
=============

Restrict values to specific literals::

    from typing import Literal

    # Color choices
    parser = from_type(Literal['red', 'green', 'blue'])

    result = parser('red')
    # Success('red')

    result = parser('yellow')
    # Failure('Value must be one of: 'red', 'green', 'blue'')

    # Mixed type literals
    parser = from_type(Literal[1, 'one', True])
    result = parser('1')
    # Success(1)

Enum Types
==========

Parse enum values with case-insensitive matching::

    from enum import Enum

    class Status(Enum):
        ACTIVE = 'active'
        INACTIVE = 'inactive'
        PENDING = 'pending'

    parser = from_type(Status)

    # Case-insensitive matching
    result = parser('ACTIVE')
    # Success(Status.ACTIVE)

    result = parser('active')
    # Success(Status.ACTIVE)

    result = parser('invalid')
    # Failure('Expected a valid enumeration value')

Annotated Types with Validators
================================

Combine type parsing with validation::

    from typing import Annotated
    from valid8r import validators

    # Integer with range validation
    parser = from_type(Annotated[int, validators.minimum(0), validators.maximum(100)])

    result = parser('50')
    # Success(50)

    result = parser('150')
    # Failure('Value must be at most 100')

    result = parser('-5')
    # Failure('Value must be at least 0')

    # String with length validation
    parser = from_type(Annotated[str, validators.length(3, 10)])

    result = parser('hello')
    # Success('hello')

    result = parser('hi')
    # Failure('String must have at least 3 characters')

Advanced Usage
==============

Nested Complex Types
--------------------

Combine multiple type features::

    from typing import Optional, Annotated

    # List of optional integers with validation
    parser = from_type(list[Optional[Annotated[int, validators.minimum(0)]]])

    result = parser('[1, null, 5, 10]')
    # Success([1, None, 5, 10])

    # Dict with validated values
    parser = from_type(dict[str, Annotated[int, validators.minimum(0), validators.maximum(100)]])

    result = parser('{"score": 95, "grade": 87}')
    # Success({'score': 95, 'grade': 87})

Reusable Type Aliases
----------------------

Define complex types once and reuse them::

    from typing import TypeAlias

    # Define reusable types
    Score: TypeAlias = Annotated[int, validators.minimum(0), validators.maximum(100)]
    Scores: TypeAlias = dict[str, list[Score]]

    # Use the alias
    parser = from_type(Scores)
    result = parser('{"math": [95, 87, 92], "english": [88, 91]}')
    # Success({'math': [95, 87, 92], 'english': [88, 91]})

Security Considerations
=======================

DoS Protection
--------------

All collection parsers include automatic protection against Denial-of-Service (DoS) attacks
through input length validation. Inputs exceeding 100KB (100,000 characters) are rejected
immediately before expensive JSON parsing::

    # This malicious input is rejected in <10ms
    malicious_input = '[' + '1,' * 100_000 + '1]'
    parser = from_type(list[int])
    result = parser(malicious_input)
    # Failure('Input too large: maximum 100000 characters')

Input Validation Best Practices
--------------------------------

1. Always validate untrusted input before parsing
2. Use appropriate type annotations to enforce structure
3. Add validators to Annotated types for business logic constraints
4. Consider using Optional for fields that may be absent
5. Use Union types sparingly - specific types are safer

Limitations
===========

Unsupported Types
-----------------

The following types are not supported:

* ``Callable`` - Function types cannot be parsed from strings
* ``TypedDict`` - Use dataclass integration instead (see :doc:`dataclasses`)
* ``Protocol`` - Structural subtyping not supported
* Custom generic types - Only built-in generics supported

Error Messages
--------------

Error messages are designed to be user-friendly and indicate the specific problem:

* Invalid input: ``"Expected a valid integer"``
* Type mismatch: ``"Expected a JSON array"``
* Element validation: ``"Failed to parse element 3: Expected a valid integer"``
* Size limits: ``"Input too large: maximum 100000 characters"``

See Also
========

* :doc:`parsers` - Individual parser functions
* :doc:`validators` - Validation functions for use with Annotated
* :doc:`schema` - Schema-based validation for structured data
* :doc:`maybe_monad` - Understanding Maybe[T] results
