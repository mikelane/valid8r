Basic Examples
==============

This section provides practical examples of common validation scenarios using Valid8r. Each example demonstrates a specific validation use case with complete code samples.

Basic Parsing
-------------

Converting strings to various data types is a common operation that Valid8r simplifies with its parsing functions. All parsing functions return a Maybe object that can be easily examined with pattern matching:

.. code-block:: python

   from valid8r import parsers
   from valid8r.core.maybe import Success, Failure

   # Parse an integer
   result = parsers.parse_int("42")
   match result:
       case Success(value):
           print(f"Parsed integer: {value}")  # Parsed integer: 42
       case Failure(error):
           print(f"Error: {error}")

   # Parse a float
   result = parsers.parse_float("3.14159")
   match result:
       case Success(value):
           print(f"Parsed float: {value}")  # Parsed float: 3.14159
       case Failure(error):
           print(f"Error: {error}")

   # Parse a boolean
   result = parsers.parse_bool("yes")
   match result:
       case Success(value):
           print(f"Parsed boolean: {value}")  # Parsed boolean: True
       case Failure(error):
           print(f"Error: {error}")

   # Parse a date
   result = parsers.parse_date("2023-04-15")
   match result:
       case Success(value):
           print(f"Parsed date: {value}")  # Parsed date: 2023-04-15
       case Failure(error):
           print(f"Error: {error}")

   # Parse a complex number
   result = parsers.parse_complex("3+4j")
   match result:
       case Success(value):
           print(f"Parsed complex: {value}")  # Parsed complex: (3+4j)
       case Failure(error):
           print(f"Error: {error}")

Basic Validation
----------------

Validating values against specific criteria is easy with Valid8r validators:

.. code-block:: python

   from valid8r import validators
   from valid8r.core.maybe import Success, Failure

   # Validate a positive number
   result = validators.minimum(0)(42)
   match result:
       case Success(value):
           print(f"Valid positive number: {value}")  # Valid positive number: 42
       case Failure(error):
           print(f"Error: {error}")

   # Validate a number in range
   result = validators.between(1, 100)(42)
   match result:
       case Success(value):
           print(f"Valid number in range: {value}")  # Valid number in range: 42
       case Failure(error):
           print(f"Error: {error}")

   # Validate string length
   result = validators.length(3, 20)("hello")
   match result:
       case Success(value):
           print(f"Valid string: {value}")  # Valid string: hello
       case Failure(error):
           print(f"Error: {error}")

   # Validate with a custom predicate
   is_even = validators.predicate(lambda x: x % 2 == 0, "Number must be even")
   result = is_even(42)
   match result:
       case Success(value):
           print(f"Valid even number: {value}")  # Valid even number: 42
       case Failure(error):
           print(f"Error: {error}")

Combining Parsing and Validation
--------------------------------

Valid8r's strength lies in chaining parsing and validation for complete input processing:

.. code-block:: python

   from valid8r import parsers, validators
   from valid8r.core.maybe import Success, Failure

   # Parse and validate a positive integer
   input_str = "42"
   result = parsers.parse_int(input_str).bind(
       lambda x: validators.minimum(0)(x)
   )

   match result:
       case Success(value):
           print(f"Valid positive integer: {value}")  # Valid positive integer: 42
       case Failure(error):
           print(f"Error: {error}")

   # Parse and validate a date in the future
   from datetime import date

   today = date.today()
   is_future = validators.predicate(
       lambda d: d > today,
       "Date must be in the future"
   )

   input_str = "2030-01-01"
   result = parsers.parse_date(input_str).bind(is_future)

   match result:
       case Success(value):
           print(f"Valid future date: {value}")  # Valid future date: 2030-01-01
       case Failure(error):
           print(f"Error: {error}")

User Input with Validation
--------------------------

Valid8r makes it simple to prompt for input with validation:

.. code-block:: python

   from valid8r import prompt, parsers, validators
   from valid8r.core.maybe import Success, Failure

   # Ask for a name (non-empty string)
   name = prompt.ask(
       "Enter your name: ",
       validator=validators.length(1, 50),
       retry=True
   )

   match name:
       case Success(value):
           print(f"Name: {value}")
       case Failure(error):
           print(f"Error: {error}")

   # Ask for an age (positive integer)
   age = prompt.ask(
       "Enter your age: ",
       parser=parsers.parse_int,
       validator=validators.between(0, 120),
       retry=True
   )

   match age:
       case Success(value):
           print(f"Age: {value}")
       case Failure(error):
           print(f"Error: {error}")

   # Ask for a score with a default value
   score = prompt.ask(
       "Enter score (0-100): ",
       parser=parsers.parse_int,
       validator=validators.between(0, 100),
       default=50,
       retry=True
   )

   match score:
       case Success(value):
           print(f"Score: {value}")
       case Failure(error):
           print(f"Error: {error}")

   # Ask for a yes/no answer
   confirm = prompt.ask(
       "Proceed? (yes/no): ",
       parser=parsers.parse_bool,
       retry=True
   )

   match confirm:
       case Success(value) if value:
           print("Proceeding...")
       case Success(_):
           print("Operation cancelled")
       case Failure(error):
           print(f"Error: {error}")

Form Validation
---------------

