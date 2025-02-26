valid8r.core.combinators
========================

.. py:module:: valid8r.core.combinators

.. autoapi-nested-parse::

   Combinators for creating complex validation rules.



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


.. py:function:: or_else(first, second)

   Combine two validators with logical OR (either can succeed).


.. py:function:: not_validator(validator, error_message)

   Negate a validator (success becomes failure and vice versa).


