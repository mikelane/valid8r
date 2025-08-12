valid8r.core.maybe
==================

.. py:module:: valid8r.core.maybe

.. autoapi-nested-parse::

   Maybe monad for clean error handling using Success and Failure types.



Attributes
----------

.. autoapisummary::

   valid8r.core.maybe.T
   valid8r.core.maybe.U


Classes
-------

.. autoapisummary::

   valid8r.core.maybe.Maybe
   valid8r.core.maybe.Success
   valid8r.core.maybe.Failure


Module Contents
---------------

.. py:data:: T

.. py:data:: U

.. py:class:: Maybe

   Bases: :py:obj:`Generic`\ [\ :py:obj:`T`\ ], :py:obj:`abc.ABC`


   Base class for the Maybe monad.


   .. py:method:: success(value)
      :staticmethod:


      Create a Success containing a value.



   .. py:method:: failure(error)
      :staticmethod:


      Create a Failure containing an error message.



   .. py:method:: is_success()
      :abstractmethod:


      Check if the Maybe is a Success.



   .. py:method:: is_failure()
      :abstractmethod:


      Check if the Maybe is a Failure.



   .. py:method:: bind(f)
      :abstractmethod:


      Chain operations that might fail.



   .. py:method:: map(f)
      :abstractmethod:


      Transform the value if present.



   .. py:method:: value_or(default)
      :abstractmethod:


      Return the contained value or the provided default if this is a Failure.



   .. py:method:: error_or(default)
      :abstractmethod:


      Return the error message or the provided default if this is a Success.



   .. py:method:: get_error()
      :abstractmethod:


      Get the error message if present, otherwise None.



.. py:class:: Success(value)

   Bases: :py:obj:`Maybe`\ [\ :py:obj:`T`\ ]


   Represents a successful computation with a value.


   .. py:attribute:: __match_args__
      :value: ('value',)



   .. py:attribute:: value


   .. py:method:: is_success()

      Check if the Maybe is a Success.



   .. py:method:: is_failure()

      Check if the Maybe is a Failure.



   .. py:method:: bind(f)

      Chain operations that might fail.



   .. py:method:: map(f)

      Transform the value.



   .. py:method:: value_or(_default)

      Return the contained value (default is ignored for Success).



   .. py:method:: error_or(default)

      Return the provided default since Success has no error.



   .. py:method:: get_error()

      Get None since Success has no error.



   .. py:method:: __str__()

      Get a string representation.



.. py:class:: Failure(error)

   Bases: :py:obj:`Maybe`\ [\ :py:obj:`T`\ ]


   Represents a failed computation with an error message.


   .. py:attribute:: __match_args__
      :value: ('error',)



   .. py:attribute:: error


   .. py:method:: is_success()

      Check if the Maybe is a Success.



   .. py:method:: is_failure()

      Check if the Maybe is a Failure.



   .. py:method:: bind(_f)

      Chain operations that might fail.

      Function is unused in Failure case as we always propagate the error.



   .. py:method:: map(_f)

      Transform the value if present.

      Function is unused in Failure case as we always propagate the error.



   .. py:method:: value_or(default)

      Return the provided default for Failure.



   .. py:method:: error_or(default)

      Return the error message for Failure (or provided default if empty).



   .. py:method:: get_error()

      Get the error message.



   .. py:method:: __str__()

      Get a string representation.



