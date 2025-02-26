Parsers
=======

Parsers are functions that convert string inputs into other data types, returning Maybe objects to handle potential parsing errors.

Basic Usage
-----------

.. code-block:: python

   from valid8r import parsers

   # Parse a string to an integer
   result = parsers.parse_int("42")
   if result.is_just():
       print(f"Parsed integer: {result.value()}")
   else:
       print(f"Error: {result.error()}")

   # Parse a string to a float
   result = parsers.parse_float("3.14")
   if result.is_just():
       print(f"Parsed float: {result.value()}")
   else:
       print(f"Error: {result.error()}")

Available Parsers
-----------------

Valid8r includes parsers for several common data types:

Integer Parser
~~~~~~~~~~~~~~

.. code-block:: python

   from valid8r import parsers

   # Basic usage
   result = parsers.parse_int("42")

   # Custom error message
   result = parsers.parse_int("abc", error_message="Please enter a valid number")

   # Handles whitespace
   result = parsers.parse_int("  42  ")

   # Parses integers with integer-equivalent float notation
   result = parsers.parse_int("42.0")  # Parses to 42

Float Parser
~~~~~~~~~~~~

.. code-block:: python

   from valid8r import parsers

   # Basic usage
   result = parsers.parse_float("3.14")

   # Scientific notation
   result = parsers.parse_float("1.23e-4")

   # Handles whitespace
   result = parsers.parse_float("  3.14  ")

   # Integer as float
   result = parsers.parse_float("42")  # Parses to 42.0

Boolean Parser
~~~~~~~~~~~~~~

.. code-block:: python

   from valid8r import parsers

   # Various true values
   for value in ["true", "True", "TRUE", "t", "T", "yes", "y", "1"]:
       result = parsers.parse_bool(value)
       # All parse to True

   # Various false values
   for value in ["false", "False", "FALSE", "f", "F", "no", "n", "0"]:
       result = parsers.parse_bool(value)
       # All parse to False

   # Invalid boolean string
   result = parsers.parse_bool("maybe")
   # Returns Nothing with error

Date Parser
~~~~~~~~~~~

.. code-block:: python

   from valid8r import parsers

   # ISO format (default)
   result = parsers.parse_date("2023-01-15")

   # Custom format
   result = parsers.parse_date("15/01/2023", date_format="%d/%m/%Y")

   # Another format example
   result = parsers.parse_date("Jan 15, 2023", date_format="%b %d, %Y")

Complex Number Parser
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from valid8r import parsers

   # Standard notation
   result = parsers.parse_complex("3+4j")

   # Alternative notation
   result = parsers.parse_complex("3+4i")  # Also works

   # Just real part
   result = parsers.parse_complex("5")  # Parses to (5+0j)

   # Just imaginary part
   result = parsers.parse_complex("3j")  # Parses to (0+3j)

Enum Parser
~~~~~~~~~~~

.. code-block:: python

   from enum import Enum
   from valid8r import parsers

   # Define an enum
   class Color(Enum):
       RED = "RED"
       GREEN = "GREEN"
       BLUE = "BLUE"

   # Parse to enum
   result = parsers.parse_enum("RED", Color)
   if result.is_just():
       print(result.value() == Color.RED)  # True

   # Invalid enum value
   result = parsers.parse_enum("YELLOW", Color)
   print(result.error())  # "Input must be a valid enumeration value"

Error Handling
--------------

All parsers follow consistent error handling patterns:

1. If the input is empty, the error is "Input must not be empty"
2. If the input cannot be parsed, a type-specific error is returned (e.g., "Input must be a valid integer")
3. You can provide a custom error message to override the default ones

.. code-block:: python

   from valid8r import parsers

   # Empty input
   result = parsers.parse_int("")
   print(result.error())  # "Input must not be empty"

   # Invalid input
   result = parsers.parse_int("abc")
   print(result.error())  # "Input must be a valid integer"

   # Custom error message
   result = parsers.parse_int("abc", error_message="Please enter a number")
   print(result.error())  # "Please enter a number"

Common Parser Features
----------------------

All parsers have these common features:

1. **Whitespace handling**: Leading and trailing whitespace is automatically removed
2. **Maybe return value**: All parsers return a Maybe object
3. **Custom error messages**: All parsers accept an optional error_message parameter
4. **Empty input handling**: All parsers check for empty input first

Combining Parsers with Validators
---------------------------------

Parsers are often used together with validators to create a complete validation pipeline:

.. code-block:: python

   from valid8r import parsers, validators

   # Parse a string to an integer, then validate it's positive
   result = parsers.parse_int("42").bind(
       lambda x: validators.minimum(0)(x)
   )

   # Parse a string to a date, then validate it's in the future
   from datetime import date

   def is_future_date(d):
       if d > date.today():
           return Maybe.just(d)
       return Maybe.nothing("Date must be in the future")

   result = parsers.parse_date("2025-01-01").bind(is_future_date)

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