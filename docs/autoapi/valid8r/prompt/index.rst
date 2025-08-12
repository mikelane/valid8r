valid8r.prompt
==============

.. py:module:: valid8r.prompt

.. autoapi-nested-parse::

   Input prompting functionality for command-line applications.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/valid8r/prompt/basic/index


Functions
---------

.. autoapisummary::

   valid8r.prompt.ask


Package Contents
----------------

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


