valid8r.core.combinators
========================

.. py:module:: valid8r.core.combinators

.. autoapi-nested-parse::

   Combinators for creating complex validation rules.

   This module provides functions to combine validators using logical operations like AND, OR, and NOT.
   These combinators allow for creation of complex validation chains.



Attributes
----------

.. autoapisummary::

   valid8r.core.combinators.T


Functions
---------

.. autoapisummary::

   valid8r.core.combinators.and_then
   valid8r.core.combinators.or_else
   valid8r.core.combinators.not_validator


Module Contents
---------------

.. py:data:: T

.. py:function:: and_then(first, second)

   Combine two validators with logical AND (both must succeed).

   :param first: The first validator function
   :param second: The second validator function

   :returns: A new validator function that passes only if both validators pass


.. py:function:: or_else(first, second)

   Combine two validators with logical OR (either can succeed).

   :param first: The first validator function
   :param second: The second validator function

   :returns: A new validator function that passes if either validator passes


.. py:function:: not_validator(validator, error_message)

   Negate a validator (success becomes failure and vice versa).

   :param validator: The validator function to negate
   :param error_message: Error message for when the negated validator fails

   :returns: A new validator function that passes if the original validator fails


