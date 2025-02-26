Basic Examples
==============

This section provides practical examples of common validation scenarios using Valid8r.

Basic Parsing
-------------

Converting strings to various data types:

.. code-block:: python

   from valid8r import parsers

   # Parse an integer
   result = parsers.parse_int("42")
   if result.is_just():
       value = result.value()  # 42

   # Parse a float
   result = parsers.parse_float("3.14159")
   if result.is_just():
       value = result.value()  # 3.14159

   # Parse a boolean
   result = parsers.parse_bool("yes")
   if result.is_just():
       value = result.value()  # True

   # Parse a date
   result = parsers.parse_date("2023-04-15")
   if result.is_just():
       value = result.value()  # datetime.date(2023, 4, 15)

   # Parse a complex number
   result = parsers.parse_complex("3+4j")
   if result.is_just():
       value = result.value()  # (3+4j)

Basic Validation
----------------

Validating values against various criteria:

.. code-block:: python

   from valid8r import validators

   # Validate a positive number
   result = validators.minimum(0)(42)
   if result.is_just():
       value = result.value()  # 42

   # Validate a number in range
   result = validators.between(1, 100)(42)
   if result.is_just():
       value = result.value()  # 42

   # Validate string length
   result = validators.length(3, 20)("hello")
   if result.is_just():
       value = result.value()  # "hello"

   # Validate with a custom predicate
   is_even = validators.predicate(lambda x: x % 2 == 0, "Number must be even")
   result = is_even(42)
   if result.is_just():
       value = result.value()  # 42

Combining Parsing and Validation
--------------------------------

Chaining parsing and validation for complete input processing:

.. code-block:: python

   from valid8r import parsers, validators

   # Parse and validate a positive integer
   input_str = "42"
   result = parsers.parse_int(input_str).bind(
       lambda x: validators.minimum(0)(x)
   )

   if result.is_just():
       print(f"Valid positive integer: {result.value()}")
   else:
       print(f"Error: {result.error()}")

   # Parse and validate a date in the future
   from datetime import date

   today = date.today()
   is_future = validators.predicate(
       lambda d: d > today,
       "Date must be in the future"
   )

   input_str = "2030-01-01"
   result = parsers.parse_date(input_str).bind(is_future)

   if result.is_just():
       print(f"Valid future date: {result.value()}")
   else:
       print(f"Error: {result.error()}")

User Input with Validation
--------------------------

Prompting for input with validation:

.. code-block:: python

   from valid8r import prompt, parsers, validators

   # Ask for a name (non-empty string)
   name = prompt.ask(
       "Enter your name: ",
       validator=validators.length(1, 50),
       retry=True
   )

   # Ask for an age (positive integer)
   age = prompt.ask(
       "Enter your age: ",
       parser=parsers.parse_int,
       validator=validators.between(0, 120),
       retry=True
   )

   # Ask for a score with a default value
   score = prompt.ask(
       "Enter score (0-100): ",
       parser=parsers.parse_int,
       validator=validators.between(0, 100),
       default=50,
       retry=True
   )

   # Ask for a yes/no answer
   confirm = prompt.ask(
       "Proceed? (yes/no): ",
       parser=parsers.parse_bool,
       retry=True
   )

   # Use the validated inputs
   if name.is_just() and age.is_just() and score.is_just() and confirm.is_just():
       print(f"Name: {name.value()}")
       print(f"Age: {age.value()}")
       print(f"Score: {score.value()}")

       if confirm.value():
           print("Proceeding...")
       else:
           print("Operation cancelled")

Form Validation
---------------

Validating form-like data:

