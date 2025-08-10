Welcome to Valid8r's documentation!
===================================

.. image:: https://img.shields.io/badge/Python-3.11%2B-blue
   :target: https://www.python.org/downloads/
   :alt: Python 3.11+

.. image:: https://img.shields.io/github/license/mikelane/valid8r
   :target: https://github.com/mikelane/valid8r/blob/main/LICENSE
   :alt: License: MIT

**Valid8r** is a clean, flexible input validation library for Python applications. It provides a functional programming approach to validation with a robust error handling system based on Success and Failure types that work seamlessly with Python's pattern matching.

Key Features
------------

* **Clean Type Parsing**: Parse strings to various Python types with robust error handling
* **Pattern Matching Support**: Use Python 3.11+ pattern matching for elegant error handling
* **Flexible Validation**: Chain validators and create custom validation rules
* **Functional Approach**: Use Success and Failure types instead of exceptions for error handling
* **Input Prompting**: Prompt users for input with built-in validation

Quick Start
-----------

.. code-block:: python

   from valid8r import parsers, validators, prompt
   from valid8r.core.maybe import Success, Failure

   # Parse a string to an integer and validate it
   result = parsers.parse_int("42").bind(
       lambda x: validators.minimum(0)(x)
   )

   match result:
       case Success(value):
           print(f"Valid number: {value}")  # Valid number: 42
       case Failure(error):
           print(f"Error: {error}")

   # Ask for user input with validation
   age = prompt.ask(
       "Enter your age: ",
       parser=parsers.parse_int,
       validator=validators.between(0, 120),
       retry=True
   )

   match age:
       case Success(value):
           print(f"Your age is {value}")
       case Failure(error):
           print(f"Error: {error}")

Installation
------------

.. code-block:: bash

   pip install valid8r

Alternatively, if you use Poetry:

.. code-block:: bash

   poetry add valid8r

Validation with Pattern Matching
--------------------------------

Valid8r is designed to work seamlessly with Python 3.11+ pattern matching, enabling elegant and readable validation code:

.. code-block:: python

   from valid8r import parsers, validators
   from valid8r.core.maybe import Success, Failure

   # Combine parsing and validation
   def validate_age(age_str):
       result = parsers.parse_int(age_str).bind(
           lambda x: validators.between(0, 120)(x)
       )

       # Use pattern matching to handle the result
       match result:
           case Success(value) if value >= 18:
               return f"Valid adult age: {value}"
           case Success(value):
               return f"Valid minor age: {value}"
           case Failure(error) if "valid integer" in error:
               return f"Parsing error: {error}"
           case Failure(error):
               return f"Validation error: {error}"

   # Example usage
   print(validate_age("42"))    # Valid adult age: 42
   print(validate_age("10"))    # Valid minor age: 10
   print(validate_age("abc"))   # Parsing error: Input must be a valid integer
   print(validate_age("-5"))    # Validation error: Value must be between 0 and 120

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   user_guide/getting_started
   user_guide/maybe_monad
   user_guide/parsers
   user_guide/validators
   user_guide/prompting
   user_guide/advanced_usage

.. toctree::
   :maxdepth: 2
   :caption: Examples

   examples/basic_examples
   examples/chaining_validators
   examples/custom_validators
   examples/interactive_prompts

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/core
   api/prompt

.. toctree::
   :maxdepth: 1
   :caption: Development

   development/contributing
   development/testing
   development/changelog

Why Valid8r?
------------

Valid8r offers several advantages over traditional validation approaches:

1. **No exceptions for control flow**: Instead of raising and catching exceptions, Valid8r uses Success and Failure types to represent validation results.

2. **Elegant pattern matching**: With Python 3.11+, you can use pattern matching to handle validation results in a clear and concise way.

3. **Composable validators**: Build complex validation rules by combining simple validators with logical operators.

4. **Clean API**: The API is designed to be intuitive and easy to use, with a consistent approach to validation throughout.

5. **Type safety**: Valid8r is designed with type safety in mind, with comprehensive type annotations for better IDE support.

Example: Building a Complete Form Validator
-------------------------------------------

Here's an example of using Valid8r to build a form validator with pattern matching:

.. code-block:: python

   from valid8r import validators, parsers
   from valid8r.core.maybe import Success, Failure
   import re

   # Define form field validators
   name_validator = validators.length(1, 100)

   email_validator = validators.predicate(
       lambda s: bool(re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", s)),
       "Invalid email format"
   )

   age_validator = validators.between(18, 120)

   # Validate a complete form
   def validate_form(form_data):
       # Validate each field
       name_result = name_validator(form_data.get('name', ''))
       email_result = email_validator(form_data.get('email', ''))

       # Parse and validate age
       age_str = form_data.get('age', '')
       age_result = parsers.parse_int(age_str).bind(age_validator)

       # Use pattern matching to process all results at once
       match (name_result, email_result, age_result):
           case (Success(name), Success(email), Success(age)):
               return {
                   "status": "valid",
                   "data": {
                       "name": name,
                       "email": email,
                       "age": age
                   }
               }
           case (Failure(error), _, _):
               return {
                   "status": "invalid",
                   "field": "name",
                   "error": error
               }
           case (_, Failure(error), _):
               return {
                   "status": "invalid",
                   "field": "email",
                   "error": error
               }
           case (_, _, Failure(error)):
               return {
                   "status": "invalid",
                   "field": "age",
                   "error": error
               }

   # Test with valid data
   valid_form = {
       "name": "John Doe",
       "email": "john@example.com",
       "age": "30"
   }

   print(validate_form(valid_form))

   # Test with invalid data
   invalid_form = {
       "name": "",
       "email": "not-an-email",
       "age": "seventeen"
   }

   print(validate_form(invalid_form))

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`