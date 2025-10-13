User Input Prompting
====================

The ``prompt`` module in Valid8r provides tools for interactively prompting users for input with built-in validation. This is particularly useful for command-line applications.

Basic Usage
-----------

.. code-block:: python

   from valid8r import prompt, parsers, validators
   from valid8r.core.maybe import Success, Failure

   # Ask for a simple string
   name = prompt.ask("Enter your name: ")
   match name:
       case Success(value):
           print(f"Hello, {value}!")
       case Failure(error):
           print(f"Error: {error}")

   # Ask for an integer
   age = prompt.ask(
       "Enter your age: ",
       parser=parsers.parse_int
   )
   match age:
       case Success(value):
           print(f"You are {value} years old.")
       case Failure(error):
           print(f"Error: {error}")

   # Ask for a validated value
   score = prompt.ask(
       "Enter a score (0-100): ",
       parser=parsers.parse_int,
       validator=validators.between(0, 100)
   )
   match score:
       case Success(value):
           print(f"Score: {value}")
       case Failure(error):
           print(f"Error: {error}")

The ``ask`` Function
--------------------

The ``ask`` function is the main entry point for user input prompting:

.. code-block:: python

   def ask(
       prompt_text: str,
       parser: Callable[[str], Maybe[T]] = None,
       validator: Callable[[T], Maybe[T]] = None,
       error_message: str = None,
       default: T = None,
       retry: bool | int = False,
   ) -> Maybe[T]:
       """Prompt the user for input with validation."""

Parameters:

- **prompt_text**: The text to display to the user
- **parser**: A function to convert the string input to the desired type (defaults to identity function)
- **validator**: A function to validate the parsed value (defaults to always valid)
- **error_message**: Custom error message for invalid input
- **default**: Default value to use if the user provides empty input
- **retry**: If True, retry indefinitely on invalid input; if an integer, retry that many times

Return Value:

- A Maybe containing either the validated value (Success) or an error (Failure)

Default Values
--------------

You can provide a default value that will be used if the user enters nothing:

.. code-block:: python

   from valid8r import prompt, parsers
   from valid8r.core.maybe import Success, Failure

   # With a default value
   age = prompt.ask(
       "Enter your age: ",
       parser=parsers.parse_int,
       default=30
   )

   # The prompt will show the default: "Enter your age: [30]: "
   # If the user presses Enter without typing anything:
   match age:
       case Success(value):
           print(f"Using age: {value}")  # Will be 30 if user pressed Enter
       case Failure(error):
           print(f"Error: {error}")

Error Handling and Retries
--------------------------

By default, if the user enters invalid input, ``ask`` will return a Failure with an error message. You can enable retries to keep asking until valid input is provided:

.. code-block:: python

   from valid8r import prompt, parsers, validators
   from valid8r.core.maybe import Success, Failure

   # No retry (default)
   age = prompt.ask(
       "Enter your age (0-120): ",
       parser=parsers.parse_int,
       validator=validators.between(0, 120)
   )
   # If user enters "abc" or -5, a Failure is returned
   match age:
       case Success(value):
           print(f"Age: {value}")
       case Failure(error):
           print(f"Invalid input: {error}")

   # Infinite retries
   age = prompt.ask(
       "Enter your age (0-120): ",
       parser=parsers.parse_int,
       validator=validators.between(0, 120),
       retry=True  # Keep asking until valid input
   )
   # This will always return Success if it returns at all
   match age:
       case Success(value):
           print(f"Age: {value}")
       case Failure(_):
           print("This won't happen unless interrupted")

   # Limited retries
   age = prompt.ask(
       "Enter your age (0-120): ",
       parser=parsers.parse_int,
       validator=validators.between(0, 120),
       retry=3  # Allow 3 attempts
   )
   # If valid input is provided within 3 attempts, Success is returned
   # Otherwise, Failure is returned
   match age:
       case Success(value):
           print(f"Age: {value}")
       case Failure(error):
           print(f"Failed after maximum retries: {error}")

When retry is enabled, error messages are displayed to the user:

.. code-block:: text

   Enter your age (0-120): abc
   Error: Input must be a valid integer
   Enter your age (0-120): -5
   Error: Value must be between 0 and 120
   Enter your age (0-120): 42
   # Valid input, function returns Success(42)

Custom Error Messages
---------------------

You can provide a custom error message that overrides the default ones:

.. code-block:: python

   from valid8r import prompt, parsers
   from valid8r.core.maybe import Success, Failure

   age = prompt.ask(
       "Enter your age: ",
       parser=parsers.parse_int,
       error_message="Please enter a valid age as a positive number",
       retry=True
   )

   # If user enters "abc":
   # Error: Please enter a valid age as a positive number
   # The prompt will keep asking with this error message until valid input

Processing User Input
---------------------

Using pattern matching to process user input results:

