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
   valid8r.core.parsers.ISO_DATE_LENGTH


Classes
-------

.. autoapisummary::

   valid8r.core.parsers.ParserRegistry


Functions
---------

.. autoapisummary::

   valid8r.core.parsers.parse_int
   valid8r.core.parsers.parse_float
   valid8r.core.parsers.parse_bool
   valid8r.core.parsers.parse_date
   valid8r.core.parsers.parse_complex
   valid8r.core.parsers.parse_enum
   valid8r.core.parsers.parse_list
   valid8r.core.parsers.parse_dict
   valid8r.core.parsers.parse_set
   valid8r.core.parsers.parse_int_with_validation
   valid8r.core.parsers.parse_list_with_validation
   valid8r.core.parsers.parse_dict_with_validation


Module Contents
---------------

.. py:data:: T

.. py:data:: K

.. py:data:: V

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

   :param input_value: The string to parse
   :param key_parser: A function that parses keys
   :param value_parser: A function that parses values
   :param pair_separator: The string that separates key-value pairs
   :param key_value_separator: The string that separates keys from values
   :param error_message: Custom error message for parsing failures

   :returns: A Maybe containing the parsed dictionary or an error message


.. py:function:: parse_set(input_value, element_parser = None, separator = ',', error_message = None)

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


.. py:class:: ParserRegistry

   Registry for parser functions.

   This class provides a way to register custom parsers for specific types
   and retrieve them later. It also provides a convenient way to parse strings
   to specific types using registered parsers.

   .. admonition:: Examples

      >>> # Register a custom parser for IP addresses
      >>> def parse_ip_address(input_value: str) -> Maybe[ipaddress.IPv4Address]:
      ...     try:
      ...         return Maybe.success(ipaddress.IPv4Address(input_value))
      ...     except ValueError:
      ...         return Maybe.failure("Invalid IP address")
      ...
      >>> ParserRegistry.register(ipaddress.IPv4Address, parse_ip_address)
      ...
      >>> # Parse a string to an IP address
      >>> result = ParserRegistry.parse("192.168.1.1", ipaddress.IPv4Address)
      >>> result.is_success()
      True
      >>> str(result.value_or(None))
      '192.168.1.1'


   .. py:method:: register(type_, parser)
      :classmethod:


      Register a parser for a specific type.

      :param type_: The type to register the parser for
      :param parser: The parser function



   .. py:method:: get_parser(type_)
      :classmethod:


      Get a parser for a specific type.

      This method first looks for a direct match with the specified type.
      If no direct match is found, it looks for a match with a parent class.

      :param type_: The type to get a parser for

      :returns: The parser function or None if not found



   .. py:method:: parse(input_value, type_, error_message = None, **kwargs)
      :classmethod:


      Parse a string to a specific type using the registered parser.

      :param input_value: The string to parse
      :param type_: The target type
      :param error_message: Custom error message for parsing failures
      :param \*\*kwargs: Additional arguments to pass to the parser

      :returns: A Maybe containing the parsed value or an error message



   .. py:method:: register_defaults()
      :classmethod:


      Register default parsers for built-in types.



