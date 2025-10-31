Chaining Validators
===================

This section demonstrates techniques for combining validators to create complex validation rules. Valid8r's composable validator architecture allows you to build sophisticated validation logic through simple chaining.

Basic Validator Chaining
------------------------

Using the ``&`` operator to combine validators with logical AND:

.. code-block:: python

   from valid8r import validators
   from valid8r.core.maybe import Success, Failure

   # Create individual validators
   is_positive = validators.minimum(0, "Value must be positive")
   is_less_than_100 = validators.maximum(100, "Value must be less than 100")

   # Combine validators with logical AND
   is_valid_percentage = is_positive & is_less_than_100

   # Test the combined validator
   result = is_valid_percentage(50)  # Valid
   match result:
       case Success(value):
           print(f"Valid percentage: {value}")  # Valid percentage: 50
       case Failure(_):
           print("This won't happen")

   # Test with invalid value (too small)
   result = is_valid_percentage(-10)  # Invalid
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(f"Error: {error}")  # Error: Value must be positive

   # Test with invalid value (too large)
   result = is_valid_percentage(150)  # Invalid
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(f"Error: {error}")  # Error: Value must be less than 100

Using Logical OR with the ``|`` Operator
----------------------------------------

Combine validators with logical OR using the ``|`` operator:

.. code-block:: python

   from valid8r import validators
   from valid8r.core.maybe import Success, Failure

   # Create individual validators
   is_zero = validators.predicate(lambda x: x == 0, "Value must be zero")
   is_positive = validators.minimum(1, "Value must be positive")

   # Combine validators with logical OR
   is_valid = is_zero | is_positive

   # Test with value that satisfies first validator
   result = is_valid(0)  # Valid (satisfies is_zero)
   match result:
       case Success(value):
           print(f"Valid value: {value}")  # Valid value: 0
       case Failure(_):
           print("This won't happen")

   # Test with value that satisfies second validator
   result = is_valid(10)  # Valid (satisfies is_positive)
   match result:
       case Success(value):
           print(f"Valid value: {value}")  # Valid value: 10
       case Failure(_):
           print("This won't happen")

   # Test with value that satisfies neither validator
   result = is_valid(-5)  # Invalid (satisfies neither)
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(f"Error: {error}")  # Error: Value must be positive

Negating Validators with the ``~`` Operator
-------------------------------------------

Negate a validator using the ``~`` operator:

.. code-block:: python

   from valid8r import validators
   from valid8r.core.maybe import Success, Failure

   # Create a validator
   is_even = validators.predicate(lambda x: x % 2 == 0, "Value must be even")

   # Negate the validator
   is_odd = ~is_even

   # Test with an odd number
   result = is_odd(5)  # Valid
   match result:
       case Success(value):
           print(f"Valid odd number: {value}")  # Valid odd number: 5
       case Failure(_):
           print("This won't happen")

   # Test with an even number
   result = is_odd(4)  # Invalid
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(f"Error: {error}")  # Error: Negated validation failed

   # Provide a custom error message for the negated validator
   from valid8r.core.combinators import not_validator

   is_odd_custom = not_validator(is_even, "Value must be odd")

   # Test with an even number
   result = is_odd_custom(4)  # Invalid
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(f"Error: {error}")  # Error: Value must be odd

Complex Validation Chains
-------------------------

Combine multiple validators with complex logic:

.. code-block:: python

   from valid8r import validators
   from valid8r.core.maybe import Success, Failure

   # Create individual validators
   is_positive = validators.minimum(0, "Value must be positive")
   is_even = validators.predicate(lambda x: x % 2 == 0, "Value must be even")
   is_multiple_of_3 = validators.predicate(
       lambda x: x % 3 == 0,
       "Value must be a multiple of 3"
   )
   is_less_than_100 = validators.maximum(100, "Value must be less than 100")

   # Create complex validation rule:
   # (Positive AND Even) OR (Multiple of 3 AND Less than 100)
   complex_validator = (is_positive & is_even) | (is_multiple_of_3 & is_less_than_100)

   # Test the complex validator with pattern matching
   def validate_number(number):
       result = complex_validator(number)
       match result:
           case Success(value):
               if value % 2 == 0 and value >= 0:
                   return f"{value} is valid (positive and even)"
               elif value % 3 == 0 and value < 100:
                   return f"{value} is valid (multiple of 3 and less than 100)"
               else:
                   return f"{value} is valid (satisfies complex condition)"
           case Failure(error):
               return f"{number} is invalid: {error}"

   print(validate_number(4))    # 4 is valid (positive and even)
   print(validate_number(9))    # 9 is valid (multiple of 3 and less than 100)
   print(validate_number(99))   # 99 is valid (multiple of 3 and less than 100)
   print(validate_number(-2))   # -2 is invalid: Value must be positive
   print(validate_number(102))  # 102 is valid (positive and even)