.. code-block:: python

   from valid8r import prompt, parsers, validators
   from valid8r.core.maybe import Success, Failure

   def process_age_input():
       age = prompt.ask(
           "Enter your age: ",
           parser=parsers.parse_int,
           validator=validators.between(0, 120),
           retry=3
       )

       match age:
           case Success(value) if value < 18:
               return f"You are {value} years old. You are a minor."
           case Success(value) if value >= 65:
               return f"You are {value} years old. You are a senior citizen."
           case Success(value):
               return f"You are {value} years old. You are an adult."
           case Failure(error):
               return f"Could not process age: {error}"

   result = process_age_input()
   print(result)

Common Patterns
---------------

Here are some common patterns for using the prompt module:

Password Input
~~~~~~~~~~~~~~

.. code-block:: python

   from valid8r import prompt, validators, Maybe
   from valid8r.core.maybe import Success, Failure
   from getpass import getpass

   # Custom parser that uses getpass for hidden input
   def password_parser(prompt_text):
       password = getpass(prompt_text)
       return Maybe.success(password)

   # Password validation
   password_validator = validators.length(8, 64) & validators.predicate(
       lambda p: any(c.isupper() for c in p) and any(c.isdigit() for c in p),
       "Password must contain at least one uppercase letter and one digit"
   )

   password = prompt.ask(
       "Enter password: ",
       parser=lambda _: password_parser("Password: "),
       validator=password_validator,
       retry=True
   )

   match password:
       case Success(value):
           print(f"Password accepted: {'*' * len(value)}")
       case Failure(error):
           print(f"Password error: {error}")

Confirmation Prompts
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from valid8r import prompt, parsers
   from valid8r.core.maybe import Success, Failure

   # Ask for confirmation
   confirm = prompt.ask(
       "Are you sure? (y/n): ",
       parser=parsers.parse_bool,
       retry=True
   )

   match confirm:
       case Success(value) if value:
           print("Proceeding...")
       case Success(_):
           print("Operation cancelled.")
       case Failure(error):
           print(f"Error: {error}")

Menu Selection
~~~~~~~~~~~~~~

.. code-block:: python

   from valid8r import prompt, parsers, validators
   from valid8r.core.maybe import Success, Failure

   # Display menu
   print("Select an option:")
   print("1. View records")
   print("2. Add record")
   print("3. Delete record")
   print("4. Exit")

   # Get user selection
   selection = prompt.ask(
       "Enter your choice (1-4): ",
       parser=parsers.parse_int,
       validator=validators.between(1, 4),
       retry=True
   )

   match selection:
       case Success(1):
           print("Viewing records...")
       case Success(2):
           print("Adding record...")
       case Success(3):
           print("Deleting record...")
       case Success(4):
           print("Exiting...")
       case Failure(error):
           print(f"Error: {error}")

Interactive Applications
------------------------

The prompt module is ideal for building interactive command-line applications:

.. code-block:: python

   from valid8r import prompt, parsers, validators
   from valid8r.core.maybe import Success, Failure
   import sys

   def main():
       print("Contact Manager")
       print("===============")

       while True:
           print("\nOptions:")
           print("1. Add contact")
           print("2. View contacts")
           print("3. Exit")

           choice = prompt.ask(
               "Enter choice (1-3): ",
               parser=parsers.parse_int,
               validator=validators.between(1, 3),
               retry=True
           )

           match choice:
               case Success(1):
                   add_contact()
               case Success(2):
                   view_contacts()
               case Success(3):
                   print("Goodbye!")
                   sys.exit(0)
               case Failure(error):
                   print(f"Error: {error}")
                   continue

   def add_contact():
       # Implementation using prompt.ask
       name = prompt.ask("Enter name: ", retry=True)
       phone = prompt.ask("Enter phone: ", retry=True)

       match (name, phone):
           case (Success(name_val), Success(phone_val)):
               print(f"Added contact: {name_val}, {phone_val}")
           case (Failure(error), _):
               print(f"Name error: {error}")
           case (_, Failure(error)):
               print(f"Phone error: {error}")

   def view_contacts():
       # Implementation
       print("No contacts available")

   if __name__ == "__main__":
       main()

Best Practices
--------------

1. **Provide clear prompt text**: Make sure the user knows what kind of input is expected
2. **Include validation requirements**: For example, "Enter your age (0-120): "
3. **Use appropriate parsers**: Match the parser to the expected input type
4. **Enable retries for better UX**: Especially in interactive applications
5. **Provide helpful error messages**: Explain what went wrong and how to fix it
6. **Use default values where appropriate**: Makes input quicker for common cases
7. **Handle all result cases**: Always use pattern matching to handle both Success and Failure cases

Limitations
-----------

1. **Terminal-based only**: The prompt module is designed for command-line interfaces
2. **No input masking**: For sensitive input like passwords, use ``getpass`` module
3. **No colored output**: Error messages are displayed in plain text
4. **No interactive features**: No arrow key navigation, autocomplete, etc.

In the next section, we'll explore advanced usage patterns and more complex examples.
