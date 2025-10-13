Core API Reference
==================

This section provides detailed documentation for the core components of Valid8r, including the Maybe monad, parsers, validators, and combinators.

Maybe Monad
-----------

.. py:class:: valid8r.core.maybe.Maybe

   A monad that represents a value which might be present (Success) or absent with an error message (Failure).

   .. py:classmethod:: success(value)

      Create a Maybe containing a successful value.

      :param value: The value to wrap
      :return: A Success Maybe instance

   .. py:classmethod:: failure(error)

      Create a Maybe containing an error message.

      :param error: The error message
      :return: A Failure Maybe instance

   .. py:method:: bind(f)

      Chain operations that might fail.

      :param f: A function that takes a value and returns a Maybe
      :return: The result of applying f to the value, or the original Failure

   .. py:method:: map(f)

      Transform the value inside a Success, do nothing to a Failure.

      :param f: A function that takes a value and returns a new value
      :return: A new Maybe with the transformed value, or the original Failure

   .. py:method:: is_success()

      Check if this Maybe contains a value.

      :return: True if this is a Success, False otherwise

   .. py:method:: is_failure()

      Check if this Maybe contains an error.

      :return: True if this is a Failure, False otherwise

   .. py:method:: value_or(default)

      Safely get the value or a default for Success.

      :param default: Value to return if this is a Failure
      :return: The contained value or the default

   .. py:method:: error_or(default)

      Safely get the error message or a default for Success.

      :param default: Value to return if this is a Success
      :return: The error message or the default

   .. py:method:: get_error()

      Retrieve the error if present.

      :return: The error message, or None if this is a Success

.. py:class:: valid8r.core.maybe.Success

   A concrete implementation of Maybe representing a successful computation.

   This class supports pattern matching in Python 3.11+.

   .. py:attribute:: value

      The successful value.

.. py:class:: valid8r.core.maybe.Failure

   A concrete implementation of Maybe representing a failed computation.

   This class supports pattern matching in Python 3.11+.

   .. py:attribute:: error

      The error message explaining why the computation failed.

Parsers
-------

Type parsing functions that convert strings to various data types. These functions follow a consistent pattern: they take a string input and return a ``Maybe`` object containing either the successfully parsed value or an error message.

.. py:function:: valid8r.core.parsers.parse_int(input_value, error_message=None)

   Parse a string to an integer.

   :param input_value: String input to parse
   :param error_message: Optional custom error message
   :return: A Maybe containing either the parsed integer or an error

   Example with pattern matching:

   .. code-block:: python

      from valid8r.core.parsers import parse_int
      from valid8r.core.maybe import Success, Failure

      result = parse_int("42")
      match result:
          case Success(value):
              print(f"Parsed integer: {value}")  # Parsed integer: 42
          case Failure(error):
              print(f"Error: {error}")

.. py:function:: valid8r.core.parsers.parse_float(input_value, error_message=None)

   Parse a string to a float.

   :param input_value: String input to parse
   :param error_message: Optional custom error message
   :return: A Maybe containing either the parsed float or an error

   Example with pattern matching:

   .. code-block:: python

      from valid8r.core.parsers import parse_float
      from valid8r.core.maybe import Success, Failure

      result = parse_float("3.14")
      match result:
          case Success(value):
              print(f"Parsed float: {value}")  # Parsed float: 3.14
          case Failure(error):
              print(f"Error: {error}")

.. py:function:: valid8r.core.parsers.parse_bool(input_value, error_message=None)

   Parse a string to a boolean.

   :param input_value: String input to parse
   :param error_message: Optional custom error message
   :return: A Maybe containing either the parsed boolean or an error

   Example with pattern matching:

   .. code-block:: python

      from valid8r.core.parsers import parse_bool
      from valid8r.core.maybe import Success, Failure

      result = parse_bool("yes")
      match result:
          case Success(value):
              print(f"Parsed boolean: {value}")  # Parsed boolean: True
          case Failure(error):
              print(f"Error: {error}")

.. py:function:: valid8r.core.parsers.parse_date(input_value, date_format=None, error_message=None)

   Parse a string to a date.

   :param input_value: String input to parse
   :param date_format: Optional format string (strftime/strptime format)
   :param error_message: Optional custom error message
   :return: A Maybe containing either the parsed date or an error

   Example with pattern matching:

   .. code-block:: python

      from valid8r.core.parsers import parse_date
      from valid8r.core.maybe import Success, Failure

      result = parse_date("2023-01-15")
      match result:
          case Success(value):
              print(f"Parsed date: {value}")  # Parsed date: 2023-01-15
          case Failure(error):
              print(f"Error: {error}")

