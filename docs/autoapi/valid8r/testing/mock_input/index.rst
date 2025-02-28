valid8r.testing.mock_input
==========================

.. py:module:: valid8r.testing.mock_input

.. autoapi-nested-parse::

   Utilities for mocking user input during tests.



Functions
---------

.. autoapisummary::

   valid8r.testing.mock_input.MockInputContext
   valid8r.testing.mock_input.configure_mock_input


Module Contents
---------------

.. py:function:: MockInputContext(inputs)

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


