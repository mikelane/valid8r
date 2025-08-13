Parsers
=======

Parsers are functions that convert string inputs into other data types, returning Maybe objects to handle potential parsing errors.

Basic Usage
-----------

.. code-block:: python

   from valid8r import parsers

   # Parse a string to an integer
   result = parsers.parse_int("42")
   match result:
       case Success(value):
           print(f"Parsed integer: {value}")  # Parsed integer: 42
       case Failure(error):
           print(f"Error: {error}")

   # Parse a string to a float
   result = parsers.parse_float("3.14")
   match result:
       case Success(value):
           print(f"Parsed float: {value}")  # Parsed float: 3.14
       case Failure(error):
           print(f"Error: {error}")

Available Parsers
-----------------

Valid8r includes parsers for several common data types:

Integer Parser
~~~~~~~~~~~~~~

.. code-block:: python

   from valid8r import parsers
   from valid8r.core.maybe import Success, Failure

   # Basic usage
   result = parsers.parse_int("42")
   match result:
       case Success(value):
           print(value)  # 42
       case Failure(_):
           print("This won't happen")

   # Custom error message
   result = parsers.parse_int("abc", error_message="Please enter a valid number")
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "Please enter a valid number"

   # Handles whitespace
   result = parsers.parse_int("  42  ")
   match result:
       case Success(value):
           print(value)  # 42
       case Failure(_):
           print("This won't happen")

   # Parses integers with integer-equivalent float notation
   result = parsers.parse_int("42.0")
   match result:
       case Success(value):
           print(value)  # 42
       case Failure(_):
           print("This won't happen")

Float Parser
~~~~~~~~~~~~

.. code-block:: python

   from valid8r import parsers
   from valid8r.core.maybe import Success, Failure

   # Basic usage
   result = parsers.parse_float("3.14")
   match result:
       case Success(value):
           print(value)  # 3.14
       case Failure(_):
           print("This won't happen")

   # Scientific notation
   result = parsers.parse_float("1.23e-4")
   match result:
       case Success(value):
           print(value)  # 0.000123
       case Failure(_):
           print("This won't happen")

   # Handles whitespace
   result = parsers.parse_float("  3.14  ")
   match result:
       case Success(value):
           print(value)  # 3.14
       case Failure(_):
           print("This won't happen")

   # Integer as float
   result = parsers.parse_float("42")
   match result:
       case Success(value):
           print(value)  # 42.0
       case Failure(_):
           print("This won't happen")

Boolean Parser
~~~~~~~~~~~~~~

.. code-block:: python

   from valid8r import parsers
   from valid8r.core.maybe import Success, Failure

   # Parse various true values
   true_values = ["true", "True", "TRUE", "t", "T", "yes", "y", "1"]
   for value in true_values:
       result = parsers.parse_bool(value)
       match result:
           case Success(value):
               assert value is True  # All parse to True
           case Failure(_):
               print("This won't happen")

   # Parse various false values
   false_values = ["false", "False", "FALSE", "f", "F", "no", "n", "0"]
   for value in false_values:
       result = parsers.parse_bool(value)
       match result:
           case Success(value):
               assert value is False  # All parse to False
           case Failure(_):
               print("This won't happen")

   # Parse invalid boolean string
   result = parsers.parse_bool("maybe")
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "Input must be a valid boolean"

Date Parser
~~~~~~~~~~~

.. code-block:: python

   from valid8r import parsers
   from valid8r.core.maybe import Success, Failure
   from datetime import date

   # ISO format (default)
   result = parsers.parse_date("2023-01-15")
   match result:
       case Success(value):
           print(value)  # date(2023, 1, 15)
       case Failure(_):
           print("This won't happen")

   # Custom format
   result = parsers.parse_date("15/01/2023", date_format="%d/%m/%Y")
   match result:
       case Success(value):
           print(value)  # date(2023, 1, 15)
       case Failure(_):
           print("This won't happen")

   # Process date attributes
   result = parsers.parse_date("Jan 15, 2023", date_format="%b %d, %Y")
   match result:
       case Success(value):
           print(f"Year: {value.year}, Month: {value.month}, Day: {value.day}")
       case Failure(_):
           print("This won't happen")