Validation Priority and Short-Circuit Behavior
----------------------------------------------

Validators are evaluated from left to right with short-circuit behavior:

.. code-block:: python

   from valid8r import validators
   from valid8r.core.maybe import Success, Failure
   import time

   # Create a slow validator that takes time to evaluate
   def slow_validator(value):
       time.sleep(1)  # Simulate slow validation
       if value < 100:
           return validators.minimum(0).func(value)
       return validators.minimum(0).func(value)

   slow = validators.Validator(slow_validator)

   # Create a fast validator
   is_even = validators.predicate(lambda x: x % 2 == 0, "Value must be even")

   # Combine validators with different order
   slow_first = slow & is_even
   even_first = is_even & slow

   # Test with efficient pattern matching
   def benchmark_validation(validator, value, description):
       start = time.time()
       result = validator(value)
       end = time.time()

       match result:
           case Success(val):
               print(f"{description} succeeded in {end - start:.2f} seconds with value {val}")
           case Failure(error):
               print(f"{description} failed in {end - start:.2f} seconds with error: {error}")

       return end - start

   # Invalid for is_even, won't evaluate slow
   benchmark_validation(even_first, 3, "even_first with odd number")  # Much faster

   # Invalid for slow, won't evaluate is_even
   benchmark_validation(slow_first, -5, "slow_first with negative number")  # Slower (≈1 second)

   # Valid case (evaluates both)
   benchmark_validation(even_first, 42, "even_first with valid number")  # Slower (≈1 second)

Validator Composition for Form Validation
-----------------------------------------

Use validator chaining to validate form fields:

.. code-block:: python

   from valid8r import validators
   from valid8r.core.maybe import Success, Failure
   import re

   # Username validation: 3-20 chars, alphanumeric with underscores
   username_validator = (
       validators.length(3, 20, "Username must be between 3 and 20 characters") &
       validators.matches_regex(
           r'^[a-zA-Z0-9_]+$',
           "Username can only contain letters, numbers, and underscores"
       )
   )

   # Password validation: 8-64 chars, contains uppercase, lowercase, and digit
   password_validator = (
       validators.length(8, 64, "Password must be between 8 and 64 characters") &
       validators.predicate(
           lambda s: any(c.isupper() for c in s),
           "Password must contain at least one uppercase letter"
       ) &
       validators.predicate(
           lambda s: any(c.islower() for c in s),
           "Password must contain at least one lowercase letter"
       ) &
       validators.predicate(
           lambda s: any(c.isdigit() for c in s),
           "Password must contain at least one digit"
       )
   )

   # Email validation: basic format check
   email_validator = validators.predicate(
       lambda s: bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', s)),
       "Invalid email format"
   )

   # Validate user registration form
   def validate_registration(username, password, email):
       # Validate each field
       username_result = username_validator(username)
       password_result = password_validator(password)
       email_result = email_validator(email)

       # Process results with pattern matching
       match (username_result, password_result, email_result):
           case (Success(u), Success(p), Success(e)):
               return {
                   "status": "success",
                   "message": "Registration successful",
                   "data": {
                       "username": u,
                       "password": "*" * len(p),  # Mask the password
                       "email": e
                   }
               }
           case (Failure(error), _, _):
               return {
                   "status": "error",
                   "field": "username",
                   "message": error
               }
           case (_, Failure(error), _):
               return {
                   "status": "error",
                   "field": "password",
                   "message": error
               }
           case (_, _, Failure(error)):
               return {
                   "status": "error",
                   "field": "email",
                   "message": error
               }

   # Test with valid inputs
   print(validate_registration("john_doe", "Passw0rd123", "john@example.com"))

   # Test with invalid inputs
   print(validate_registration("jo", "password", "not-an-email"))

Validator Factory Functions
---------------------------

Create functions that generate validators:

