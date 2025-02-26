Getting Started
===============

Installation
------------

Valid8r requires Python 3.11 or higher. You can install it using pip:

.. code-block:: bash

   pip install valid8r

Or, if you use Poetry:

.. code-block:: bash

   poetry add valid8r

Basic Concepts
--------------

Valid8r is built around a few key concepts:

1. **Maybe Monad**: A functional programming construct that helps handle operations that might fail, without using exceptions.
2. **Parsers**: Functions that convert strings to other data types, returning Maybe objects.
3. **Validators**: Functions that validate values based on specific rules, returning Maybe objects.
4. **Combinators**: Functions that allow combining validators with logical operations (AND, OR, NOT).
5. **Prompts**: Functions that ask for user input and handle validation and retries.

These components work together to create a clean, flexible validation system.

Your First Validation
---------------------

Here's a simple example that validates a number:

.. code-block:: python

   from valid8r import parsers, validators

   # Parse a string to an integer
   result = parsers.parse_int("42")

   if result.is_just():
       print(f"Parsed successfully: {result.value()}")
   else:
       print(f"Error: {result.error()}")

   # Validate that the number is positive
   parsed_value = parsers.parse_int("42")
   validated = parsed_value.bind(lambda x: validators.minimum(0)(x))

   if validated.is_just():
       print(f"Valid positive number: {validated.value()}")
   else:
       print(f"Error: {validated.error()}")

Using the Maybe Monad
---------------------

The Maybe monad is at the heart of Valid8r. It represents a value that might exist (`Just`) or might not exist (`Nothing`):

.. code-block:: python

   from valid8r import Maybe

   # Creating a Just (success case)
   success = Maybe.just(42)
   print(success.is_just())  # True
   print(success.value())    # 42

   # Creating a Nothing (failure case)
   failure = Maybe.nothing("Something went wrong")
   print(failure.is_nothing())  # True
   print(failure.error())       # "Something went wrong"

   # Using bind for chaining operations
   result = Maybe.just(5).bind(
       lambda x: Maybe.just(x * 2)
   )
   print(result.value())  # 10

   # Error propagation happens automatically
   result = Maybe.nothing("First error").bind(
       lambda x: Maybe.just(x * 2)
   )
   print(result.error())  # "First error"

Chaining Validators
-------------------

One of the powerful features of Valid8r is the ability to chain validators using operators:

.. code-block:: python

   from valid8r import validators

   # Create a complex validation rule: between 1-100 AND (even OR divisible by 5)
   is_in_range = validators.between(1, 100)
   is_even = validators.predicate(lambda x: x % 2 == 0, "Number must be even")
   is_div_by_5 = validators.predicate(lambda x: x % 5 == 0, "Number must be divisible by 5")

   # Combine validators with & (AND) and | (OR)
   valid_number = is_in_range & (is_even | is_div_by_5)

   # Test the combined validator
   result = valid_number(42)  # Valid: in range and even
   print(result.is_just())  # True

   result = valid_number(35)  # Valid: in range and divisible by 5
   print(result.is_just())  # True

   result = valid_number(37)  # Invalid: in range but neither even nor divisible by 5
   print(result.is_nothing())  # True
   print(result.error())  # Shows the error message

Prompting for User Input
------------------------

Valid8r makes it easy to prompt for user input with validation:

.. code-block:: python

   from valid8r import prompt, parsers, validators

   # Ask for a positive number with retry
   number = prompt.ask(
       "Enter a positive number: ",
       parser=parsers.parse_int,
       validator=validators.minimum(0),
       retry=True
   )

   if number.is_just():
       print(f"You entered: {number.value()}")

   # Ask for a value with a default
   age = prompt.ask(
       "Enter your age: ",
       parser=parsers.parse_int,
       validator=validators.between(0, 120),
       default=30,
       retry=True
   )

   if age.is_just():
       print(f"Your age is: {age.value()}")

Next Steps
----------

Now that you understand the basics, you can explore:

* The :doc:`Maybe monad </user_guide/maybe_monad>` in more detail
* Available :doc:`parsers </user_guide/parsers>` for different data types
* Built-in :doc:`validators </user_guide/validators>` and how to create custom ones
* Advanced :doc:`prompting techniques </user_guide/prompting>`
* :doc:`Advanced usage patterns </user_guide/advanced_usage>`

Or jump right to the :doc:`API reference </api/core>` for comprehensive documentation of all functions and classes.