Complex Number Parser
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from valid8r import parsers
   from valid8r.core.maybe import Success, Failure

   # Standard notation
   result = parsers.parse_complex("3+4j")
   match result:
       case Success(value):
           print(value)  # (3+4j)
       case Failure(_):
           print("This won't happen")

   # Alternative notation
   result = parsers.parse_complex("3+4i")
   match result:
       case Success(value):
           print(value)  # (3+4j)
       case Failure(_):
           print("This won't happen")

   # Just real part
   result = parsers.parse_complex("5")
   match result:
       case Success(value):
           print(value)  # (5+0j)
       case Failure(_):
           print("This won't happen")

   # Just imaginary part
   result = parsers.parse_complex("3j")
   match result:
       case Success(value):
           print(value)  # (0+3j)
       case Failure(_):
           print("This won't happen")

Enum Parser
~~~~~~~~~~~

.. code-block:: python

   from enum import Enum
   from valid8r import parsers
   from valid8r.core.maybe import Success, Failure

   # Define an enum
   class Color(Enum):
       RED = "RED"
       GREEN = "GREEN"
       BLUE = "BLUE"

   # Parse to enum
   result = parsers.parse_enum("RED", Color)
   match result:
       case Success(value):
           print(value == Color.RED)  # True
       case Failure(_):
           print("This won't happen")

   # Invalid enum value
   result = parsers.parse_enum("YELLOW", Color)
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "Input must be a valid enumeration value"

Collection Type Parsing
-----------------------

Valid8r supports parsing strings into collection types like lists and dictionaries:

.. code-block:: python

   from valid8r import parsers
   from valid8r.core.maybe import Success, Failure

   # Parse a string to a list of integers
   result = parsers.parse_list("1,2,3", element_parser=parsers.parse_int)
   match result:
       case Success(value):
           print(f"Parsed list: {value}")  # Parsed list: [1, 2, 3]
       case Failure(error):
           print(f"Error: {error}")

   # Parse with custom separator
   result = parsers.parse_list("1|2|3", element_parser=parsers.parse_int, separator="|")
   match result:
       case Success(value):
           print(f"Parsed list: {value}")  # Parsed list: [1, 2, 3]
       case Failure(error):
           print(f"Error: {error}")

   # Parse a string to a dictionary
   result = parsers.parse_dict("name:John,age:30",
                               value_parser=parsers.parse_int)
   match result:
       case Success(value):
           print(f"Parsed dict: {value}")  # Parsed dict: {'name': 'John', 'age': 30}
       case Failure(error):
           print(f"Error: {error}")

   # Parse a set (removes duplicates)
   result = parsers.parse_set("1,2,3,2,1", element_parser=parsers.parse_int)
   match result:
       case Success(value):
           print(f"Parsed set: {value}")  # Parsed set: {1, 2, 3}
       case Failure(error):
           print(f"Error: {error}")

IP Address and CIDR Parsers
---------------------------

Valid8r provides built-in helpers for parsing IPv4, IPv6, generic IP addresses, and CIDR networks using Python's ``ipaddress``.

.. code-block:: python

   from valid8r.core.maybe import Success, Failure
   from valid8r import parsers

   # IPv4
   match parsers.parse_ipv4("192.168.0.1"):
       case Success(addr):
           print(addr)  # 192.168.0.1
       case Failure(error):
           print(error)

   # IPv6 (normalized to canonical form)
   match parsers.parse_ipv6("2001:db8:0:0:0:0:2:1"):
       case Success(addr):
           print(addr)  # 2001:db8::2:1
       case Failure(error):
           print(error)

   # Generic IP (either IPv4 or IPv6)
   match parsers.parse_ip("::1"):
       case Success(addr):
           print(type(addr), addr)  # <class 'ipaddress.IPv6Address'> ::1
       case Failure(error):
           print(error)

   # CIDR networks (strict by default)
   match parsers.parse_cidr("10.0.0.0/8"):
       case Success(net):
           print(net)  # 10.0.0.0/8
       case Failure(error):
           print(error)

   # Non-strict CIDR masks host bits instead of failing
   match parsers.parse_cidr("10.0.0.1/24", strict=False):
       case Success(net):
           print(net)  # 10.0.0.0/24
       case Failure(error):
           print(error)

