valid8r.core.parsers
====================

.. py:module:: valid8r.core.parsers

.. autoapi-nested-parse::

   String parsing functions with Maybe monad error handling.



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


