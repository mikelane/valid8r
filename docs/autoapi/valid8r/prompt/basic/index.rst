valid8r.prompt.basic
====================

.. py:module:: valid8r.prompt.basic

.. autoapi-nested-parse::

   Basic input prompting functions with validation support.

   This module provides functionality for prompting users for input via the command line
   with built-in parsing, validation, and retry logic.



Attributes
----------

.. autoapisummary::

   valid8r.prompt.basic.T


Classes
-------

.. autoapisummary::

   valid8r.prompt.basic.PromptConfig


Functions
---------

.. autoapisummary::

   valid8r.prompt.basic.ask


Module Contents
---------------

.. py:data:: T

.. py:class:: PromptConfig

   Configuration for the ask function.


   .. py:attribute:: parser
      :type:  collections.abc.Callable[[str], valid8r.core.maybe.Maybe[T]] | None
      :value: None



   .. py:attribute:: validator
      :type:  collections.abc.Callable[[T], valid8r.core.maybe.Maybe[T]] | None
      :value: None



   .. py:attribute:: error_message
      :type:  str | None
      :value: None



   .. py:attribute:: default
      :type:  T | None
      :value: None



   .. py:attribute:: retry
      :type:  bool | int
      :value: False



.. py:function:: ask(prompt_text, *, parser = None, validator = None, error_message = None, default = None, retry = False, _test_mode = False)

   Prompt the user for input with validation.

   :param prompt_text: The prompt to display to the user
   :param parser: Function to convert string to desired type
   :param validator: Function to validate the parsed value
   :param error_message: Custom error message for invalid input
   :param default: Default value to use if input is empty
   :param retry: If True or an integer, retry on invalid input
   :param _test_mode: Hidden parameter for testing the final return path

   :returns: A Maybe containing the validated input or an error

   .. admonition:: Examples

      >>> # This would prompt the user and validate their input
      >>> from valid8r.core import parsers, validators
      >>> age = ask(
      ...     "Enter your age: ",
      ...     parser=parsers.parse_int,
      ...     validator=validators.minimum(0),
      ...     retry=True
      ... )