.. code-block:: python

   from valid8r import Maybe, validators
   from valid8r.core.maybe import Success, Failure

   # Factory function for creating a validator that checks if a value is divisible by n
   def divisible_by(n, error_message=None):
       def validator(value):
           if value % n == 0:
               return Maybe.success(value)
           return Maybe.failure(
               error_message or f"Value must be divisible by {n}"
           )
       return validators.Validator(validator)

   # Factory function for creating a validator that checks if a value is within a percentage of a target
   def within_percentage(target, percentage, error_message=None):
       def validator(value):
           min_val = target * (1 - percentage / 100)
           max_val = target * (1 + percentage / 100)
           if min_val <= value <= max_val:
               return Maybe.success(value)
           return Maybe.failure(
               error_message or f"Value must be within {percentage}% of {target}"
           )
       return validators.Validator(validator)

   # Create a validation pipeline with factory-generated validators
   def validate_measurement(value):
       # Use the factory functions
       is_divisible_by_5 = divisible_by(5)
       is_within_10pct_of_100 = within_percentage(100, 10)

       # Combine with other validators
       valid_number = validators.minimum(0) & is_divisible_by_5 & is_within_10pct_of_100

       # Validate with pattern matching
       result = valid_number(value)
       match result:
           case Success(validated):
               return f"{validated} is a valid measurement"
           case Failure(error):
               return f"Invalid measurement ({value}): {error}"

   # Test with various values
   for value in [100, 105, 95, 85, 7, 120]:
       print(validate_measurement(value))

Real-world Example: Data Pipeline Validation
--------------------------------------------

Use validator chaining in a data processing pipeline:

.. code-block:: python

   from valid8r import Maybe, validators
   from valid8r.core.maybe import Success, Failure
   from datetime import datetime

   # Sample data record
   record = {
       "id": "TRX-12345",
       "timestamp": "2023-04-15T12:30:45",
       "amount": 99.95,
       "currency": "USD",
       "status": "COMPLETED"
   }

   # Validate transaction ID
   def validate_id(id_str):
       id_validator = validators.predicate(
           lambda s: s.startswith("TRX-") and len(s) >= 8,
           "Transaction ID must start with 'TRX-' and be at least 8 characters"
       )
       return id_validator(id_str)

   # Validate timestamp
   def validate_timestamp(ts_str):
       try:
           dt = datetime.fromisoformat(ts_str)
           # Ensure timestamp is not in the future
           if dt > datetime.now():
               return Maybe.failure("Timestamp cannot be in the future")
           return Maybe.success(dt)
       except ValueError:
           return Maybe.failure("Invalid timestamp format")

   # Validate amount
   def validate_amount(amount):
       amount_validator = validators.minimum(0.01, "Amount must be positive") & validators.maximum(
           10000, "Amount cannot exceed 10000"
       )
       return amount_validator(amount)

   # Validate currency
   def validate_currency(currency):
       valid_currencies = ["USD", "EUR", "GBP", "JPY", "CAD"]
       return validators.predicate(
           lambda c: c in valid_currencies,
           f"Currency must be one of {valid_currencies}"
       )(currency)

   # Validate status
   def validate_status(status):
       valid_statuses = ["PENDING", "PROCESSING", "COMPLETED", "FAILED"]
       return validators.predicate(
           lambda s: s in valid_statuses,
           f"Status must be one of {valid_statuses}"
       )(status)

   # Validate complete transaction record
   def validate_transaction(record):
       # Process all validations at once using pattern matching
       id_result = validate_id(record.get("id", ""))
       timestamp_result = validate_timestamp(record.get("timestamp", ""))
       amount_result = validate_amount(record.get("amount", 0))
       currency_result = validate_currency(record.get("currency", ""))
       status_result = validate_status(record.get("status", ""))

       # Check all results together
       match (id_result, timestamp_result, amount_result, currency_result, status_result):
           case (Success(id_val), Success(ts_val), Success(amt_val), Success(curr_val), Success(stat_val)):
               # All validations passed, return validated record
               validated_record = record.copy()
               validated_record["timestamp"] = ts_val  # Replace with parsed datetime
               return Maybe.success(validated_record)
           case (Failure(error), _, _, _, _):
               return Maybe.failure(f"Invalid ID: {error}")
           case (_, Failure(error), _, _, _):
               return Maybe.failure(f"Invalid timestamp: {error}")
           case (_, _, Failure(error), _, _):
               return Maybe.failure(f"Invalid amount: {error}")
           case (_, _, _, Failure(error), _):
               return Maybe.failure(f"Invalid currency: {error}")
           case (_, _, _, _, Failure(error)):
               return Maybe.failure(f"Invalid status: {error}")

   # Process a transaction record
   def process_transaction(record):
       result = validate_transaction(record)
       match result:
           case Success(valid_record):
               print("Transaction is valid:")
               for key, value in valid_record.items():
                   print(f"  {key}: {value}")
               return True
           case Failure(error):
               print(f"Transaction is invalid: {error}")
               return False

   # Test with our sample record
   process_transaction(record)

   # Test with invalid record
   invalid_record = record.copy()
   invalid_record["amount"] = -10
   process_transaction(invalid_record)

In the next sections, we'll explore more examples and patterns for custom validators and interactive prompting.