Error messages are short and deterministic:

- "value must be a string" for non-string inputs
- "value is empty" for empty strings
- "not a valid IPv4 address" or "not a valid IPv6 address" for address-specific failures
- "not a valid IP address" for generic IP failures
- "not a valid network" for invalid CIDR/prefix formats
- "has host bits set" when strict CIDR parsing is enabled and input contains host bits

Creating Custom Parsers
------------------------

Valid8r offers two approaches for creating custom parsers:

Using the ``create_parser`` Function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``create_parser`` function allows you to create a parser from any function that converts a string to another type:

.. code-block:: python

   from valid8r.core.parsers import create_parser
   from valid8r.core.maybe import Maybe, Success, Failure
   # You can still create custom parsers with create_parser for other types.

   # Parse a string to an IP address
   # (Built-in helpers exist: parse_ipv4/parse_ipv6/parse_ip/parse_cidr)
   result = create_parser(int, "Not a valid integer")("123")
   match result:
       case Success(value):
           print(f"Parsed: {value}")  # Parsed: 123
       case Failure(error):
           print(f"Error: {error}")

Using the ``make_parser`` Decorator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``make_parser`` decorator converts a function into a parser:

.. code-block:: python

   from valid8r.core.parsers import make_parser
   from decimal import Decimal

   # Create a parser using the decorator
   @make_parser
   def parse_decimal(s: str) -> Decimal:
       return Decimal(s)

   # Parse with custom error message
   @make_parser
   def parse_percentage(s: str) -> float:
       value = float(s.strip('%')) / 100
       return value

   # Use the parsers
   result = parse_decimal("42.5")
   match result:
       case Success(value):
           print(f"Parsed decimal: {value}")  # Parsed decimal: 42.5
       case Failure(error):
           print(f"Error: {error}")

   result = parse_percentage("75%")
   match result:
       case Success(value):
           print(f"Parsed percentage: {value}")  # Parsed percentage: 0.75
       case Failure(error):
           print(f"Error: {error}")

Validated Parsers
----------------

For cases where you want to combine parsing and validation in a single step:

.. code-block:: python

   from valid8r.core.parsers import validated_parser
   from valid8r.core.validators import minimum, maximum
   from decimal import Decimal

   # Create a parser that only accepts positive numbers
   positive_decimal = validated_parser(
       Decimal,  # Convert function
       lambda x: minimum(Decimal('0'))(x),  # Validator function
       "Not a valid positive decimal"  # Error message
   )

   # Use the validated parser
   result = positive_decimal("42.5")  # Valid
   match result:
       case Success(value):
           print(f"Valid positive decimal: {value}")  # Valid positive decimal: 42.5
       case Failure(error):
           print(f"Error: {error}")

   result = positive_decimal("-10.5")  # Invalid
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(f"Error: {error}")  # Error: Value must be at least 0

Error Handling
--------------

All parsers follow consistent error handling patterns:

1. If the input is empty, the error is "Input must not be empty"
2. If the input cannot be parsed, a type-specific error is returned (e.g., "Input must be a valid integer")
3. You can provide a custom error message to override the default ones

.. code-block:: python

   from valid8r import parsers
   from valid8r.core.maybe import Success, Failure

   # Empty input
   result = parsers.parse_int("")
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "Input must not be empty"

   # Invalid input
   result = parsers.parse_int("abc")
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "Input must be a valid integer"

   # Custom error message
   result = parsers.parse_int("abc", error_message="Please enter a number")
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "Please enter a number"

Common Parser Features
----------------------

All parsers have these common features:

1. **Whitespace handling**: Leading and trailing whitespace is automatically removed
2. **Maybe return value**: All parsers return a Maybe object that can be pattern matched
3. **Custom error messages**: All parsers accept an optional error_message parameter
4. **Empty input handling**: All parsers check for empty input first

Combining Parsers with Validators
---------------------------------

Parsers are often used together with validators to create a complete validation pipeline:

