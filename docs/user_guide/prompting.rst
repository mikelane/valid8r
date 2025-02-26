User Input Prompting
====================

The `prompt` module in Valid8r provides tools for interactively prompting users for input with built-in validation. This is particularly useful for command-line applications.

Basic Usage
-----------

.. code-block:: python

   from valid8r import prompt, parsers, validators

   # Ask for a simple string
   name = prompt.ask("Enter your name: ")
   if name.is_just():
       print(f"Hello, {name.value()}!")

   # Ask for an integer
   age = prompt.ask(
       "Enter your age: ",
       parser=parsers.parse_int
   )
   if age.is_just():
       print(f"You are {age.value()} years old.")

   # Ask for a validated value
   score = prompt.ask(
       "Enter a score (0-100): ",
       parser=parsers.parse_int,
       validator=validators.between(0, 100)
   )
   if score.is_just():
       print(f"Score: {score.value()}")

The `ask` Function
------------------

The `ask` function is the main entry point for user input prompting:

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

- A Maybe containing either the validated value or an error

Default Values
--------------

You can provide a default value that will be used if the user enters nothing:

.. code-block:: python

   from valid8r import prompt, parsers

   # With a default value
   age = prompt.ask(
       "Enter your age: ",
       parser=parsers.parse_int,
       default=30
   )

   # The prompt will show the default: "Enter your age: [30]: "
   # If the user presses Enter without typing anything, 30 will be used

Error Handling and Retries
--------------------------

By default, if the user enters invalid input, `ask` will return a Nothing with an error message. You can enable retries to keep asking until valid input is provided:

.. code-block:: python

   from valid8r import prompt, parsers, validators

   # No retry (default)
   age = prompt.ask(
       "Enter your age (0-120): ",
       parser=parsers.parse_int,
       validator=validators.between(0, 120)
   )
   # If user enters "abc" or -5, a Nothing is returned

   # Infinite retries
   age = prompt.ask(
       "Enter your age (0-120): ",
       parser=parsers.parse_int,
       validator=validators.between(0, 120),
       retry=True  # Keep asking until valid input
   )

   # Limited retries
   age = prompt.ask(
       "Enter your age (0-120): ",
       parser=parsers.parse_int,
       validator=validators.between(0, 120),
       retry=3  # Allow 3 attempts
   )

When retry is enabled, error messages are displayed to the user:

.. code-block:: text

   Enter your age (0-120): abc
   Error: Input must be a valid integer
   Enter your age (0-120): -5
   Error: Value must be between 0 and 120
   Enter your age (0-120): 42
   # Valid input, function returns

Custom Error Messages
---------------------

You can provide a custom error message that overrides the default ones:

.. code-block:: python

   from valid8r import prompt, parsers

   age = prompt.ask(
       "Enter your age: ",
       parser=parsers.parse_int,
       error_message="Please enter a valid age as a positive number",
       retry=True
   )

   # If user enters "abc":
   # Error: Please enter a valid age as a positive number

Common Patterns
---------------

Here are some common patterns for using the prompt module:

Password Input
~~~~~~~~~~~~~~

.. code-block:: python

   from valid8r import prompt, validators
   from getpass import getpass

   # Custom parser that uses getpass for hidden input
   def password_parser(prompt_text):
       password = getpass(prompt_text)
       return Maybe.just(password)

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

Confirmation Prompts
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from valid8r import prompt, parsers

   # Ask for confirmation
   confirm = prompt.ask(
       "Are you sure? (y/n): ",
       parser=parsers.parse_bool,
       retry=True
   )

   if confirm.is_just() and confirm.value():
       print("Proceeding...")
   else:
       print("Operation cancelled.")

Menu Selection
~~~~~~~~~~~~~~

.. code-block:: python

   from valid8r import prompt, parsers, validators

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

   if selection.is_just():
       if selection.value() == 1:
           print("Viewing records...")
       elif selection.value() == 2:
           print("Adding record...")
       elif selection.value() == 3:
           print("Deleting record...")
       else:  # 4
           print("Exiting...")

Complex Input Flow
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from valid8r import prompt, parsers, validators, Maybe

   # Get user information with validation
   name = prompt.ask("Enter your name: ", retry=True)

   age = prompt.ask(
       "Enter your age: ",
       parser=parsers.parse_int,
       validator=validators.between(0, 120),
       retry=True
   )

   # Custom email validation
   import re

   def is_valid_email(email):
       pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
       return bool(re.match(pattern, email))

   email = prompt.ask(
       "Enter your email: ",
       validator=validators.predicate(is_valid_email, "Invalid email format"),
       retry=True
   )

   # Create user record if all inputs are valid
   if all(result.is_just() for result in [name, age, email]):
       user = {
           "name": name.value(),
           "age": age.value(),
           "email": email.value()
       }
       print(f"User created: {user}")
   else:
       print("Failed to create user")

Interactive Applications
------------------------

The prompt module is ideal for building interactive command-line applications:

.. code-block:: python

   from valid8r import prompt, parsers, validators
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

           if not choice.is_just():
               continue

           if choice.value() == 1:
               add_contact()
           elif choice.value() == 2:
               view_contacts()
           else:
               print("Goodbye!")
               sys.exit(0)

   def add_contact():
       # Implementation using prompt.ask
       pass

   def view_contacts():
       # Implementation
       pass

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

Limitations
-----------

1. **Terminal-based only**: The prompt module is designed for command-line interfaces
2. **No input masking**: For sensitive input like passwords, use `getpass` module
3. **No colored output**: Error messages are displayed in plain text
4. **No interactive features**: No arrow key navigation, autocomplete, etc.

Next, we'll explore advanced usage patterns and more complex examples in the next section.