Advanced Usage
==============

This section covers advanced usage patterns and techniques for getting the most out of Valid8r. We'll explore complex validation scenarios, custom validators, integration patterns, and more.

Complex Validation Chains
-------------------------

One of Valid8r's strengths is the ability to create complex validation chains:

.. code-block:: python

   from valid8r import parsers, validators, Maybe

   # Create complex validation logic
   def validate_password(password):
       # Password must:
       # 1. Be between 8 and 64 characters
       # 2. Contain at least one uppercase letter
       # 3. Contain at least one lowercase letter
       # 4. Contain at least one digit
       # 5. Contain at least one special character

       length_check = validators.length(8, 64)

       has_uppercase = validators.predicate(
           lambda p: any(c.isupper() for c in p),
           "Password must contain at least one uppercase letter"
       )

       has_lowercase = validators.predicate(
           lambda p: any(c.islower() for c in p),
           "Password must contain at least one lowercase letter"
       )

       has_digit = validators.predicate(
           lambda p: any(c.isdigit() for c in p),
           "Password must contain at least one digit"
       )

       has_special = validators.predicate(
           lambda p: any(not c.isalnum() for c in p),
           "Password must contain at least one special character"
       )

       # Combine all validators
       return (
           Maybe.just(password)
           .bind(lambda p: length_check(p))
           .bind(lambda p: has_uppercase(p))
           .bind(lambda p: has_lowercase(p))
           .bind(lambda p: has_digit(p))
           .bind(lambda p: has_special(p))
       )

   # Test the password validator
   result = validate_password("Abc123!")  # Valid
   result = validate_password("abc123")   # Missing uppercase and special char

The same validation chain can be written more concisely using validator composition:

.. code-block:: python

   from valid8r import validators

   # Create the same validator using operator composition
   password_validator = (
       validators.length(8, 64) &
       validators.predicate(
           lambda p: any(c.isupper() for c in p),
           "Password must contain at least one uppercase letter"
       ) &
       validators.predicate(
           lambda p: any(c.islower() for c in p),
           "Password must contain at least one lowercase letter"
       ) &
       validators.predicate(
           lambda p: any(c.isdigit() for c in p),
           "Password must contain at least one digit"
       ) &
       validators.predicate(
           lambda p: any(not c.isalnum() for c in p),
           "Password must contain at least one special character"
       )
   )

   result = password_validator("Abc123!")  # Valid
   result = password_validator("abc123")   # Invalid

Custom Validator Factories
--------------------------

You can create your own validator factory functions to extend Valid8r's capabilities:

.. code-block:: python

   from valid8r import Maybe, validators
   from datetime import date

   # Create a validator for dates
   def date_after(min_date, error_message=None):
       """Create a validator that checks if a date is after the specified date."""
       def validator(value):
           if value > min_date:
               return Maybe.just(value)
           return Maybe.nothing(
               error_message or f"Date must be after {min_date.isoformat()}"
           )
       return validators.Validator(validator)

   def date_before(max_date, error_message=None):
       """Create a validator that checks if a date is before the specified date."""
       def validator(value):
           if value < max_date:
               return Maybe.just(value)
           return Maybe.nothing(
               error_message or f"Date must be before {max_date.isoformat()}"
           )
       return validators.Validator(validator)

   # Use the custom validators
   today = date.today()
   is_in_future = date_after(today, "Date must be in the future")
   is_this_century = date_before(date(2100, 1, 1), "Date must be in this century")

   # Combine them
   valid_date = is_in_future & is_this_century

   # Test
   future_date = date(2030, 1, 1)
   result = valid_date(future_date)  # Valid

   past_date = date(2020, 1, 1)
   result = valid_date(past_date)    # Invalid - not in future

   far_future = date(2200, 1, 1)
   result = valid_date(far_future)   # Invalid - not in this century

Creating a Domain-Specific Validation Library
---------------------------------------------

You can build domain-specific validation libraries on top of Valid8r:

.. code-block:: python

   from valid8r import Maybe, parsers, validators
   import re

   # User validation library
   class UserValidators:
       @staticmethod
       def username(min_length=3, max_length=20):
           """Validate a username."""
           pattern = r"^[a-zA-Z0-9_]+$"

           length_check = validators.length(min_length, max_length)
           format_check = validators.predicate(
               lambda s: bool(re.match(pattern, s)),
               "Username must contain only letters, numbers, and underscores"
           )

           return length_check & format_check

       @staticmethod
       def email():
           """Validate an email address."""
           pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

           return validators.predicate(
               lambda s: bool(re.match(pattern, s)),
               "Invalid email format"
           )

       @staticmethod
       def phone(country_code="US"):
           """Validate a phone number for a specific country."""
           if country_code == "US":
               pattern = r"^\d{3}-\d{3}-\d{4}$"
               message = "US phone number must be in format: 123-456-7890"
           else:
               # Default pattern for international numbers
               pattern = r"^\+\d{1,3}-\d{3,14}$"
               message = "International phone number must be in format: +XX-XXXXXXXXXX"

           return validators.predicate(
               lambda s: bool(re.match(pattern, s)),
               message
           )

   # Usage
   username_validator = UserValidators.username()
   email_validator = UserValidators.email()
   phone_validator = UserValidators.phone()

   # Validate a user
   username_result = username_validator("john_doe123")
   email_result = email_validator("john@example.com")
   phone_result = phone_validator("123-456-7890")

Working with External Data
--------------------------

Valid8r can also validate data from external sources like JSON or CSV files:

.. code-block:: python

   import json
   from valid8r import Maybe, validators

   # Define validators for user data
   user_validators = {
       "name": validators.length(1, 100),
       "age": validators.between(0, 120),
       "email": validators.predicate(
           lambda s: "@" in s and "." in s.split("@")[1],
           "Invalid email format"
       )
   }

   def validate_user(user_data):
       """Validate a user data dictionary."""
       results = {}
       errors = {}

       for field, validator in user_validators.items():
           if field in user_data:
               result = validator(user_data[field])
               if result.is_just():
                   results[field] = result.value()
               else:
                   errors[field] = result.error()
           else:
               errors[field] = f"Missing required field: {field}"

       if errors:
           return Maybe.nothing(errors)
       return Maybe.just(results)

   # Load data from a JSON file
   def load_and_validate_users(file_path):
       with open(file_path, 'r') as f:
           data = json.load(f)

       valid_users = []
       invalid_users = []

       for user in data:
           result = validate_user(user)
           if result.is_just():
               valid_users.append(result.value())
           else:
               invalid_users.append((user, result.error()))

       return valid_users, invalid_users

Integration with Web Frameworks
-------------------------------

Valid8r can be integrated with web frameworks for form validation:

.. code-block:: python

   from flask import Flask, request, jsonify
   from valid8r import parsers, validators

   app = Flask(__name__)

   # Define validators
   username_validator = validators.length(3, 20) & validators.predicate(
       lambda s: s.isalnum(),
       "Username must be alphanumeric"
   )

   password_validator = validators.length(8, 64) & validators.predicate(
       lambda p: any(c.isupper() for c in p) and any(c.isdigit() for c in p),
       "Password must contain at least one uppercase letter and one digit"
   )

   @app.route('/api/register', methods=['POST'])
   def register():
       data = request.json

       # Validate username
       username_result = username_validator(data.get('username', ''))
       if username_result.is_nothing():
           return jsonify({"error": "username", "message": username_result.error()}), 400

       # Validate password
       password_result = password_validator(data.get('password', ''))
       if password_result.is_nothing():
           return jsonify({"error": "password", "message": password_result.error()}), 400

       # Both valid, proceed with registration
       # ...

       return jsonify({"message": "Registration successful"}), 201

Advanced Monadic Patterns
-------------------------

Valid8r's Maybe monad enables some advanced functional programming patterns:

.. code-block:: python

   from valid8r import Maybe, parsers
   from typing import List

   # Sequence operation - convert a list of Maybes to a Maybe of list
   def sequence(maybes: List[Maybe]):
       """Convert a list of Maybe values to a Maybe containing a list of values.

       If any Maybe is Nothing, the result is Nothing with the first error.
       """
       values = []
       for m in maybes:
           if m.is_nothing():
               return m  # Return the first Nothing
           values.append(m.value())
       return Maybe.just(values)

   # Parse multiple values
   results = [
       parsers.parse_int("42"),
       parsers.parse_float("3.14"),
       parsers.parse_bool("true")
   ]

   # Sequence the results
   seq_result = sequence(results)
   if seq_result.is_just():
       print(f"All values parsed successfully: {seq_result.value()}")
   else:
       print(f"Error parsing values: {seq_result.error()}")

   # Map operation - apply a function to a list of values inside a Maybe
   def map_maybe(maybe, func):
       """Apply a function to a value inside a Maybe."""
       if maybe.is_just():
           return Maybe.just(func(maybe.value()))
       return maybe

   # Double a number inside a Maybe
   doubled = map_maybe(parsers.parse_int("42"), lambda x: x * 2)
   print(doubled.value())  # 84