.. py:function:: valid8r.core.parsers.parse_complex(input_value, error_message=None)

   Parse a string to a complex number.

   :param input_value: String input to parse
   :param error_message: Optional custom error message
   :return: A Maybe containing either the parsed complex number or an error

   Example with pattern matching:

   .. code-block:: python

      from valid8r.core.parsers import parse_complex
      from valid8r.core.maybe import Success, Failure

      result = parse_complex("3+4j")
      match result:
          case Success(value):
              print(f"Parsed complex: {value}")  # Parsed complex: (3+4j)
          case Failure(error):
              print(f"Error: {error}")

.. py:function:: valid8r.core.parsers.parse_enum(input_value, enum_class, error_message=None)

   Parse a string to an enum value.

   :param input_value: String input to parse
   :param enum_class: The enum class to use for parsing
   :param error_message: Optional custom error message
   :return: A Maybe containing either the parsed enum value or an error

   Example with pattern matching:

   .. code-block:: python

      from enum import Enum
      from valid8r.core.parsers import parse_enum
      from valid8r.core.maybe import Success, Failure

      class Color(Enum):
          RED = "RED"
          GREEN = "GREEN"
          BLUE = "BLUE"

      result = parse_enum("RED", Color)
      match result:
          case Success(value):
              print(f"Parsed enum: {value}")  # Parsed enum: Color.RED
          case Failure(error):
              print(f"Error: {error}")

.. py:function:: valid8r.core.parsers.parse_list(input_value, element_parser=None, separator=',', error_message=None)

   Parse a string to a list using the specified element parser and separator.

   :param input_value: String input to parse
   :param element_parser: A function that parses individual elements
   :param separator: The string that separates elements
   :param error_message: Custom error message for parsing failures
   :return: A Maybe containing the parsed list or an error message

   Example with pattern matching:

   .. code-block:: python

      from valid8r.core.parsers import parse_list, parse_int
      from valid8r.core.maybe import Success, Failure

      result = parse_list("1,2,3", element_parser=parse_int)
      match result:
          case Success(value):
              print(f"Parsed list: {value}")  # Parsed list: [1, 2, 3]
          case Failure(error):
              print(f"Error: {error}")

.. py:function:: valid8r.core.parsers.parse_dict(input_value, key_parser=None, value_parser=None, pair_separator=',', key_value_separator=':', error_message=None)

   Parse a string to a dictionary using the specified parsers and separators.

   :param input_value: String input to parse
   :param key_parser: A function that parses keys
   :param value_parser: A function that parses values
   :param pair_separator: The string that separates key-value pairs
   :param key_value_separator: The string that separates keys from values
   :param error_message: Custom error message for parsing failures
   :return: A Maybe containing the parsed dictionary or an error message

   Example with pattern matching:

   .. code-block:: python

      from valid8r.core.parsers import parse_dict, parse_int
      from valid8r.core.maybe import Success, Failure

      result = parse_dict("name:John,age:30", value_parser=parse_int)
      match result:
          case Success(value):
              print(f"Parsed dict: {value}")  # Parsed dict: {'name': 'John', 'age': 30}
          case Failure(error):
              print(f"Error: {error}")

.. py:function:: valid8r.core.parsers.parse_set(input_value, element_parser=None, separator=',', error_message=None)

   Parse a string to a set using the specified element parser and separator.

   :param input_value: String input to parse
   :param element_parser: A function that parses individual elements
   :param separator: The string that separates elements
   :param error_message: Custom error message for parsing failures
   :return: A Maybe containing the parsed set or an error message

   Example with pattern matching:

   .. code-block:: python

      from valid8r.core.parsers import parse_set, parse_int
      from valid8r.core.maybe import Success, Failure

      result = parse_set("1,2,3,2,1", element_parser=parse_int)
      match result:
          case Success(value):
              print(f"Parsed set: {value}")  # Parsed set: {1, 2, 3}
          case Failure(error):
              print(f"Error: {error}")