Valid8r excels at validating form-like data structures:

.. code-block:: python

   from valid8r import Maybe, validators
   from valid8r.core.maybe import Success, Failure
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
               match result:
                   case Success(value):
                       results[field] = value
                   case Failure(error):
                       errors[field] = error
           else:
               errors[field] = f"Missing required field: {field}"

       if errors:
           return (False, errors)
       return (True, results)

   # Process validation results
   def process_form(form_data):
       is_valid, data = validate_form(form_data)

       if is_valid:
           print("Form is valid!")
           print(f"Username: {data['username']}")
           print(f"Email: {data['email']}")
           print(f"Age: {data['age']}")
           return True
       else:
           print("Form has errors:")
           for field, error in data.items():
               print(f"  - {field}: {error}")
           return False

   # Test with valid data
   valid_form = {
       "username": "john_doe",
       "email": "john@example.com",
       "age": 30
   }

   process_form(valid_form)

   # Test with invalid data
   invalid_form = {
       "username": "john_doe@",  # Contains invalid character
       "email": "not-an-email",
       "age": 15  # Below minimum
   }

   process_form(invalid_form)

Configuration Validation
------------------------

Validating configuration settings is another common use case for Valid8r:

.. code-block:: python

   from valid8r import validators
   from valid8r.core.maybe import Success, Failure

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
               match result:
                   case Success(value):
                       results[key] = value
                   case Failure(error):
                       errors[key] = error

       if errors:
           return (False, errors)
       return (True, results)

   # Test with pattern matching
   def apply_config(config):
       is_valid, data = validate_config(config)

       if is_valid:
           print("Configuration valid! Applying settings:")
           for key, value in data.items():
               print(f"  Setting {key} = {value}")
           return True
       else:
           print("Configuration invalid:")
           for key, error in data.items():
               print(f"  - {key}: {error}")
           return False

   # Test config
   config = {
       "port": 8080,
       "host": "localhost",
       "debug": True,
       "timeout": 30,
       "max_connections": 100
   }

   apply_config(config)

Data Structure Validation
-------------------------

Valid8r also handles validation of complex data structures:

.. code-block:: python

   from valid8r import Maybe, validators
   from valid8r.core.maybe import Success, Failure

   # Validate a list of items
   def validate_list(items, item_validator):
       results = []
       errors = []

       for i, item in enumerate(items):
           result = item_validator(item)
           match result:
               case Success(value):
                   results.append(value)
               case Failure(error):
                   errors.append(f"Item {i}: {error}")

       if errors:
           return Maybe.failure(errors)
       return Maybe.success(results)

   # Validate a dictionary
   def validate_dict(data, key_validators):
       results = {}
       errors = {}

       for key, validator in key_validators.items():
           if key in data:
               result = validator(data[key])
               match result:
                   case Success(value):
                       results[key] = value
                   case Failure(error):
                       errors[key] = error
           else:
               errors[key] = f"Missing required key: {key}"

       if errors:
           return Maybe.failure(errors)
       return Maybe.success(results)

   # Example usage with pattern matching
   def process_numbers(numbers):
       is_positive = validators.minimum(0)
       result = validate_list(numbers, is_positive)

       match result:
           case Success(valid_numbers):
               total = sum(valid_numbers)
               average = total / len(valid_numbers) if valid_numbers else 0
               print(f"All numbers are valid!")
               print(f"Total: {total}")
               print(f"Average: {average:.2f}")
           case Failure(errors):
               print("Validation failed:")
               for error in errors:
                   print(f"  {error}")

   # Test with valid data
   numbers = [1, 2, 3, 4, 5]
   process_numbers(numbers)

   # Test with invalid data
   numbers_with_errors = [1, -2, 3, -4, 5]
   process_numbers(numbers_with_errors)

   # Validate user data with pattern matching
   def process_user(user):
       user_validators = {
           "name": validators.length(1, 100),
           "age": validators.between(0, 120),
           "email": validators.predicate(
               lambda s: "@" in s,
               "Invalid email format"
           )
       }

       result = validate_dict(user, user_validators)
       match result:
           case Success(valid_user):
               print(f"User data is valid for {valid_user['name']}!")
               return valid_user
           case Failure(errors):
               print("User data has errors:")
               for key, error in errors.items():
                   print(f"  - {key}: {error}")
               return None

   # Test with user data
   user = {
       "name": "John Doe",
       "age": 30,
       "email": "john@example.com"
   }

   process_user(user)

IP Address parsing
------------------

.. code-block:: python

   from valid8r.core.maybe import Success, Failure
   from valid8r import parsers

   # IPv4
   match parsers.parse_ipv4("8.8.8.8"):
       case Success(addr):
           print(addr)
       case Failure(err):
           print("Error:", err)

   # IPv6
   match parsers.parse_ipv6("2001:db8::1"):
       case Success(addr):
           print(addr)
       case Failure(err):
           print("Error:", err)

   # CIDR (non-strict)
   match parsers.parse_cidr("10.0.0.1/24", strict=False):
       case Success(net):
           print(net)  # 10.0.0.0/24
       case Failure(err):
           print("Error:", err)

These examples provide a solid foundation for understanding how to use Valid8r effectively in your applications. In the next sections, we'll explore more advanced usage patterns.