.. code-block:: python

   from valid8r import parsers, validators
   from valid8r.core.maybe import Success, Failure

   # Parse a string to an integer, then validate it's positive
   result = parsers.parse_int("42").bind(
       lambda x: validators.minimum(0)(x)
   )

   match result:
       case Success(value):
           print(f"Valid positive number: {value}")  # Valid positive number: 42
       case Failure(error):
           print(f"Error: {error}")

   # Parse a string to a date, then validate it's in the future
   from datetime import date

   def is_future_date(d):
       if d > date.today():
           return Maybe.success(d)
       return Maybe.failure("Date must be in the future")

   result = parsers.parse_date("2025-01-01").bind(is_future_date)

   match result:
       case Success(value):
           print(f"Valid future date: {value}")  # Valid future date: 2025-01-01
       case Failure(error):
           print(f"Error: {error}")

Parser Function Errors vs Validation Logic
------------------------------------------

When deciding between handling errors in parser functions versus validation logic:

.. code-block:: python

   from valid8r import parsers, validators
   from valid8r.core.maybe import Success, Failure

   # Approach 1: Handle it in the parser directly
   result = parsers.parse_int("42.5")  # Will fail because it's not an integer
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "Input must be a valid integer"

   # Approach 2: Parse as float, then validate it's an integer
   def validate_integer_value(x):
       if x.is_integer():
           return Maybe.success(int(x))
       return Maybe.failure("Value must be an integer")

   result = parsers.parse_float("42.5").bind(validate_integer_value)
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "Value must be an integer"

Parsing with Validation
-----------------------

Valid8r provides parser functions with built-in validation:

.. code-block:: python

   from valid8r import parsers
   from valid8r.core.maybe import Success, Failure

   # Parse an integer with validation
   result = parsers.parse_int_with_validation("42", min_value=0, max_value=100)
   match result:
       case Success(value):
           print(f"Valid integer: {value}")  # Valid integer: 42
       case Failure(error):
           print(f"Error: {error}")

   # Parse a list with length validation
   result = parsers.parse_list_with_validation(
       "1,2,3,4,5",
       element_parser=parsers.parse_int,
       min_length=3,
       max_length=10
   )
   match result:
       case Success(value):
           print(f"Valid list: {value}")  # Valid list: [1, 2, 3, 4, 5]
       case Failure(error):
           print(f"Error: {error}")

   # Parse a dictionary with required keys
   result = parsers.parse_dict_with_validation(
       "name:John,age:30,city:New York",
       value_parser=parsers.parse_int,
       required_keys=["name", "age"]
   )
   match result:
       case Success(value):
           print(f"Valid dict: {value}")  # Valid dict: {'name': 'John', 'age': 30, 'city': 'New York'}
       case Failure(error):
           print(f"Error: {error}")

Parser Limitations and Edge Cases
---------------------------------

Here are some important things to know about the parsers:

Integer Parser
~~~~~~~~~~~~~~

- Handles decimals that convert exactly to integers (e.g., "42.0")
- Rejects decimals with fractional parts (e.g., "42.5")
- Handles leading zeros (e.g., "007" → 7)
- Handles large integers automatically

Float Parser
~~~~~~~~~~~~

- Accepts special values like "inf", "-inf", and "NaN"
- Scientific notation is supported
- Very large or small values near the limits of float precision may have representation issues

Boolean Parser
~~~~~~~~~~~~~~

- Only recognizes specific strings for true/false values
- Case-insensitive for string-based inputs

Date Parser
~~~~~~~~~~~

- When using custom formats, use strftime/strptime codes (e.g., %Y, %m, %d)
- ISO format (YYYY-MM-DD) is the default when no format is specified
- Compact formats without separators (e.g., "20230115") need explicit format strings

Complex Parser
~~~~~~~~~~~~~~

- Handles various notations, including spaces between parts
- Accepts both 'j' and 'i' for the imaginary part
- Parentheses are handled ("(3+4j)" is valid)

Enum Parser
~~~~~~~~~~~

- Case-sensitive by default
- Works with both name and value lookup
- Handles whitespace automatically
- Special handling for empty values if the enum contains an empty string value

In the next section, we'll explore validators for checking that values meet specific criteria.