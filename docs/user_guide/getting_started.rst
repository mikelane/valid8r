Getting Started
===============

Installation
------------

Valid8r requires Python 3.11 or higher (supports Python 3.11-3.14).

**Basic Installation** (includes Pydantic integration):

.. code-block:: bash

   pip install valid8r

**With Optional Integrations**:

.. code-block:: bash

   # Click integration for CLI applications
   pip install 'valid8r[click]'

**Using uv** (recommended for faster dependency resolution):

.. code-block:: bash

   uv add valid8r
   # or with Click
   uv add "valid8r[click]"

**Using Poetry**:

.. code-block:: bash

   poetry add valid8r
   # or with Click
   poetry add "valid8r[click]"

**What's Included**:

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Feature
     - Installation
     - Import
   * - Core parsers & validators
     - ``pip install valid8r``
     - ``from valid8r import parsers, validators``
   * - **Pydantic integration**
     - *included by default*
     - ``from valid8r.integrations import validator_from_parser``
   * - **Click integration (CLI)**
     - ``pip install 'valid8r[click]'``
     - ``from valid8r.integrations import ParamTypeAdapter``

Basic Concepts
--------------

Valid8r is built around a few key concepts:

1. **Success and Failure Types**: Functional programming constructs that represent computations which succeed or fail, without using exceptions.
2. **Parsers**: Functions that convert strings to other data types, returning Success or Failure results.
3. **Validators**: Functions that validate values based on specific rules, returning Success or Failure results.
4. **Combinators**: Functions that allow combining validators with logical operations (AND, OR, NOT).
5. **Prompts**: Functions that ask for user input and handle validation and retries.

These components work together to create a clean, flexible validation system with elegant error handling via pattern matching.

Your First Validation
---------------------

Here's a simple example that validates a number:

.. code-block:: python

   from valid8r import parsers, validators
   from valid8r.core.maybe import Success, Failure

   # Parse a string to an integer
   result = parsers.parse_int("42")

   match result:
       case Success(value):
           print(f"Parsed successfully: {value}")  # Parsed successfully: 42
       case Failure(error):
           print(f"Error: {error}")

   # Validate that the number is positive
   parsed_value = parsers.parse_int("42")
   validated = parsed_value.bind(lambda x: validators.minimum(0)(x))

   match validated:
       case Success(value):
           print(f"Valid positive number: {value}")  # Valid positive number: 42
       case Failure(error):
           print(f"Error: {error}")

Using Success and Failure Types
-------------------------------

The Success and Failure types are at the heart of Valid8r. They represent a value that might exist (Success) or might not exist (Failure):

.. code-block:: python

   from valid8r import Maybe
   from valid8r.core.maybe import Success, Failure

   # Creating a Success (success case)
   success = Maybe.success(42)
   print(success.is_success())  # True

   # Creating a Failure (failure case)
   failure = Maybe.failure("Something went wrong")
   print(failure.is_failure())  # True

   # Using pattern matching
   result = Maybe.success(42)
   match result:
       case Success(value):
           print(f"Success: {value}")  # Success: 42
       case Failure(error):
           print(f"Error: {error}")

   # Pattern matching with failure
   result = Maybe.failure("An error occurred")
   match result:
       case Success(value):
           print(f"Success: {value}")
       case Failure(error):
           print(f"Error: {error}")  # Error: An error occurred

   # Using bind for chaining operations
   result = Maybe.success(5).bind(
       lambda x: Maybe.success(x * 2)
   )
   match result:
       case Success(value):
           print(value)  # 10
       case Failure(_):
           print("This won't happen")

   # Error propagation happens automatically
   result = Maybe.failure("First error").bind(
       lambda x: Maybe.success(x * 2)
   )
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # First error

Chaining Validators
-------------------

One of the powerful features of Valid8r is the ability to chain validators using operators:

.. code-block:: python

   from valid8r import validators
   from valid8r.core.maybe import Success, Failure

   # Create a complex validation rule: between 1-100 AND (even OR divisible by 5)
   is_in_range = validators.between(1, 100)
   is_even = validators.predicate(lambda x: x % 2 == 0, "Number must be even")
   is_div_by_5 = validators.predicate(lambda x: x % 5 == 0, "Number must be divisible by 5")

   # Combine validators with & (AND) and | (OR)
   valid_number = is_in_range & (is_even | is_div_by_5)

   # Test the combined validator with pattern matching
   result = valid_number(42)  # Valid: in range and even
   match result:
       case Success(value):
           print(f"Valid number: {value}")  # Valid number: 42
       case Failure(error):
           print(f"Error: {error}")

   result = valid_number(35)  # Valid: in range and divisible by 5
   match result:
       case Success(value):
           print(f"Valid number: {value}")  # Valid number: 35
       case Failure(error):
           print(f"Error: {error}")

   result = valid_number(37)  # Invalid: in range but neither even nor divisible by 5
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(f"Error: {error}")  # Error: Number must be divisible by 5

   # Pattern matching with conditions
   def describe_number(num):
       result = valid_number(num)
       match result:
           case Success(value) if value % 2 == 0:
               return f"{value} is valid (even)"
           case Success(value) if value % 5 == 0:
               return f"{value} is valid (divisible by 5)"
           case Success(value):
               return f"{value} is valid"
           case Failure(error):
               return f"{num} is invalid: {error}"

   print(describe_number(42))  # 42 is valid (even)
   print(describe_number(35))  # 35 is valid (divisible by 5)
   print(describe_number(37))  # 37 is invalid: Number must be divisible by 5

Prompting for User Input
------------------------

Valid8r makes it easy to prompt for user input with validation:

.. code-block:: python

   from valid8r import prompt, parsers, validators
   from valid8r.core.maybe import Success, Failure

   # Ask for a positive number with retry
   number = prompt.ask(
       "Enter a positive number: ",
       parser=parsers.parse_int,
       validator=validators.minimum(0),
       retry=True
   )

   match number:
       case Success(value):
           print(f"You entered: {value}")
       case Failure(error):
           print(f"Error: {error}")

   # Ask for a value with a default
   age = prompt.ask(
       "Enter your age: ",
       parser=parsers.parse_int,
       validator=validators.between(0, 120),
       default=30,
       retry=True
   )

   match age:
       case Success(value):
           print(f"Your age is: {value}")
       case Failure(error):
           print(f"Error: {error}")

   # Processing multiple inputs with pattern matching
   def collect_user_info():
       name = prompt.ask("Enter your name: ", retry=True)
       age = prompt.ask(
           "Enter your age: ",
           parser=parsers.parse_int,
           validator=validators.between(0, 120),
           retry=True
       )

       # Pattern match on both results at once
       match (name, age):
           case (Success(name_val), Success(age_val)):
               return f"Hello, {name_val}! You are {age_val} years old."
           case (Failure(error), _):
               return f"Name error: {error}"
           case (_, Failure(error)):
               return f"Age error: {error}"

   print(collect_user_info())

Next Steps
----------

Now that you understand the basics, you can explore:

* The :doc:`Success and Failure types </user_guide/maybe_monad>` in more detail
* Available :doc:`parsers </user_guide/parsers>` for different data types
* Built-in :doc:`validators </user_guide/validators>` and how to create custom ones
* Prompting :doc:`prompting techniques </user_guide/prompting>`
* :doc:`Advanced usage patterns </user_guide/advanced_usage>`
* :doc:`Testing utilities </user_guide/testing>`

Or jump right to the :doc:`API reference </api/core>` for comprehensive documentation of all functions and classes.
