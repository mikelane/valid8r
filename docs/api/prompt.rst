Prompt API Reference
====================

This section provides detailed documentation for the prompt module of Valid8r. The prompt module offers a robust interface for collecting and validating user input in command-line applications.

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

   Example with pattern matching:

   .. code-block:: python

      from valid8r import prompt, parsers
      from valid8r.core.maybe import Success, Failure

      result = prompt.ask("Enter your name: ")
      match result:
          case Success(value):
              print(f"Hello, {value}!")
          case Failure(error):
              print(f"Error: {error}")

Parameters in Detail
--------------------

prompt_text
~~~~~~~~~~~

The text to display to the user. If a default value is provided, the default will be shown in brackets after the prompt text.

.. code-block:: python

   from valid8r import prompt
   from valid8r.core.maybe import Success, Failure

   # Without default
   result = prompt.ask("Enter your name: ")
   # Displays: "Enter your name: "

   # With default
   result = prompt.ask("Enter your name: ", default="Guest")
   # Displays: "Enter your name: [Guest]: "

   match result:
       case Success(value):
           print(f"Using name: {value}")  # Will be "Guest" if user pressed Enter
       case Failure(error):
           print(f"Error: {error}")

parser
~~~~~~

A function that converts the string input to the desired type. It should take a string and return a Maybe object. If not provided, a default parser that returns the input string is used.

.. code-block:: python

   from valid8r import prompt, parsers, Maybe
   from valid8r.core.maybe import Success, Failure

   # Default parser (identity)
   result = prompt.ask("Enter your name: ")
   match result:
       case Success(value):
           print(f"Name: {value}")
       case Failure(error):
           print(f"Error: {error}")

   # Integer parser
   result = prompt.ask("Enter your age: ", parser=parsers.parse_int)
   match result:
       case Success(value):
           print(f"Age: {value}")
       case Failure(error):
           print(f"Error: {error}")

   # Float parser
   result = prompt.ask("Enter price: ", parser=parsers.parse_float)
   match result:
       case Success(value):
           print(f"Price: ${value:.2f}")
       case Failure(error):
           print(f"Error: {error}")

   # Boolean parser
   result = prompt.ask("Proceed? (yes/no): ", parser=parsers.parse_bool)
   match result:
       case Success(value) if value:
           print("Proceeding...")
       case Success(_):
           print("Operation cancelled")
       case Failure(error):
           print(f"Error: {error}")

   # Custom parser
   def email_parser(s):
       import re
       if re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", s):
           return Maybe.success(s)
       return Maybe.failure("Invalid email format")

   result = prompt.ask("Enter email: ", parser=email_parser)
   match result:
       case Success(value):
           print(f"Email: {value}")
       case Failure(error):
           print(f"Error: {error}")

validator
~~~~~~~~~

A function that validates the parsed value. It should take a value and return a Maybe object. If not provided, a default validator that always passes is used.

.. code-block:: python

   from valid8r import prompt, parsers, validators
   from valid8r.core.maybe import Success, Failure

   # No validator (always passes)
   result = prompt.ask("Enter your name: ")
   match result:
       case Success(value):
           print(f"Name: {value}")
       case Failure(error):
           print(f"Error: {error}")

   # Minimum value validator
   result = prompt.ask(
       "Enter a positive number: ",
       parser=parsers.parse_int,
       validator=validators.minimum(0)
   )
   match result:
       case Success(value):
           print(f"Positive number: {value}")
       case Failure(error):
           print(f"Error: {error}")

   # Range validator
   result = prompt.ask(
       "Enter your age (0-120): ",
       parser=parsers.parse_int,
       validator=validators.between(0, 120)
   )
   match result:
       case Success(value):
           print(f"Age: {value}")
       case Failure(error):
           print(f"Error: {error}")

   # String length validator
   result = prompt.ask(
       "Enter username (3-20 chars): ",
       validator=validators.length(3, 20)
   )
   match result:
       case Success(value):
           print(f"Username: {value}")
       case Failure(error):
           print(f"Error: {error}")

   # Custom validator
   def is_even(x):
       if x % 2 == 0:
           return Maybe.success(x)
       return Maybe.failure("Value must be even")

   result = prompt.ask(
       "Enter an even number: ",
       parser=parsers.parse_int,
       validator=is_even
   )
   match result:
       case Success(value):
           print(f"Even number: {value}")
       case Failure(error):
           print(f"Error: {error}")

error_message
~~~~~~~~~~~~~

A custom error message to display when validation fails. If not provided, the error message from the parser or validator will be used.

