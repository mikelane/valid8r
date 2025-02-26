Core API Reference
==================

This section provides detailed documentation for the core components of Valid8r.

Maybe Monad
------------

.. py:class:: valid8r.core.maybe.Maybe

   A monad that represents a value which might be present (Just) or absent with an error message (Nothing).

   .. py:classmethod:: just(value)

      Create a Maybe containing a successful value.

      :param value: The value to wrap
      :return: A Just Maybe instance

   .. py:classmethod:: nothing(error)

      Create a Maybe containing an error message.

      :param error: The error message
      :return: A Nothing Maybe instance

   .. py:method:: bind(f)

      Chain operations that might fail.

      :param f: A function that takes a value and returns a Maybe
      :return: The result of applying f to the value, or the original Nothing

   .. py:method:: map(f)

      Transform the value inside a Just, do nothing to a Nothing.

      :param f: A function that takes a value and returns a new value
      :return: A new Maybe with the transformed value, or the original Nothing

   .. py:method:: is_just()

      Check if this Maybe contains a value.

      :return: True if this is a Just, False otherwise

   .. py:method:: is_nothing()

      Check if this Maybe contains an error.

      :return: True if this is a Nothing, False otherwise

   .. py:method:: value()

      Get the contained value. Unsafe if is_nothing().

      :return: The contained value
      :raises ValueError: If called on a Nothing

   .. py:method:: error()

      Get the error message. Unsafe if is_just().

      :return: The error message
      :raises ValueError: If called on a Just

   .. py:method:: value_or(default)

      Safely get the value or a default.

      :param default: Value to return if this is a Nothing
      :return: The contained value or the default

Parsers
-------

Type parsing functions that convert strings to various data types.

.. py:function:: valid8r.core.parsers.parse_int(input_value, error_message=None, max_digits=30)

   Parse a string to an integer.

   :param input_value: String input to parse
   :param error_message: Optional custom error message
   :param max_digits: Maximum number of digits allowed (default 30)
   :return: A Maybe containing either the parsed integer or an error

.. py:function:: valid8r.core.parsers.parse_float(input_value, error_message=None)

   Parse a string to a float.

   :param input_value: String input to parse
   :param error_message: Optional custom error message
   :return: A Maybe containing either the parsed float or an error

.. py:function:: valid8r.core.parsers.parse_bool(input_value, error_message=None)

   Parse a string to a boolean.

   :param input_value: String input to parse
   :param error_message: Optional custom error message
   :return: A Maybe containing either the parsed boolean or an error

.. py:function:: valid8r.core.parsers.parse_date(input_value, date_format=None, error_message=None)

   Parse a string to a date.

   :param input_value: String input to parse
   :param date_format: Optional format string (strftime/strptime format)
   :param error_message: Optional custom error message
   :return: A Maybe containing either the parsed date or an error

.. py:function:: valid8r.core.parsers.parse_complex(input_value, error_message=None)

   Parse a string to a complex number.

   :param input_value: String input to parse
   :param error_message: Optional custom error message
   :return: A Maybe containing either the parsed complex number or an error

.. py:function:: valid8r.core.parsers.parse_enum(input_value, enum_class, error_message=None)

   Parse a string to an enum value.

   :param input_value: String input to parse
   :param enum_class: The enum class to use for parsing
   :param error_message: Optional custom error message
   :return: A Maybe containing either the parsed enum value or an error

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

.. py:function:: valid8r.core.validators.minimum(min_value, error_message=None)

   Create a validator that ensures a value is at least the minimum.

   :param min_value: The minimum allowed value
   :param error_message: Optional custom error message
   :return: A Validator that checks for minimum value

.. py:function:: valid8r.core.validators.maximum(max_value, error_message=None)

   Create a validator that ensures a value is at most the maximum.

   :param max_value: The maximum allowed value
   :param error_message: Optional custom error message
   :return: A Validator that checks for maximum value

.. py:function:: valid8r.core.validators.between(min_value, max_value, error_message=None)

   Create a validator that ensures a value is between minimum and maximum (inclusive).

   :param min_value: The minimum allowed value
   :param max_value: The maximum allowed value
   :param error_message: Optional custom error message
   :return: A Validator that checks for a value within range

.. py:function:: valid8r.core.validators.predicate(pred, error_message)

   Create a validator using a custom predicate function.

   :param pred: A function that takes a value and returns a boolean
   :param error_message: Error message when validation fails
   :return: A Validator that checks the predicate

.. py:function:: valid8r.core.validators.length(min_length, max_length, error_message=None)

   Create a validator that ensures a string's length is within bounds.

   :param min_length: Minimum length of the string
   :param max_length: Maximum length of the string
   :param error_message: Optional custom error message
   :return: A Validator that checks string length

Combinators
-----------

Functions for combining validators.

.. py:function:: valid8r.core.combinators.and_then(first, second)

   Combine two validators with logical AND (both must succeed).

   :param first: The first validator function
   :param second: The second validator function
   :return: A combined validator function

.. py:function:: valid8r.core.combinators.or_else(first, second)

   Combine two validators with logical OR (either can succeed).

   :param first: The first validator function
   :param second: The second validator function
   :return: A combined validator function

.. py:function:: valid8r.core.combinators.not_validator(validator, error_message)

   Negate a validator (success becomes failure and vice versa).

   :param validator: The validator function to negate
   :param error_message: Error message for the negated validator
   :return: A negated validator function

Usage Examples
--------------

Here are some examples of using the core API:

.. code-block:: python

   from valid8r import Maybe, parsers, validators

   # Using the Maybe monad
   result = Maybe.just(42)
   if result.is_just():
       value = result.value()

   # Chaining with bind
   result = (
       Maybe.just(42)
       .bind(lambda x: Maybe.just(x * 2))
       .bind(lambda x: Maybe.just(x + 10))
   )
   # result is Just(94)

   # Using parsers
   result = parsers.parse_int("42")
   if result.is_just():
       value = result.value()  # 42

   # Using validators
   is_positive = validators.minimum(0)
   result = is_positive(42)  # Just(42)
   result = is_positive(-1)  # Nothing("Value must be at least 0")

   # Combining validators
   valid_age = validators.minimum(0) & validators.maximum(120)
   result = valid_age(42)  # Just(42)
   result = valid_age(-1)  # Nothing("Value must be at least 0")
   result = valid_age(150)  # Nothing("Value must be at most 120")

   # Parser and validator together
   result = parsers.parse_int("42").bind(lambda x: valid_age(x))
   if result.is_just():
       print(f"Valid age: {result.value()}")
   else:
       print(f"Invalid age: {result.error()}")