.. py:function:: valid8r.core.parsers.parse_int_with_validation(input_value, min_value=None, max_value=None, error_message=None)

   Parse a string to an integer with validation.

   :param input_value: String input to parse
   :param min_value: Minimum allowed value (inclusive)
   :param max_value: Maximum allowed value (inclusive)
   :param error_message: Custom error message for parsing failures
   :return: A Maybe containing the parsed integer or an error message

   Example with pattern matching:

   .. code-block:: python

      from valid8r.core.parsers import parse_int_with_validation
      from valid8r.core.maybe import Success, Failure

      result = parse_int_with_validation("42", min_value=0, max_value=100)
      match result:
          case Success(value):
              print(f"Valid integer: {value}")  # Valid integer: 42
          case Failure(error):
              print(f"Error: {error}")

.. py:function:: valid8r.core.parsers.parse_list_with_validation(input_value, element_parser=None, separator=',', min_length=None, max_length=None, error_message=None)

   Parse a string to a list with validation.

   :param input_value: String input to parse
   :param element_parser: A function that parses individual elements
   :param separator: The string that separates elements
   :param min_length: Minimum allowed list length
   :param max_length: Maximum allowed list length
   :param error_message: Custom error message for parsing failures
   :return: A Maybe containing the parsed list or an error message

.. py:function:: valid8r.core.parsers.parse_dict_with_validation(input_value, key_parser=None, value_parser=None, pair_separator=',', key_value_separator=':', required_keys=None, error_message=None)

   Parse a string to a dictionary with validation.

   :param input_value: String input to parse
   :param key_parser: A function that parses keys
   :param value_parser: A function that parses values
:param pair_separator: The string that separates key-value pairs
   :param key_value_separator: The string that separates keys from values
   :param required_keys: List of keys that must be present
   :param error_message: Custom error message for parsing failures
   :return: A Maybe containing the parsed dictionary or an error message

Custom Parser Creation
^^^^^^^^^^^^^^^^^^^^^^

.. py:function:: valid8r.core.parsers.create_parser(convert_func, error_message=None)

   Create a parser function from a conversion function.

   :param convert_func: A function that converts strings to values
   :param error_message: Optional custom error message
   :return: A parser function that returns a Maybe

.. py:function:: valid8r.core.parsers.make_parser(func=None)

   Decorator that creates a parser function from a conversion function.

   :param func: A function that converts strings to values
   :return: A decorated function that returns a Maybe

.. py:function:: valid8r.core.parsers.validated_parser(convert_func, validator, error_message=None)

   Create a parser with validation built in.

   :param convert_func: A function that converts strings to values
   :param validator: A function that validates the parsed value
   :param error_message: Optional custom error message
   :return: A parser function that combines parsing and validation

   Example:

   .. code-block:: python

      from valid8r.core.parsers import validated_parser
      from valid8r.core.validators import minimum
      from decimal import Decimal

      # Create a parser that only accepts positive decimals
      positive_decimal = validated_parser(
          Decimal,  # Convert function
          lambda x: minimum(Decimal('0'))(x),  # Validator function
          "Not a valid positive decimal"  # Error message
      )

      result = positive_decimal("42.5")
      match result:
          case Success(value):
              print(f"Valid decimal: {value}")
          case Failure(error):
              print(f"Error: {error}")

Validators
----------

Functions for validating values against various criteria.

.. py:class:: valid8r.core.validators.Validator

   A wrapper class for validator functions that supports operator overloading.

   .. py:method:: __and__(other)

      Combine with another validator using logical AND.

      :param other: Another Validator instance
      :return: A new Validator that passes only if both validators pass

   .. py:method:: __or__(other)

      Combine with another validator using logical OR.

      :param other: Another Validator instance
      :return: A new Validator that passes if either validator passes

   .. py:method:: __invert__()

      Negate this validator.

      :return: A new Validator that passes if this validator fails

   Example with pattern matching:

   .. code-block:: python

      from valid8r.core.validators import Validator, minimum, maximum
      from valid8r.core.maybe import Success, Failure

      # Create a combined validator using operator overloading
      is_adult = minimum(18)
      is_senior = maximum(65)
      working_age = is_adult & is_senior

      result = working_age(42)
      match result:
          case Success(value):
              print(f"Valid working age: {value}")  # Valid working age: 42
          case Failure(error):
              print(f"Invalid age: {error}")