.. code-block:: python

   from valid8r import Maybe, validators
   import re

   # Define validators
   validators_map = {
       "username": validators.length(3, 20) & validators.predicate(
           lambda s: s.isalnum(),
           "Username must be alphanumeric"
       ),
       "email": validators.predicate(
           lambda s: bool(re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", s)),
           "Invalid email format"
       ),
       "age": validators.between(18, 120),
   }

   # Validate form data
   def validate_form(form_data):
       results = {}
       errors = {}

       for field, validator in validators_map.items():
           if field in form_data:
               result = validator(form_data[field])
               if result.is_just():
                   results[field] = result.value()
               else:
                   errors[field] = result.error()
           else:
               errors[field] = f"Missing required field: {field}"

       if errors:
           return (False, errors)
       return (True, results)

   # Test with valid data
   valid_form = {
       "username": "john_doe",
       "email": "john@example.com",
       "age": 30
   }

   is_valid, data = validate_form(valid_form)
   print(f"Is valid: {is_valid}")
   print(f"Data or errors: {data}")

   # Test with invalid data
   invalid_form = {
       "username": "john_doe@",  # Contains invalid character
       "email": "not-an-email",
       "age": 15  # Below minimum
   }

   is_valid, data = validate_form(invalid_form)
   print(f"Is valid: {is_valid}")
   print(f"Data or errors: {data}")

Configuration Validation
------------------------

Validating configuration settings:

.. code-block:: python

   from valid8r import validators

   # Define validators for configuration
   config_validators = {
       "port": validators.between(1024, 65535),
       "host": validators.predicate(
           lambda s: s == "localhost" or all(part.isdigit() and 0 <= int(part) <= 255
                                          for part in s.split(".")),
           "Host must be 'localhost' or a valid IP address"
       ),
       "debug": validators.predicate(
           lambda b: isinstance(b, bool),
           "Debug must be a boolean"
       ),
       "timeout": validators.minimum(0),
       "max_connections": validators.between(1, 1000),
   }

   # Validate config
   def validate_config(config):
       results = {}
       errors = {}

       for key, validator in config_validators.items():
           if key in config:
               result = validator(config[key])
               if result.is_just():
                   results[key] = result.value()
               else:
                   errors[key] = result.error()
           # Allow missing fields in config

       if errors:
           return (False, errors)
       return (True, results)

   # Test config
   config = {
       "port": 8080,
       "host": "localhost",
       "debug": True,
       "timeout": 30,
       "max_connections": 100
   }

   is_valid, data = validate_config(config)
   print(f"Config valid: {is_valid}")
   print(f"Data or errors: {data}")

Data Structure Validation
-------------------------

Validating nested data structures:

.. code-block:: python

   from valid8r import Maybe, validators

   # Validate a list of items
   def validate_list(items, item_validator):
       results = []
       errors = []

       for i, item in enumerate(items):
           result = item_validator(item)
           if result.is_just():
               results.append(result.value())
           else:
               errors.append(f"Item {i}: {result.error()}")

       if errors:
           return Maybe.nothing(errors)
       return Maybe.just(results)

   # Validate a dictionary
   def validate_dict(data, key_validators):
       results = {}
       errors = {}

       for key, validator in key_validators.items():
           if key in data:
               result = validator(data[key])
               if result.is_just():
                   results[key] = result.value()
               else:
                   errors[key] = result.error()
           else:
               errors[key] = f"Missing required key: {key}"

       if errors:
           return Maybe.nothing(errors)
       return Maybe.just(results)

   # Example usage
   numbers = [1, 2, 3, 4, 5]
   is_positive = validators.minimum(0)

   result = validate_list(numbers, is_positive)
   if result.is_just():
       print(f"All numbers are valid: {result.value()}")
   else:
       print(f"Errors: {result.error()}")

   # Validate user data
   user = {
       "name": "John Doe",
       "age": 30,
       "email": "john@example.com"
   }

   user_validators = {
       "name": validators.length(1, 100),
       "age": validators.between(0, 120),
       "email": validators.predicate(
           lambda s: "@" in s,
           "Invalid email format"
       )
   }

   result = validate_dict(user, user_validators)
   if result.is_just():
       print(f"User data is valid: {result.value()}")
   else:
       print(f"Errors: {result.error()}")

These examples provide a starting point for common validation scenarios. In the next sections, we'll explore more advanced examples and patterns.