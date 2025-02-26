Prompt API Reference
====================

This section provides detailed documentation for the prompt module of Valid8r.

Basic Prompting
---------------

.. py:function:: valid8r.prompt.basic.ask(prompt_text, parser=None, validator=None, error_message=None, default=None, retry=False)

   Prompt the user for input with validation.

   :param prompt_text: The prompt to display to the user
   :param parser: Function to convert string to desired type (defaults to identity function)
   :param validator: Function to validate the parsed value (defaults to always valid)
   :param error_message: Custom error message for invalid input
   :param default: Default value to use if input is empty
   :param retry: If True or an integer, retry on invalid input
   :return: A Maybe containing the validated input or an error

Parameters in Detail
--------------------

prompt_text
~~~~~~~~~~~

The text to display to the user. If a default value is provided, the default will be shown in brackets after the prompt text.

.. code-block:: python

   # Without default
   result = prompt.ask("Enter your name: ")
   # Displays: "Enter your name: "

   # With default
   result = prompt.ask("Enter your name: ", default="Guest")
   # Displays: "Enter your name: [Guest]: "

parser
~~~~~~

A function that converts the string input to the desired type. It should take a string and return a Maybe object. If not provided, a default parser that returns the input string is used.

.. code-block:: python

   from valid8r import prompt, parsers

   # Default parser (identity)
   result = prompt.ask("Enter your name: ")

   # Integer parser
   result = prompt.ask("Enter your age: ", parser=parsers.parse_int)

   # Float parser
   result = prompt.ask("Enter price: ", parser=parsers.parse_float)

   # Boolean parser
   result = prompt.ask("Proceed? (yes/no): ", parser=parsers.parse_bool)

   # Custom parser
   def email_parser(s):
       import re
       if re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", s):
           return Maybe.just(s)
       return Maybe.nothing("Invalid email format")

   result = prompt.ask("Enter email: ", parser=email_parser)

validator
~~~~~~~~~

A function that validates the parsed value. It should take a value and return a Maybe object. If not provided, a default validator that always passes is used.

.. code-block:: python

   from valid8r import prompt, parsers, validators

   # No validator (always passes)
   result = prompt.ask("Enter your name: ")

   # Minimum value validator
   result = prompt.ask(
       "Enter a positive number: ",
       parser=parsers.parse_int,
       validator=validators.minimum(0)
   )

   # Range validator
   result = prompt.ask(
       "Enter your age (0-120): ",
       parser=parsers.parse_int,
       validator=validators.between(0, 120)
   )

   # String length validator
   result = prompt.ask(
       "Enter username (3-20 chars): ",
       validator=validators.length(3, 20)
   )

   # Custom validator
   def is_even(x):
       if x % 2 == 0:
           return Maybe.just(x)
       return Maybe.nothing("Value must be even")

   result = prompt.ask(
       "Enter an even number: ",
       parser=parsers.parse_int,
       validator=is_even
   )

error_message
~~~~~~~~~~~~~

A custom error message to display when validation fails. If not provided, the error message from the parser or validator will be used.

.. code-block:: python

   from valid8r import prompt, parsers, validators

   # Default error message
   result = prompt.ask(
       "Enter a positive number: ",
       parser=parsers.parse_int,
       validator=validators.minimum(0),
       retry=True
   )
   # If user enters "abc":
   # Displays: "Error: Input must be a valid integer"

   # Custom error message
   result = prompt.ask(
       "Enter a positive number: ",
       parser=parsers.parse_int,
       validator=validators.minimum(0),
       error_message="Please enter a positive whole number",
       retry=True
   )
   # If user enters "abc":
   # Displays: "Error: Please enter a positive whole number"

default
~~~~~~~

A default value to use if the user provides empty input. If provided, the default will be shown in brackets after the prompt text.

.. code-block:: python

   from valid8r import prompt, parsers

   # With default value
   result = prompt.ask(
       "Enter your age: ",
       parser=parsers.parse_int,
       default=30
   )
   # Displays: "Enter your age: [30]: "

   # If user presses Enter without typing:
   # result will be Just(30)

retry
~~~~~

Controls retry behavior for invalid input:

- If ``False`` (default): No retries, return a Nothing with the error for invalid input
- If ``True``: Retry indefinitely until valid input is provided
- If an integer: Retry that many times before returning a Nothing with the error

.. code-block:: python

   from valid8r import prompt, parsers, validators

   # No retries (default)
   result = prompt.ask(
       "Enter your age: ",
       parser=parsers.parse_int,
       validator=validators.between(0, 120)
   )
   # If user enters invalid input, returns Nothing

   # Infinite retries
   result = prompt.ask(
       "Enter your age: ",
       parser=parsers.parse_int,
       validator=validators.between(0, 120),
       retry=True
   )
   # Keeps asking until valid input is provided

   # Limited retries
   result = prompt.ask(
       "Enter your age: ",
       parser=parsers.parse_int,
       validator=validators.between(0, 120),
       retry=3
   )
   # Allows up to 3 retry attempts
   # If all fail, returns Nothing

Return Value
------------

The ``ask`` function returns a Maybe object:

- If the input is valid: Returns a Just containing the validated value
- If the input is invalid and retries are exhausted or disabled: Returns a Nothing with an error message

.. code-block:: python

   from valid8r import prompt, parsers

   # Check the result
   result = prompt.ask("Enter your age: ", parser=parsers.parse_int)

   if result.is_just():
       age = result.value()
       print(f"Your age is {age}")
   else:
       print(f"Invalid input: {result.error()}")

Error Display
-------------

When retries are enabled, error messages are displayed to the user:

.. code-block:: python

   from valid8r import prompt, parsers, validators

   result = prompt.ask(
       "Enter your age (0-120): ",
       parser=parsers.parse_int,
       validator=validators.between(0, 120),
       retry=3
   )

   # If user enters "abc":
   # Displays: "Error: Input must be a valid integer (2 attempt(s) remaining)"

   # If user then enters "-5":
   # Displays: "Error: Value must be between 0 and 120 (1 attempt(s) remaining)"

   # If user then enters "200":
   # Displays: "Error: Value must be between 0 and 120 (0 attempt(s) remaining)"

   # After all retries are exhausted, returns Nothing

Integration with Parsers and Validators
---------------------------------------

The prompt module is designed to work seamlessly with the parsers and validators modules:

.. code-block:: python

   from valid8r import prompt, parsers, validators

   # Complete integration example
   age = prompt.ask(
       "Enter your age: ",
       parser=parsers.parse_int,
       validator=validators.between(0, 120),
       error_message="Please enter a valid age between 0 and 120",
       default=30,
       retry=True
   )

   if age.is_just():
       print(f"Age: {age.value()}")
   else:
       print(f"Error: {age.error()}")

   # Email validation
   import re
   is_valid_email = validators.predicate(
       lambda s: bool(re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", s)),
       "Invalid email format"
   )

   email = prompt.ask(
       "Enter your email: ",
       validator=is_valid_email,
       retry=True
   )

   if email.is_just():
       print(f"Email: {email.value()}")

Hidden Parameters for Testing
-----------------------------

The ``ask`` function includes a hidden parameter for testing:

.. py:function:: valid8r.prompt.basic.ask(..., _test_mode=False)

   Hidden parameter for testing.

   :param _test_mode: If True, returns a failure Maybe without prompting
   :return: A failure Maybe with a default error message

This parameter is not intended for normal use and is primarily for testing purposes.

Advanced Usage Patterns
-----------------------

For more advanced usage patterns, see the :doc:`Interactive Prompts </examples/interactive_prompts>` example section.