Advanced Usage
==============

This section covers advanced usage patterns and techniques for getting the most out of Valid8r. We'll explore complex validation scenarios, custom validators, integration patterns, and more.

Complex Validation Chains
-------------------------

One of Valid8r's strengths is the ability to create complex validation chains:

.. code-block:: python

   from valid8r import parsers, validators, Maybe
   from valid8r.core.maybe import Success, Failure

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
           Maybe.success(password)
           .bind(lambda p: length_check(p))
           .bind(lambda p: has_uppercase(p))
           .bind(lambda p: has_lowercase(p))
           .bind(lambda p: has_digit(p))
           .bind(lambda p: has_special(p))
       )

   # Test the password validator
   result = validate_password("Abc123!")  # Valid
   match result:
       case Success(value):
           print(f"Valid password: {value}")  # Valid password: Abc123!
       case Failure(error):
           print(f"Invalid password: {error}")

   result = validate_password("abc123")   # Missing uppercase and special char
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(f"Invalid password: {error}")  # Invalid password: Password must contain at least one uppercase letter

The same validation chain can be written more concisely using validator composition:

.. code-block:: python

   from valid8r import validators
   from valid8r.core.maybe import Success, Failure

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
   match result:
       case Success(value):
           print(f"Valid password: {value}")  # Valid password: Abc123!
       case Failure(_):
           print("This won't happen")

   result = password_validator("abc123")   # Invalid
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(f"Invalid password: {error}")  # Invalid password: Password must contain at least one uppercase letter

Custom Validator Factories
--------------------------

You can create your own validator factory functions to extend Valid8r's capabilities:

.. code-block:: python

   from valid8r import Maybe, validators
   from valid8r.core.maybe import Success, Failure
   from datetime import date

   # Create a validator for dates
   def date_after(min_date, error_message=None):
       """Create a validator that checks if a date is after the specified date."""
       def validator(value):
           if value > min_date:
               return Maybe.success(value)
           return Maybe.failure(
               error_message or f"Date must be after {min_date.isoformat()}"
           )
       return validators.Validator(validator)

   def date_before(max_date, error_message=None):
       """Create a validator that checks if a date is before the specified date."""
       def validator(value):
           if value < max_date:
               return Maybe.success(value)
           return Maybe.failure(
               error_message or f"Date must be before {max_date.isoformat()}"
           )
       return validators.Validator(validator)

   # Use the custom validators
   today = date.today()
   is_in_future = date_after(today, "Date must be in the future")
   is_this_century = date_before(date(2100, 1, 1), "Date must be in this century")

   # Combine them
   valid_date = is_in_future & is_this_century

   # Test with pattern matching
   future_date = date(2030, 1, 1)
   result = valid_date(future_date)
   match result:
       case Success(value):
           print(f"Valid date: {value.isoformat()}")  # Valid date: 2030-01-01
       case Failure(_):
           print("This won't happen")

   past_date = date(2020, 1, 1)
   result = valid_date(past_date)
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(f"Invalid date: {error}")  # Invalid date: Date must be in the future

   far_future = date(2200, 1, 1)
   result = valid_date(far_future)
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(f"Invalid date: {error}")  # Invalid date: Date must be in this century

Creating a Domain-Specific Validation Library
---------------------------------------------

You can build domain-specific validation libraries on top of Valid8r:

.. code-block:: python

   from valid8r import Maybe, parsers, validators
   from valid8r.core.maybe import Success, Failure
   import re

   # User validation library
   class UserValidators:
       @staticmethod
       def username(min_length=3, max_length=20):
           """Validate a username."""
           length_check = validators.length(min_length, max_length)
           format_check = validators.matches_regex(
               r"^[a-zA-Z0-9_]+$",
               error_message="Username must contain only letters, numbers, and underscores"
           )

           return length_check & format_check

       @staticmethod
       def email():
           """Validate an email address."""
           return validators.matches_regex(
               r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
               error_message="Invalid email format"
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

           return validators.matches_regex(pattern, error_message=message)

   # Usage with pattern matching
   username_validator = UserValidators.username()
   email_validator = UserValidators.email()
   phone_validator = UserValidators.phone()

   # Validate a user
   def validate_user_field(value, validator, field_name):
       result = validator(value)
       match result:
           case Success(validated_value):
               return f"Valid {field_name}: {validated_value}"
           case Failure(error):
               return f"Invalid {field_name}: {error}"

   print(validate_user_field("john_doe123", username_validator, "username"))
   print(validate_user_field("john@example.com", email_validator, "email"))
   print(validate_user_field("123-456-7890", phone_validator, "phone"))
   print(validate_user_field("invalid-email", email_validator, "email"))

Working with External Data
--------------------------

Valid8r can also validate data from external sources like JSON or CSV files:

.. code-block:: python

   import json
   from valid8r import Maybe, validators
   from valid8r.core.maybe import Success, Failure

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
               match result:
                   case Success(value):
                       results[field] = value
                   case Failure(error):
                       errors[field] = error
           else:
               errors[field] = f"Missing required field: {field}"

       if errors:
           return Maybe.failure(errors)
       return Maybe.success(results)

   # Load data from a JSON file
   def load_and_validate_users(file_path):
       with open(file_path, 'r') as f:
           data = json.load(f)

       valid_users = []
       invalid_users = []

       for user in data:
           result = validate_user(user)
           match result:
               case Success(validated_user):
                   valid_users.append(validated_user)
               case Failure(errors):
                   invalid_users.append((user, errors))

       return valid_users, invalid_users

   # Example usage with pattern matching
   def process_users(file_path):
       try:
           valid_users, invalid_users = load_and_validate_users(file_path)
           print(f"Valid users: {len(valid_users)}")
           print(f"Invalid users: {len(invalid_users)}")

           # Process valid users
           for user in valid_users:
               print(f"Processing valid user: {user['name']}, age {user['age']}")

           # Report invalid users
           for user, errors in invalid_users:
               print(f"Invalid user: {user.get('name', 'Unknown')}")
               for field, error in errors.items():
                   print(f"  - {field}: {error}")

       except Exception as e:
           print(f"Error loading users: {e}")

Integration with Web Frameworks
-------------------------------

Valid8r can be integrated with web frameworks for form validation:

.. code-block:: python

   from flask import Flask, request, jsonify
   from valid8r import parsers, validators
   from valid8r.core.maybe import Success, Failure

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
       match username_result:
           case Failure(error):
               return jsonify({"error": "username", "message": error}), 400
           case Success(_):
               # Continue validation
               pass

       # Validate password
       password_result = password_validator(data.get('password', ''))
       match password_result:
           case Failure(error):
               return jsonify({"error": "password", "message": error}), 400
           case Success(_):
               # Continue validation
               pass

       # Both valid, proceed with registration
       # ...

       return jsonify({"message": "Registration successful"}), 201

Advanced Monadic Patterns
-------------------------

Valid8r's Maybe monad enables some advanced functional programming patterns:

.. code-block:: python

   from valid8r import Maybe, parsers
   from valid8r.core.maybe import Success, Failure
   from typing import List

   # Sequence operation - convert a list of Maybes to a Maybe of list
   def sequence(maybes: List[Maybe]):
       """Convert a list of Maybe values to a Maybe containing a list of values.

       If any Maybe is Failure, the result is Failure with the first error.
       """
       values = []
       for m in maybes:
           match m:
               case Failure(error):
                   return Maybe.failure(error)  # Return the first Failure
               case Success(value):
                   values.append(value)
       return Maybe.success(values)

   # Parse multiple values
   results = [
       parsers.parse_int("42"),
       parsers.parse_float("3.14"),
       parsers.parse_bool("true")
   ]

   # Sequence the results
   seq_result = sequence(results)
   match seq_result:
       case Success(values):
           print(f"All values parsed successfully: {values}")  # All values parsed successfully: [42, 3.14, True]
       case Failure(error):
           print(f"Error parsing values: {error}")

   # Invalid case
   results_with_error = [
       parsers.parse_int("42"),
       parsers.parse_int("not_a_number"),  # This will be a Failure
       parsers.parse_bool("true")
   ]

   seq_result = sequence(results_with_error)
   match seq_result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(f"Error parsing values: {error}")  # Error parsing values: Input must be a valid integer

   # Map operation - apply a function to a value inside a Maybe
   def map_maybe(maybe, func):
       """Apply a function to a value inside a Maybe."""
       match maybe:
           case Success(value):
               return Maybe.success(func(value))
           case Failure(error):
               return Maybe.failure(error)

   # Double a number inside a Maybe
   doubled = map_maybe(parsers.parse_int("42"), lambda x: x * 2)
   match doubled:
       case Success(value):
           print(value)  # 84
       case Failure(_):
           print("This won't happen")

Asynchronous Validation
-----------------------

For asynchronous validation in asyncio-based applications:

.. code-block:: python

   import asyncio
   from valid8r import Maybe, validators
   from valid8r.core.maybe import Success, Failure

   async def async_validator(value):
       """Simulate an asynchronous validation (e.g., checking a database)."""
       await asyncio.sleep(1)  # Simulate network delay
       if value.startswith("valid_"):
           return Maybe.success(value)
       return Maybe.failure("Value must start with 'valid_'")

   async def validate_user_exists(username):
       """Check if a username exists in the database."""
       # Simulate database check
       await asyncio.sleep(0.5)
       existing_users = ["alice", "bob", "charlie"]
       if username in existing_users:
           return Maybe.success(username)
       return Maybe.failure(f"User '{username}' does not exist")

   async def main():
       # Validate a string asynchronously
       result = await async_validator("valid_user")
       match result:
           case Success(value):
               print(f"Valid user: {value}")  # Valid user: valid_user
           case Failure(_):
               print("This won't happen")

       result = await async_validator("invalid_user")
       match result:
           case Success(_):
               print("This won't happen")
           case Failure(error):
               print(f"Invalid user: {error}")  # Invalid user: Value must start with 'valid_'

       # Check if user exists
       result = await validate_user_exists("alice")
       match result:
           case Success(value):
               print(f"User found: {value}")  # User found: alice
           case Failure(_):
               print("This won't happen")

       result = await validate_user_exists("dave")
       match result:
           case Success(_):
               print("This won't happen")
           case Failure(error):
               print(f"User error: {error}")  # User error: User 'dave' does not exist

   # Run with asyncio
   asyncio.run(main())

Testing Your Validators
-----------------------

Writing tests for your validators is crucial:

.. code-block:: python

   import unittest
   from valid8r import validators
   from valid8r.core.maybe import Success, Failure

   class TestValidators(unittest.TestCase):
       def test_minimum_validator(self):
           # Create validator
           is_positive = validators.minimum(0)

           # Test valid case
           result = is_positive(10)
           self.assertTrue(result.is_success())
           self.assertEqual(result.value_or(0), 10)

           # Test invalid case
           result = is_positive(-5)
           self.assertTrue(result.is_failure())
           self.assertIn("must be at least 0", result.error_or(""))

       def test_combined_validators(self):
           # Create combined validator
           is_valid_age = validators.minimum(18) & validators.maximum(65)

           # Test valid case
           result = is_valid_age(30)
           self.assertTrue(result.is_success())

           # Test invalid cases
           result = is_valid_age(15)
           self.assertTrue(result.is_failure())
           self.assertIn("must be at least 18", result.error_or(""))

           result = is_valid_age(70)
           self.assertTrue(result.is_failure())
           self.assertIn("must be at most 65", result.error_or(""))

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

   # Process results with pattern matching
   def summarize_validation_results(results):
       valid_count = 0
       invalid_count = 0
       errors = []

       for result in results:
           match result:
               case Success(_):
                   valid_count += 1
               case Failure(error):
                   invalid_count += 1
                   errors.append(error)

       return {
           "valid": valid_count,
           "invalid": invalid_count,
           "errors": errors[:5]  # Show just the first few errors
       }

   # Test with a large dataset
   test_data = list(range(10000))
   inefficient_results = validate_inefficient(test_data)
   efficient_results = validate_efficient(test_data)

   print(summarize_validation_results(inefficient_results))
   print(summarize_validation_results(efficient_results))

Production Security Patterns
-----------------------------

When deploying Valid8r in production, implement defense in depth:

.. code-block:: python

   from flask import Flask, request, jsonify
   from valid8r import parsers
   from valid8r.core.maybe import Success, Failure

   app = Flask(__name__)
   app.config['MAX_CONTENT_LENGTH'] = 10 * 1024  # Layer 1: Framework limit

   @app.route('/api/validate', methods=['POST'])
   def validate_input():
       data = request.get_json()

       # Layer 2: Application-level pre-validation
       email_input = data.get('email', '')
       if len(email_input) > 254:
           return jsonify({"error": "Email too long"}), 400

       # Layer 3: Valid8r parsing (with built-in DoS protection)
       match parsers.parse_email(email_input):
           case Success(email):
               return jsonify({"email": email.local + "@" + email.domain})
           case Failure(error):
               return jsonify({"error": "Invalid email"}), 400

.. seealso::
   See :doc:`/security/production-deployment` for complete framework-specific guides
   covering Flask, Django, FastAPI, rate limiting, and monitoring.

In the next sections, we'll explore concrete examples and the complete API reference.