.. py:function:: valid8r.core.validators.minimum(min_value, error_message=None)

   Create a validator that ensures a value is at least the minimum.

   :param min_value: The minimum allowed value
   :param error_message: Optional custom error message
   :return: A Validator that checks for minimum value

   Example with pattern matching:

   .. code-block:: python

      from valid8r.core.validators import minimum
      from valid8r.core.maybe import Success, Failure

      is_positive = minimum(0)
      result = is_positive(42)
      match result:
          case Success(value):
              print(f"Valid positive number: {value}")  # Valid positive number: 42
          case Failure(error):
              print(f"Error: {error}")

.. py:function:: valid8r.core.validators.maximum(max_value, error_message=None)

   Create a validator that ensures a value is at most the maximum.

   :param max_value: The maximum allowed value
   :param error_message: Optional custom error message
   :return: A Validator that checks for maximum value

   Example with pattern matching:

   .. code-block:: python

      from valid8r.core.validators import maximum
      from valid8r.core.maybe import Success, Failure

      under_hundred = maximum(100)
      result = under_hundred(42)
      match result:
          case Success(value):
              print(f"Valid number under 100: {value}")  # Valid number under 100: 42
          case Failure(error):
              print(f"Error: {error}")

.. py:function:: valid8r.core.validators.between(min_value, max_value, error_message=None)

   Create a validator that ensures a value is between minimum and maximum (inclusive).

   :param min_value: The minimum allowed value
   :param max_value: The maximum allowed value
   :param error_message: Optional custom error message
   :return: A Validator that checks for a value within range

   Example with pattern matching:

   .. code-block:: python

      from valid8r.core.validators import between
      from valid8r.core.maybe import Success, Failure

      is_valid_age = between(0, 120)
      result = is_valid_age(42)
      match result:
          case Success(value):
              print(f"Valid age: {value}")  # Valid age: 42
          case Failure(error):
              print(f"Error: {error}")

.. py:function:: valid8r.core.validators.predicate(pred, error_message)

   Create a validator using a custom predicate function.

   :param pred: A function that takes a value and returns a boolean
   :param error_message: Error message when validation fails
   :return: A Validator that checks the predicate

   Example with pattern matching:

   .. code-block:: python

      from valid8r.core.validators import predicate
      from valid8r.core.maybe import Success, Failure

      is_even = predicate(lambda x: x % 2 == 0, "Value must be even")
      result = is_even(42)
      match result:
          case Success(value):
              print(f"Valid even number: {value}")  # Valid even number: 42
          case Failure(error):
              print(f"Error: {error}")

.. py:function:: valid8r.core.validators.length(min_length, max_length, error_message=None)

   Create a validator that ensures a string's length is within bounds.

   :param min_length: Minimum length of the string
   :param max_length: Maximum length of the string
   :param error_message: Optional custom error message
   :return: A Validator that checks string length

   Example with pattern matching:

   .. code-block:: python

      from valid8r.core.validators import length
      from valid8r.core.maybe import Success, Failure

      valid_name = length(2, 50)
      result = valid_name("John Doe")
      match result:
          case Success(value):
              print(f"Valid name: {value}")  # Valid name: John Doe
          case Failure(error):
              print(f"Error: {error}")

Combinators
-----------

Functions for combining validators.

.. py:function:: valid8r.core.combinators.and_then(first, second)

   Combine two validators with logical AND (both must succeed).

   :param first: The first validator function
   :param second: The second validator function
   :return: A combined validator function

   Example with pattern matching:

   .. code-block:: python

      from valid8r.core.combinators import and_then
      from valid8r.core.validators import minimum, predicate
      from valid8r.core.maybe import Success, Failure

      is_positive = minimum(0)
      is_even = predicate(lambda x: x % 2 == 0, "Value must be even")

      # Combine with and_then
      positive_and_even = and_then(is_positive, is_even)

      result = positive_and_even(42)
      match result:
          case Success(value):
              print(f"Valid positive even number: {value}")  # Valid positive even number: 42
          case Failure(error):
              print(f"Error: {error}")