.. code-block:: python

   from valid8r import prompt, parsers, validators
   from valid8r.core.maybe import Success, Failure

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

   match result:
       case Success(value):
           print(f"Valid number: {value}")
       case Failure(error):
           print(f"Final error: {error}")

default
~~~~~~~

A default value to use if the user provides empty input. If provided, the default will be shown in brackets after the prompt text.

.. code-block:: python

   from valid8r import prompt, parsers
   from valid8r.core.maybe import Success, Failure

   # With default value
   result = prompt.ask(
       "Enter your age: ",
       parser=parsers.parse_int,
       default=30
   )
   # Displays: "Enter your age: [30]: "

   # If user presses Enter without typing:
   match result:
       case Success(value):
           print(f"Using age: {value}")  # Will show 30
       case Failure(error):
           print(f"Error: {error}")

   # Default with validation
   result = prompt.ask(
       "Enter port number: ",
       parser=parsers.parse_int,
       validator=validators.between(1024, 65535),
       default=8080
   )
   match result:
       case Success(value):
           print(f"Using port: {value}")
       case Failure(error):
           print(f"Error: {error}")

retry
~~~~~

Controls retry behavior for invalid input:

- If ``False`` (default): No retries, return a Failure with the error for invalid input
- If ``True``: Retry indefinitely until valid input is provided
- If an integer: Retry that many times before returning a Failure with the error

.. code-block:: python

   from valid8r import prompt, parsers, validators
   from valid8r.core.maybe import Success, Failure

   # No retries (default)
   result = prompt.ask(
       "Enter your age: ",
       parser=parsers.parse_int,
       validator=validators.between(0, 120)
   )
   # If user enters invalid input, returns Failure
   match result:
       case Success(value):
           print(f"Age: {value}")
       case Failure(error):
           print(f"Error: {error}")

   # Infinite retries
   result = prompt.ask(
       "Enter your age: ",
       parser=parsers.parse_int,
       validator=validators.between(0, 120),
       retry=True
   )
   # Keeps asking until valid input is provided
   # This will always return Success if it returns at all
   match result:
       case Success(value):
           print(f"Age: {value}")
       case Failure(_):
           print("This won't happen unless interrupted")

   # Limited retries
   result = prompt.ask(
       "Enter your age: ",
       parser=parsers.parse_int,
       validator=validators.between(0, 120),
       retry=3
   )
   # Allows up to 3 retry attempts
   # If all fail, returns Failure
   match result:
       case Success(value):
           print(f"Age: {value}")
       case Failure(error):
           print(f"Failed after 3 attempts: {error}")

Return Value
------------

The ``ask`` function returns a Maybe object:

- If the input is valid: Returns a Success containing the validated value
- If the input is invalid and retries are exhausted or disabled: Returns a Failure with an error message

.. code-block:: python

   from valid8r import prompt, parsers
   from valid8r.core.maybe import Success, Failure

   # Check the result with pattern matching
   result = prompt.ask("Enter your age: ", parser=parsers.parse_int)
   match result:
       case Success(value):
           print(f"Your age is {value}")
       case Failure(error):
           print(f"Invalid input: {error}")

Error Display
-------------

When retries are enabled, error messages are displayed to the user:

.. code-block:: python

   from valid8r import prompt, parsers, validators
   from valid8r.core.maybe import Success, Failure

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

   # After all retries are exhausted, returns Failure

Integration with Parsers and Validators
---------------------------------------

The prompt module is designed to work seamlessly with the parsers and validators modules:

.. code-block:: python

   from valid8r import prompt, parsers, validators
   from valid8r.core.maybe import Success, Failure

   # Complete integration example
   age = prompt.ask(
       "Enter your age: ",
       parser=parsers.parse_int,
       validator=validators.between(0, 120),
       error_message="Please enter a valid age between 0 and 120",
       default=30,
       retry=True
   )

   match age:
       case Success(value):
           print(f"Age: {value}")
       case Failure(error):
           print(f"Error: {error}")

Processing Multiple Inputs
--------------------------

When collecting multiple inputs, pattern matching allows for elegant handling of all outcomes:

.. code-block:: python

   from valid8r import prompt, parsers, validators
   from valid8r.core.maybe import Success, Failure

   # Collect multiple inputs
   def collect_user_data():
       name = prompt.ask("Enter name: ", retry=True)
       age = prompt.ask(
           "Enter age: ",
           parser=parsers.parse_int,
           validator=validators.between(0, 120),
           retry=True
       )
       email = prompt.ask("Enter email: ", retry=True)

       # Process all inputs together
       match (name, age, email):
           case (Success(name_val), Success(age_val), Success(email_val)):
               return {
                   "name": name_val,
                   "age": age_val,
                   "email": email_val
               }
           case (Failure(error), _, _):
               print(f"Name error: {error}")
           case (_, Failure(error), _):
               print(f"Age error: {error}")
           case (_, _, Failure(error)):
               print(f"Email error: {error}")

       return None

   user = collect_user_data()
   if user:
       print(f"User created: {user['name']}, age {user['age']}")

Hidden Parameters for Testing
-----------------------------

The ``ask`` function includes a hidden parameter for testing:

.. py:function:: valid8r.prompt.basic.ask(..., _test_mode=False)

   Hidden parameter for testing.

   :param _test_mode: If True, returns a Failure Maybe without prompting
   :return: A Failure Maybe with a default error message

This parameter is not intended for normal use and is primarily for testing purposes.

.. code-block:: python

   from valid8r import prompt
   from valid8r.core.maybe import Success, Failure

   # For testing only
   result = prompt.ask("This won't be displayed:", _test_mode=True)
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(f"Expected test error: {error}")

Internal Implementation Details
-------------------------------

The prompt module uses several internal helper functions to manage the prompting process:

.. py:function:: valid8r.prompt.basic._handle_user_input(prompt_text, default)

   Handle getting user input and displaying the prompt.

   :param prompt_text: The text to display to the user
   :param default: Optional default value to show in brackets
   :return: A tuple of (user_input, use_default) where use_default is True if the default value should be used

.. py:function:: valid8r.prompt.basic._process_input(user_input, parser, validator)

   Process user input by parsing and validating.

   :param user_input: The string input from the user
   :param parser: Function to convert string to desired type
   :param validator: Function to validate the parsed value
   :return: A Maybe containing the validated value or an error

.. py:function:: valid8r.prompt.basic._run_prompt_loop(prompt_text, parser, validator, default, max_retries, error_message)

   Run the prompt loop with retries.

   :param prompt_text: The text to display to the user
   :param parser: Function to convert string to desired type
   :param validator: Function to validate the parsed value
   :param default: Default value to use if input is empty
   :param max_retries: Maximum number of retry attempts
   :param error_message: Custom error message for invalid input
   :return: A Maybe containing the validated value or an error

.. py:function:: valid8r.prompt.basic._display_error(result_error, custom_error, max_retries, attempt)

   Display error message to the user.

   :param result_error: The error message from the result
   :param custom_error: Optional custom error message
   :param max_retries: Maximum number of retry attempts
   :param attempt: Current attempt number
   :return: None

Advanced Usage Patterns
-----------------------

For more advanced usage patterns, see the :doc:`Interactive Prompts </examples/interactive_prompts>` example section.

Combining with Pattern Matching
-------------------------------

The prompt module works especially well with pattern matching to create robust command-line interfaces:

.. code-block:: python

   from valid8r import prompt, parsers, validators
   from valid8r.core.maybe import Success, Failure
   import sys

   def main():
       print("Welcome to Task Manager")
       print("======================")

       while True:
           print("\nOptions:")
           print("1. Add Task")
           print("2. View Tasks")
           print("3. Exit")

           choice = prompt.ask(
               "Select an option (1-3): ",
               parser=parsers.parse_int,
               validator=validators.between(1, 3),
               retry=True
           )

           match choice:
               case Success(1):
                   add_task()
               case Success(2):
                   view_tasks()
               case Success(3):
                   print("Goodbye!")
                   sys.exit(0)
               case Failure(error):
                   print(f"Error: {error}")

   def add_task():
       # Implementation using prompt.ask and pattern matching
       task_name = prompt.ask("Task name: ", retry=True)

       priority_options = ["Low", "Medium", "High"]
       print("Priority options:")
       for i, priority in enumerate(priority_options, 1):
           print(f"{i}. {priority}")

       priority = prompt.ask(
           "Select priority (1-3): ",
           parser=parsers.parse_int,
           validator=validators.between(1, 3),
           retry=True
       )

       match (task_name, priority):
           case (Success(name), Success(p)):
               priority_text = priority_options[p - 1]
               print(f"Added task: {name} (Priority: {priority_text})")
           case (Failure(error), _):
               print(f"Task name error: {error}")
           case (_, Failure(error)):
               print(f"Priority error: {error}")

   def view_tasks():
       # Implementation
       print("No tasks available")

   if __name__ == "__main__":
       main()
