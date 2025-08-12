valid8r
=======

.. py:module:: valid8r

.. autoapi-nested-parse::

   Valid8r: A clean, flexible input validation library for Python.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/valid8r/core/index
   /autoapi/valid8r/prompt/index
   /autoapi/valid8r/testing/index


Attributes
----------

.. autoapisummary::

   valid8r.__version__


Classes
-------

.. autoapisummary::

   valid8r.Maybe


Package Contents
----------------

.. py:data:: __version__
   :value: '0.1.0'


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



