valid8r.testing.assertions
==========================

.. py:module:: valid8r.testing.assertions

.. autoapi-nested-parse::

   Assertion helpers for testing with Maybe monads.



Attributes
----------

.. autoapisummary::

   valid8r.testing.assertions.T


Functions
---------

.. autoapisummary::

   valid8r.testing.assertions.assert_maybe_success
   valid8r.testing.assertions.assert_maybe_failure
   valid8r.testing.assertions.assert_error_equals


Module Contents
---------------

.. py:data:: T

.. py:function:: assert_maybe_success(result, expected_value)

   Assert that a Maybe is a Success with the expected value.

   :param result: The Maybe instance to check
   :param expected_value: The expected value inside the Maybe

   :returns: True if result is a Success with the expected value, False otherwise

   .. admonition:: Examples

      >>> result = Maybe.success(42)
      >>> assert_maybe_success(result, 42)  # Returns True
      >>> assert_maybe_success(result, 43)  # Returns False


.. py:function:: assert_maybe_failure(result, expected_error)

   Assert that a Maybe is a Failure with the expected error message.

   :param result: The Maybe instance to check
   :param expected_error: The expected error message inside the Maybe

   :returns: True if result is a Failure with the expected error, False otherwise

   .. admonition:: Examples

      >>> result = Maybe.failure("Invalid input")
      >>> assert_maybe_failure(result, "Invalid input")  # Returns True
      >>> assert_maybe_failure(result, "Other error")  # Returns False


.. py:function:: assert_error_equals(result, expected_error, default = '')

   Assert error via error_or helper.


