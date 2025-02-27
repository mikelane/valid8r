valid8r.core.parsers
====================

.. py:module:: valid8r.core.parsers

.. autoapi-nested-parse::

   String parsing functions with Maybe monad error handling.

   This module provides functions to parse strings into various Python types.
   All parsing functions return Maybe objects, allowing for clean error handling.



Attributes
----------

.. autoapisummary::

   valid8r.core.parsers.T
   valid8r.core.parsers.ISO_DATE_LENGTH


Functions
---------

.. autoapisummary::

   valid8r.core.parsers.parse_int
   valid8r.core.parsers.parse_float
   valid8r.core.parsers.parse_bool
   valid8r.core.parsers.parse_date
   valid8r.core.parsers.parse_complex
   valid8r.core.parsers.parse_enum


Module Contents
---------------

.. py:data:: T

.. py:data:: ISO_DATE_LENGTH
   :value: 10


.. py:function:: parse_int(input_value, error_message = None)

   Parse a string to an integer.

   :param input_value: String input to parse
   :param error_message: Optional custom error message

   :returns: A Maybe containing either the parsed integer or an error

   .. admonition:: Examples

      >>> parse_int("42")
      Just(42)
      >>> parse_int("abc")
      Nothing(Input must be a valid integer)


.. py:function:: parse_float(input_value, error_message = None)

   Parse a string to a float.

   :param input_value: String input to parse
   :param error_message: Optional custom error message

   :returns: A Maybe containing either the parsed float or an error


.. py:function:: parse_bool(input_value, error_message = None)

   Parse a string to a boolean.

   :param input_value: String input to parse
   :param error_message: Optional custom error message

   :returns: A Maybe containing either the parsed boolean or an error


.. py:function:: parse_date(input_value, date_format = None, error_message = None)

   Parse a string to a date.

   :param input_value: String input to parse
   :param date_format: Optional format string (strftime format)
   :param error_message: Optional custom error message

   :returns: A Maybe containing either the parsed date or an error


.. py:function:: parse_complex(input_value, error_message = None)

   Parse a string to a complex number.

   :param input_value: String input to parse
   :param error_message: Optional custom error message

   :returns: A Maybe containing either the parsed complex number or an error

   .. admonition:: Examples

      >>> parse_complex("3+4j")
      Just((3+4j))
      >>> parse_complex("3+4i")  # Also supports mathematical 'i' notation
      Just((3+4j))
      >>> parse_complex("not a complex")
      Nothing(Input must be a valid complex number)


.. py:function:: parse_enum(input_value, enum_class, error_message = None)

   Parse a string to an enum value.

   :param input_value: String input to parse
   :param enum_class: The enum class to use for parsing
   :param error_message: Optional custom error message

   :returns: A Maybe containing either the parsed enum value or an error

   .. admonition:: Examples

      >>> from enum import Enum
      >>> class Color(Enum):
      ...     RED = "RED"
      ...     GREEN = "GREEN"
      ...     BLUE = "BLUE"
      >>> parse_enum("RED", Color)
      Just(Color.RED)
      >>> parse_enum("YELLOW", Color)
      Nothing(Input must be a valid enumeration value)


