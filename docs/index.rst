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

**Basic installation** (includes Pydantic integration):

.. code-block:: bash

   pip install valid8r

**With optional framework integrations**:

.. code-block:: bash

   # Click integration for CLI applications
   pip install 'valid8r[click]'

**Using uv**:

.. code-block:: bash

   uv add valid8r
   # or with Click
   uv add "valid8r[click]"

**Using Poetry**:

.. code-block:: bash

   poetry add valid8r
   # or with Click
   poetry add "valid8r[click]"

.. note::
   **Pydantic integration** is included by default. The **Click integration** is optional
   and only needed if you're building CLI applications with Click.

   See :doc:`user_guide/getting_started` for detailed installation instructions.

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

   examples/basic_example
   examples/chaining_validators
   examples/custom_validators
   examples/interactive_prompts
   examples/fastapi_integration
   examples/environment_variables

.. toctree::
   :maxdepth: 2
   :caption: Security

   security/overview
   security/production-deployment
   security/secure-parser-development
   security/policy

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

Structured Result Types
-----------------------

Some parsers return rich dataclasses containing parsed components for easy access. This is particularly useful for network-related data like URLs, emails, and phone numbers.

URL Parsing with UrlParts
^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``parse_url`` function returns a ``UrlParts`` object with structured access to URL components:

.. code-block:: python

   from valid8r import parsers
   from valid8r.core.maybe import Success

   result = parsers.parse_url('https://user:pass@api.example.com:8080/v1/users?active=true#section')

   match result:
       case Success(url):
           print(f"Scheme: {url.scheme}")       # https
           print(f"Host: {url.host}")           # api.example.com
           print(f"Port: {url.port}")           # 8080
           print(f"Path: {url.path}")           # /v1/users
           print(f"Query: {url.query}")         # active=true
           print(f"Fragment: {url.fragment}")   # section

           # Access credentials
           print(f"Username: {url.username}")   # user
           print(f"Password: {url.password}")   # pass

Email Parsing with EmailAddress
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``parse_email`` function returns an ``EmailAddress`` object with normalized domain:

.. code-block:: python

   from valid8r import parsers
   from valid8r.core.maybe import Success

   result = parsers.parse_email('User.Name+tag@Example.COM')

   match result:
       case Success(email):
           print(f"Local: {email.local}")     # User.Name+tag (case preserved)
           print(f"Domain: {email.domain}")   # example.com (normalized lowercase)

Phone Number Parsing with PhoneNumber
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``parse_phone`` function returns a ``PhoneNumber`` object with structured NANP components:

.. code-block:: python

   from valid8r import parsers
   from valid8r.core.maybe import Success

   result = parsers.parse_phone('+1 (555) 123-4567')

   match result:
       case Success(phone):
           print(f"Country: {phone.country_code}")  # 1
           print(f"Area: {phone.area_code}")        # 555
           print(f"Exchange: {phone.exchange}")     # 123
           print(f"Subscriber: {phone.subscriber}") # 4567

           # Format for display
           print(f"E.164: {phone.e164}")           # +15551234567
           print(f"National: {phone.national}")    # (555) 123-4567

Testing Utilities
-----------------

Valid8r provides comprehensive testing utilities to help you test validation logic in your applications.

Assert Helpers
^^^^^^^^^^^^^^

Use ``assert_maybe_success`` and ``assert_maybe_failure`` to verify Maybe results in tests:

.. code-block:: python

   from valid8r import parsers, validators
   from valid8r.testing import assert_maybe_success, assert_maybe_failure

   def test_valid_age():
       result = parsers.parse_int("42").bind(validators.minimum(0))
       assert assert_maybe_success(result, 42)

   def test_invalid_age():
       result = parsers.parse_int("-5").bind(validators.minimum(0))
       assert assert_maybe_failure(result, "at least 0")

Mock Input Context
^^^^^^^^^^^^^^^^^^

Use ``MockInputContext`` to test interactive prompts without actual user input:

.. code-block:: python

   from valid8r import parsers, validators, prompt
   from valid8r.testing import MockInputContext

   def test_interactive_age_prompt():
       with MockInputContext(["25"]):
           age = prompt.ask(
               "Enter your age: ",
               parser=parsers.parse_int,
               validator=validators.minimum(0)
           )
           assert age == 25

   def test_prompt_with_retry():
       # First input invalid, second valid
       with MockInputContext(["invalid", "30"]):
           age = prompt.ask(
               "Age: ",
               parser=parsers.parse_int,
               retries=1  # Allow one retry
           )
           assert age == 30

Testing Complex Validation
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Combine testing utilities for comprehensive validation tests:

.. code-block:: python

   from valid8r import parsers, validators, Maybe
   from valid8r.testing import assert_maybe_success, assert_maybe_failure

   def validate_user_age(age_str: str) -> Maybe[int]:
       """Validate user age is between 0 and 120."""
       return parsers.parse_int(age_str).bind(
           validators.minimum(0) & validators.maximum(120)
       )

   def test_user_age_validation():
       # Test valid ages
       assert assert_maybe_success(validate_user_age("25"), 25)
       assert assert_maybe_success(validate_user_age("0"), 0)
       assert assert_maybe_success(validate_user_age("120"), 120)

       # Test invalid ages
       assert assert_maybe_failure(validate_user_age("-1"), "at least 0")
       assert assert_maybe_failure(validate_user_age("121"), "at most 120")
       assert assert_maybe_failure(validate_user_age("abc"), "valid integer")

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