.. py:function:: valid8r.core.combinators.or_else(first, second)

   Combine two validators with logical OR (either can succeed).

   :param first: The first validator function
   :param second: The second validator function
   :return: A combined validator function

   Example with pattern matching:

   .. code-block:: python

      from valid8r.core.combinators import or_else
      from valid8r.core.validators import predicate
      from valid8r.core.maybe import Success, Failure

      is_even = predicate(lambda x: x % 2 == 0, "Value must be even")
      is_multiple_of_5 = predicate(lambda x: x % 5 == 0, "Value must be divisible by 5")

      # Combine with or_else
      even_or_multiple_of_5 = or_else(is_even, is_multiple_of_5)

      result = even_or_multiple_of_5(15)
      match result:
          case Success(value):
              print(f"Valid number: {value}")  # Valid number: 15 (multiple of 5)
          case Failure(error):
              print(f"Error: {error}")

.. py:function:: valid8r.core.combinators.not_validator(validator, error_message)

   Negate a validator (success becomes failure and vice versa).

   :param validator: The validator function to negate
   :param error_message: Error message for the negated validator
   :return: A negated validator function

   Example with pattern matching:

   .. code-block:: python

      from valid8r.core.combinators import not_validator
      from valid8r.core.validators import predicate
      from valid8r.core.maybe import Success, Failure

      is_even = predicate(lambda x: x % 2 == 0, "Value must be even")
      is_odd = not_validator(is_even, "Value must be odd")

      result = is_odd(7)
      match result:
          case Success(value):
              print(f"Valid odd number: {value}")  # Valid odd number: 7
          case Failure(error):
              print(f"Error: {error}")

Pattern Matching with Success and Failure
-----------------------------------------

The Success and Failure classes in Valid8r are designed to work with Python's pattern matching feature (introduced in Python 3.11). This enables concise and readable handling of validation results.

Basic Pattern Matching
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from valid8r import parsers
   from valid8r.core.maybe import Success, Failure

   result = parsers.parse_int("42")

   match result:
       case Success(value):
           print(f"Valid integer: {value}")
       case Failure(error):
           print(f"Error: {error}")

Pattern Matching with Conditions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from valid8r import parsers, validators
   from valid8r.core.maybe import Success, Failure

   def validate_input(input_str):
       # Parse and validate
       result = parsers.parse_int(input_str).bind(
           lambda x: validators.between(1, 100)(x)
       )

       match result:
           case Success(value) if value % 2 == 0:
               return f"Valid even number: {value}"
           case Success(value):
               return f"Valid odd number: {value}"
           case Failure(error) if "valid integer" in error:
               return f"Parsing error: {error}"
           case Failure(error):
               return f"Validation error: {error}"

Matching Multiple Results
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from valid8r import parsers
   from valid8r.core.maybe import Success, Failure

   def process_coordinates(x_str, y_str):
       # Parse both coordinates
       x_result = parsers.parse_int(x_str)
       y_result = parsers.parse_int(y_str)

       # Pattern match on tuple of results
       match (x_result, y_result):
           case (Success(x), Success(y)):
               return f"Valid point: ({x}, {y})"
           case (Failure(error), _):
               return f"Invalid x-coordinate: {error}"
           case (_, Failure(error)):
               return f"Invalid y-coordinate: {error}"

.. py:function:: valid8r.core.parsers.parse_ipv4(text)

   Parse a string to an IPv4Address. Surrounding whitespace is ignored.

   :param text: Input string
   :return: Maybe[IPv4Address] with deterministic errors: "value must be a string", "value is empty", "not a valid IPv4 address"

.. py:function:: valid8r.core.parsers.parse_ipv6(text)

   Parse a string to an IPv6Address. Surrounding whitespace is ignored and output is canonicalized.

   :param text: Input string
   :return: Maybe[IPv6Address] with deterministic errors: "value must be a string", "value is empty", "not a valid IPv6 address"

.. py:function:: valid8r.core.parsers.parse_ip(text)

   Parse a string to an IP address, accepting either IPv4 or IPv6. Surrounding whitespace is ignored.

   :param text: Input string
   :return: Maybe[IPv4Address | IPv6Address] with deterministic errors: "value must be a string", "value is empty", "not a valid IP address"

.. py:function:: valid8r.core.parsers.parse_cidr(text, *, strict=True)

   Parse a CIDR network string to IPv4Network or IPv6Network using ``ipaddress.ip_network``.

   ``strict=True`` (default) rejects inputs with host bits set; use ``strict=False`` to mask host bits.

   :param text: Input string
   :param strict: Whether to reject host bits
   :return: Maybe[IPv4Network | IPv6Network] with deterministic errors: "value must be a string", "value is empty", "has host bits set" (when strict), "not a valid network"
