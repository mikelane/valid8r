valid8r.testing
===============

.. py:module:: valid8r.testing

.. autoapi-nested-parse::

   Testing utilities for Valid8r.

   This module provides tools for testing applications that use Valid8r,
   making it easier to test validation logic, user prompts, and Maybe monads.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/valid8r/testing/assertions/index
   /autoapi/valid8r/testing/generators/index
   /autoapi/valid8r/testing/mock_input/index


Functions
---------

.. autoapisummary::

   valid8r.testing.assert_maybe_failure
   valid8r.testing.assert_maybe_success
   valid8r.testing.generate_random_inputs
   valid8r.testing.generate_test_cases
   valid8r.testing.test_validator_composition
   valid8r.testing.MockInputContext
   valid8r.testing.configure_mock_input


Package Contents
----------------

.. py:function:: assert_maybe_failure(result, expected_error)

   Assert that a Maybe is a Failure with the expected error message.

   :param result: The Maybe instance to check
   :param expected_error: The expected error message inside the Maybe

   :returns: True if result is a Failure with the expected error, False otherwise

   .. admonition:: Examples

      >>> result = Maybe.failure("Invalid input")
      >>> assert_maybe_failure(result, "Invalid input")  # Returns True
      >>> assert_maybe_failure(result, "Other error")  # Returns False


.. py:function:: assert_maybe_success(result, expected_value)

   Assert that a Maybe is a Success with the expected value.

   :param result: The Maybe instance to check
   :param expected_value: The expected value inside the Maybe

   :returns: True if result is a Success with the expected value, False otherwise

   .. admonition:: Examples

      >>> result = Maybe.success(42)
      >>> assert_maybe_success(result, 42)  # Returns True
      >>> assert_maybe_success(result, 43)  # Returns False


.. py:function:: generate_random_inputs(validator, count = 20, range_min = -100, range_max = 100)

   Generate random inputs that include both valid and invalid cases.

   :param validator: The validator to test against
   :param count: Number of inputs to generate
   :param range_min: Minimum value for generated integers
   :param range_max: Maximum value for generated integers

   :returns: A list of random integers

   .. admonition:: Examples

      >>> inputs = generate_random_inputs(minimum(0), count=10)
      >>> len(inputs)
      10


.. py:function:: generate_test_cases(validator)

   Generate test cases for a validator.

   This function analyzes the validator and generates appropriate test cases
   that should pass and fail the validation.

   :param validator: The validator to generate test cases for

   :returns: A dictionary with 'valid' and 'invalid' lists of test cases

   .. admonition:: Examples

      >>> test_cases = generate_test_cases(minimum(10))
      >>> test_cases
      {'valid': [10, 11, 15, 20, 100], 'invalid': [9, 5, 0, -10]}


.. py:function:: test_validator_composition(validator)

   Test a composed validator with various inputs to verify it works correctly.

   :param validator: The composed validator to test

   :returns: True if the validator behaves as expected, False otherwise

   .. admonition:: Examples

      >>> is_valid_age = minimum(0) & maximum(120)
      >>> test_validator_composition(is_valid_age)  # Returns True


.. py:function:: MockInputContext(inputs = None)

   Context manager for mocking user input.

   :param inputs: A list of strings to be returned sequentially by input().

   :Yields: None

   .. admonition:: Examples

      >>> with MockInputContext(["yes", "42"]):
      ...     answer = input("Continue? ")  # returns "yes"
      ...     number = input("Enter number: ")  # returns "42"


.. py:function:: configure_mock_input(inputs)

   Configure input to be mocked globally.

   Unlike MockInputContext, this function replaces the input function
   globally without restoring it automatically. Use for simple tests
   where cleanup isn't critical.

   :param inputs: A list of strings to be returned sequentially by input().

   .. admonition:: Examples

      >>> configure_mock_input(["yes", "42"])
      >>> answer = input("Continue? ")  # returns "yes"
      >>> number = input("Enter number: ")  # returns "42"
