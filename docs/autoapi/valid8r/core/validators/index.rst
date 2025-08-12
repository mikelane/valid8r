valid8r.core.validators
=======================

.. py:module:: valid8r.core.validators

.. autoapi-nested-parse::

   Core validators for validating values against specific criteria.

   This module provides a collection of validator functions for common validation scenarios.
   All validators follow the same pattern - they take a value and return a Maybe object
   that either contains the validated value or an error message.



Attributes
----------

.. autoapisummary::

   valid8r.core.validators.T
   valid8r.core.validators.U
   valid8r.core.validators.N


Classes
-------

.. autoapisummary::

   valid8r.core.validators.SupportsComparison
   valid8r.core.validators.Validator


Functions
---------

.. autoapisummary::

   valid8r.core.validators.minimum
   valid8r.core.validators.maximum
   valid8r.core.validators.between
   valid8r.core.validators.predicate
   valid8r.core.validators.length


Module Contents
---------------

.. py:class:: SupportsComparison

   Bases: :py:obj:`Protocol`


   Base class for protocol classes.

   Protocol classes are defined as::

       class Proto(Protocol):
           def meth(self) -> int:
               ...

   Such classes are primarily used with static type checkers that recognize
   structural subtyping (static duck-typing).

   For example::

       class C:
           def meth(self) -> int:
               return 0

       def func(x: Proto) -> int:
           return x.meth()

       func(C())  # Passes static type check

   See PEP 544 for details. Protocol classes decorated with
   @typing.runtime_checkable act as simple-minded runtime protocols that check
   only the presence of given attributes, ignoring their type signatures.
   Protocol classes can be generic, they are defined as::

       class GenProto[T](Protocol):
           def meth(self) -> T:
               ...


   .. py:method:: __le__(other, /)


   .. py:method:: __lt__(other, /)


   .. py:method:: __ge__(other, /)


   .. py:method:: __gt__(other, /)


   .. py:method:: __eq__(other, /)


   .. py:method:: __ne__(other, /)


   .. py:method:: __hash__(/)


.. py:data:: T

.. py:data:: U

.. py:data:: N

.. py:class:: Validator(func)

   Bases: :py:obj:`Generic`\ [\ :py:obj:`T`\ ]


   A wrapper class for validator functions that supports operator overloading.


   .. py:attribute:: func


   .. py:method:: __call__(value)

      Apply the validator to a value.

      :param value: The value to validate

      :returns: A Maybe containing either the validated value or an error



   .. py:method:: __and__(other)

      Combine with another validator using logical AND.

      :param other: Another validator to combine with

      :returns: A new validator that passes only if both validators pass



   .. py:method:: __or__(other)

      Combine with another validator using logical OR.

      :param other: Another validator to combine with

      :returns: A new validator that passes if either validator passes



   .. py:method:: __invert__()

      Negate this validator.

      :returns: A new validator that passes if this validator fails



.. py:function:: minimum(min_value, error_message = None)

   Create a validator that ensures a value is at least the minimum.

   :param min_value: The minimum allowed value
   :param error_message: Optional custom error message

   :returns: A validator function


.. py:function:: maximum(max_value, error_message = None)

   Create a validator that ensures a value is at most the maximum.

   :param max_value: The maximum allowed value
   :param error_message: Optional custom error message

   :returns: A validator function


.. py:function:: between(min_value, max_value, error_message = None)

   Create a validator that ensures a value is between minimum and maximum (inclusive).

   :param min_value: The minimum allowed value
   :param max_value: The maximum allowed value
   :param error_message: Optional custom error message

   :returns: A validator function


.. py:function:: predicate(pred, error_message)

   Create a validator using a custom predicate function.

   :param pred: A function that takes a value and returns a boolean
   :param error_message: Error message when validation fails

   :returns: A validator function


.. py:function:: length(min_length, max_length, error_message = None)

   Create a validator that ensures a string's length is within bounds.

   :param min_length: Minimum length of the string
   :param max_length: Maximum length of the string
   :param error_message: Optional custom error message

   :returns: A validator function