Asynchronous Validation
-----------------------

For asynchronous validation in asyncio-based applications:

.. code-block:: python

   import asyncio
   from valid8r import Maybe, validators

   async def async_validator(value):
       """Simulate an asynchronous validation (e.g., checking a database)."""
       await asyncio.sleep(1)  # Simulate network delay
       if value.startswith("valid_"):
           return Maybe.just(value)
       return Maybe.nothing("Value must start with 'valid_'")

   async def validate_user_exists(username):
       """Check if a username exists in the database."""
       # Simulate database check
       await asyncio.sleep(0.5)
       existing_users = ["alice", "bob", "charlie"]
       if username in existing_users:
           return Maybe.just(username)
       return Maybe.nothing(f"User '{username}' does not exist")

   async def main():
       # Validate a string asynchronously
       result = await async_validator("valid_user")
       print(result.is_just())  # True

       result = await async_validator("invalid_user")
       print(result.is_nothing())  # True

       # Check if user exists
       result = await validate_user_exists("alice")
       print(result.is_just())  # True

       result = await validate_user_exists("dave")
       print(result.is_nothing())  # True

   # Run with asyncio
   asyncio.run(main())

Testing Your Validators
-----------------------

Writing tests for your validators is crucial:

.. code-block:: python

   import unittest
   from valid8r import validators

   class TestValidators(unittest.TestCase):
       def test_minimum_validator(self):
           # Create validator
           is_positive = validators.minimum(0)

           # Test valid case
           result = is_positive(10)
           self.assertTrue(result.is_just())
           self.assertEqual(result.value(), 10)

           # Test invalid case
           result = is_positive(-5)
           self.assertTrue(result.is_nothing())
           self.assertIn("must be at least 0", result.error())

       def test_combined_validators(self):
           # Create combined validator
           is_valid_age = validators.minimum(18) & validators.maximum(65)

           # Test valid case
           result = is_valid_age(30)
           self.assertTrue(result.is_just())

           # Test invalid cases
           result = is_valid_age(15)
           self.assertTrue(result.is_nothing())
           self.assertIn("must be at least 18", result.error())

           result = is_valid_age(70)
           self.assertTrue(result.is_nothing())
           self.assertIn("must be at most 65", result.error())

Performance Considerations
--------------------------

When dealing with large datasets or performance-critical code:

1. **Avoid unnecessary chaining**: Each bind operation creates overhead
2. **Reuse validators**: Create validators once and reuse them
3. **Batch validation**: Validate multiple items at once for better efficiency
4. **Early termination**: Use short-circuit operators where possible

.. code-block:: python

   from valid8r import validators
   import time

   # Create validators once
   is_positive = validators.minimum(0)
   is_even = validators.predicate(lambda x: x % 2 == 0, "Must be even")
   valid_number = is_positive & is_even

   # Inefficient approach
   def validate_inefficient(numbers):
       start = time.time()
       results = []

       for num in numbers:
           # Creates new validators for each number
           temp_is_positive = validators.minimum(0)
           temp_is_even = validators.predicate(lambda x: x % 2 == 0, "Must be even")
           temp_valid = temp_is_positive & temp_is_even

           results.append(temp_valid(num))

       end = time.time()
       print(f"Inefficient: {end - start:.6f} seconds")
       return results

   # Efficient approach
   def validate_efficient(numbers):
       start = time.time()
       results = []

       for num in numbers:
           # Reuses the validators
           results.append(valid_number(num))

       end = time.time()
       print(f"Efficient: {end - start:.6f} seconds")
       return results

   # Test with a large dataset
   test_data = list(range(10000))
   validate_inefficient(test_data)
   validate_efficient(test_data)

In the next sections, we'll explore concrete examples and the complete API reference.