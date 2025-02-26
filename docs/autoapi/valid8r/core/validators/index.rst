valid8r.core.validators
=======================

.. py:module:: valid8r.core.validators


Attributes
----------

.. autoapisummary::

   valid8r.core.validators.T
   valid8r.core.validators.U


Classes
-------

.. autoapisummary::

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

.. py:data:: T

.. py:data:: U

.. py:class:: Validator(func)

   Bases: :py:obj:`Generic`\ [\ :py:obj:`T`\ ]


   A wrapper class for validator functions that supports operator overloading.


   .. py:attribute:: func


   .. py:method:: __call__(value)


   .. py:method:: __and__(other)


   .. py:method:: __or__(other)


   .. py:method:: __invert__()


.. py:function:: minimum(min_value, error_message = None)

   Create a validator that ensures a value is at least the minimum.


.. py:function:: maximum(max_value, error_message = None)

   Create a validator that ensures a value is at most the maximum.


.. py:function:: between(min_value, max_value, error_message = None)

   Create a validator that ensures a value is between minimum and maximum (inclusive).


.. py:function:: predicate(pred, error_message)

   Create a validator using a custom predicate function.


.. py:function:: length(min_length, max_length, error_message = None)

   Create a validator that ensures a string's length is within bounds.


