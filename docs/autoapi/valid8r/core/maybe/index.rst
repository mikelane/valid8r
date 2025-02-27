valid8r.core.maybe
==================

.. py:module:: valid8r.core.maybe

.. autoapi-nested-parse::

   Maybe monad for clean error handling.



Attributes
----------

.. autoapisummary::

   valid8r.core.maybe.T
   valid8r.core.maybe.U


Classes
-------

.. autoapisummary::

   valid8r.core.maybe.Maybe


Module Contents
---------------

.. py:data:: T

.. py:data:: U

.. py:class:: Maybe(value = None, error = None)

   Bases: :py:obj:`Generic`\ [\ :py:obj:`T`\ ]


   A Maybe monad implementation that handles computations which might fail.

   The Maybe monad is a functional programming concept that provides a clean
   way to handle operations that might fail, without using exceptions for
   control flow.

   .. admonition:: Examples

      >>> from valid8r.core.maybe import Maybe
      >>> Maybe.just(5)
      Just(5)
      >>> Maybe.nothing("Error")
      Nothing(Error)
      >>> Maybe.just(5).bind(lambda x: Maybe.just(x * 2))
      Just(10)


   .. py:method:: just(value)
      :staticmethod:


      Create a Maybe containing a value.



   .. py:method:: nothing(error)
      :staticmethod:


      Create a Maybe containing an error.



   .. py:method:: bind(f)

      Chain operations that might fail.



   .. py:method:: map(f)

      Transform the value if present.



   .. py:method:: is_just()

      Check if this Maybe contains a value.



   .. py:method:: is_nothing()

      Check if this Maybe contains an error.



   .. py:method:: value()

      Get the contained value. Unsafe if is_nothing().



   .. py:method:: error()

      Get the error message. Unsafe if is_just().



   .. py:method:: value_or(default)

      Safely get the value or a default.



   .. py:method:: __str__()

      Get a string representation of the Maybe.



