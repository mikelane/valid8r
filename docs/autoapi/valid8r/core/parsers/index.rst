valid8r.core.parsers
====================

.. py:module:: valid8r.core.parsers

.. autoapi-nested-parse::

   String parsing functions with Maybe monad error handling.



Attributes
----------

.. autoapisummary::

   valid8r.core.parsers.T
   valid8r.core.parsers.K
   valid8r.core.parsers.V
   valid8r.core.parsers.P
   valid8r.core.parsers.E
   valid8r.core.parsers.ISO_DATE_LENGTH


Functions
---------

.. autoapisummary::

   valid8r.core.parsers.parse_int
   valid8r.core.parsers.parse_float
   valid8r.core.parsers.parse_bool
   valid8r.core.parsers.parse_date
   valid8r.core.parsers.parse_complex
   valid8r.core.parsers.parse_decimal
   valid8r.core.parsers.parse_enum
   valid8r.core.parsers.parse_list
   valid8r.core.parsers.parse_dict
   valid8r.core.parsers.parse_set
   valid8r.core.parsers.parse_int_with_validation
   valid8r.core.parsers.parse_list_with_validation
   valid8r.core.parsers.parse_dict_with_validation
   valid8r.core.parsers.create_parser
   valid8r.core.parsers.make_parser
   valid8r.core.parsers.validated_parser
   valid8r.core.parsers.parse_uuid


Module Contents
---------------

.. py:data:: T

.. py:data:: K

.. py:data:: V

.. py:data:: P

.. py:data:: E

.. py:data:: ISO_DATE_LENGTH
   :value: 10


.. py:function:: parse_int(input_value, error_message = None)

   Parse a string to an integer.


.. py:function:: parse_float(input_value, error_message = None)

   Parse a string to a float.


.. py:function:: parse_bool(input_value, error_message = None)

   Parse a string to a boolean.


.. py:function:: parse_date(input_value, date_format = None, error_message = None)

   Parse a string to a date.


.. py:function:: parse_complex(input_value, error_message = None)

   Parse a string to a complex number.


.. py:function:: parse_decimal(input_value, error_message = None)

   Parse a string to a Decimal.

   :param input_value: String representation of a decimal number
   :param error_message: Optional custom error message

   :returns: Success with Decimal value or Failure with an error message
   :rtype: Maybe[Decimal]


.. py:function:: parse_enum(input_value, enum_class, error_message = None)

   Parse a string to an enum value.


.. py:function:: parse_list(input_value, element_parser = None, separator = ',', error_message = None)

   Parse a string to a list using the specified element parser and separator.

   :param input_value: The string to parse
   :param element_parser: A function that parses individual elements
   :param separator: The string that separates elements
   :param error_message: Custom error message for parsing failures

   :returns: A Maybe containing the parsed list or an error message


.. py:function:: parse_dict(input_value, key_parser = None, value_parser = None, pair_separator = ',', key_value_separator = ':', error_message = None)

   Parse a string to a dictionary using the specified parsers and separators.


.. py:function:: parse_set(input_value, element_parser = None, separator = None, error_message = None)

   Parse a string to a set using the specified element parser and separator.

   :param input_value: The string to parse
   :param element_parser: A function that parses individual elements
   :param separator: The string that separates elements
   :param error_message: Custom error message for parsing failures

   :returns: A Maybe containing the parsed set or an error message


.. py:function:: parse_int_with_validation(input_value, min_value = None, max_value = None, error_message = None)

   Parse a string to an integer with validation.

   :param input_value: The string to parse
   :param min_value: Minimum allowed value (inclusive)
   :param max_value: Maximum allowed value (inclusive)
   :param error_message: Custom error message for parsing failures

   :returns: A Maybe containing the parsed integer or an error message


.. py:function:: parse_list_with_validation(input_value, element_parser = None, separator = ',', min_length = None, max_length = None, error_message = None)

   Parse a string to a list with validation.

   :param input_value: The string to parse
   :param element_parser: A function that parses individual elements
   :param separator: The string that separates elements
   :param min_length: Minimum allowed list length
   :param max_length: Maximum allowed list length
   :param error_message: Custom error message for parsing failures

   :returns: A Maybe containing the parsed list or an error message


.. py:function:: parse_dict_with_validation(input_value, key_parser = None, value_parser = None, pair_separator = ',', key_value_separator = ':', required_keys = None, error_message = None)

   Parse a string to a dictionary with validation.

   :param input_value: The string to parse
   :param key_parser: A function that parses keys
   :param value_parser: A function that parses values
   :param pair_separator: The string that separates key-value pairs
   :param key_value_separator: The string that separates keys from values
   :param required_keys: List of keys that must be present
   :param error_message: Custom error message for parsing failures

   :returns: A Maybe containing the parsed dictionary or an error message


.. py:function:: create_parser(convert_func, error_message = None)

   Create a parser function from a conversion function.

   This factory takes a function that converts strings to values and wraps it
   in error handling logic to return Maybe instances.

   :param convert_func: A function that converts strings to values of type T
   :param error_message: Optional custom error message for failures

   :returns: A parser function that returns Maybe[T]

   .. admonition:: Example

      >>> from decimal import Decimal
      >>> parse_decimal = create_parser(Decimal, "Invalid decimal format")
      >>> result = parse_decimal("3.14")
      >>> result.is_success()
      True


.. py:function:: make_parser(func: collections.abc.Callable[[str], T]) -> collections.abc.Callable[[str], valid8r.core.maybe.Maybe[T]]
                 make_parser() -> collections.abc.Callable[[collections.abc.Callable[[str], T]], collections.abc.Callable[[str], valid8r.core.maybe.Maybe[T]]]

   Create a parser function from a conversion function with a decorator.

   .. admonition:: Example

      @make_parser
      def parse_decimal(s: str) -> Decimal:
          return Decimal(s)
      
      # Or with parentheses
      @make_parser()
      def parse_decimal(s: str) -> Decimal:
          return Decimal(s)
      
      result = parse_decimal("123.45")  # Returns Maybe[Decimal]


.. py:function:: validated_parser(convert_func, validator, error_message = None)

   Create a parser with a built-in validator.

   This combines parsing and validation in a single function.

   :param convert_func: A function that converts strings to values of type T
   :param validator: A validator function that validates the parsed value
   :param error_message: Optional custom error message for parsing failures

   :returns: A parser function that returns Maybe[T]

   .. admonition:: Example

      >>> from decimal import Decimal
      >>> from valid8r.core.validators import minimum, maximum
      >>> # Create a parser for positive decimals
      >>> valid_range = lambda x: minimum(0)(x).bind(lambda y: maximum(100)(y))
      >>> parse_percent = validated_parser(Decimal, valid_range)
      >>> result = parse_percent("42.5")
      >>> result.is_success()
      True


.. py:function:: parse_uuid(text, version = None, strict = True)

   Parse a string to a UUID.

   Uses uuid-utils to parse and validate UUIDs across versions 1, 3, 4, 5, 6, 7, and 8.
   When ``version`` is provided, validates the parsed UUID version. In ``strict`` mode (default),
   a mismatch yields a Failure; otherwise, the mismatch is ignored and the UUID is returned.

   :param text: The UUID string in canonical 8-4-4-4-12 form.
   :param version: Optional expected UUID version to validate against.
   :param strict: Whether to enforce the expected version when provided.

   :returns: Success with a UUID object or Failure with an error message.
   :rtype: Maybe[UUID]


