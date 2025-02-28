valid8r.testing.generators
==========================

.. py:module:: valid8r.testing.generators

.. autoapi-nested-parse::

   Generators for test cases and test input data.



Attributes
----------

.. autoapisummary::

   valid8r.testing.generators.T


Functions
---------

.. autoapisummary::

   valid8r.testing.generators.generate_test_cases
   valid8r.testing.generators.generate_random_inputs
   valid8r.testing.generators.test_validator_composition


Module Contents
---------------

.. py:data:: T

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


.. py:function:: test_validator_composition(validator)

   Test a composed validator with various inputs to verify it works correctly.

   :param validator: The composed validator to test

   :returns: True if the validator behaves as expected, False otherwise

   .. admonition:: Examples

      >>> is_valid_age = minimum(0) & maximum(120)
      >>> test_validator_composition(is_valid_age)  # Returns True


