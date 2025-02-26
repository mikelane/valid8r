Chaining Validators
===================

This section demonstrates techniques for combining validators to create complex validation rules.

Basic Validator Chaining
------------------------

Using the `&` operator to combine validators with logical AND:

.. code-block:: python

   from valid8r import validators

   # Create individual validators
   is_positive = validators.minimum(0, "Value must be positive")
   is_less_than_100 = validators.maximum(100, "Value must be less than 100")

   # Combine validators with logical AND
   is_valid_percentage = is_positive & is_less_than_100

   # Test the combined validator
   result = is_valid_percentage(50)  # Valid
   print(result.is_just())  # True

   result = is_valid_percentage(-10)  # Invalid
   print(result.is_nothing())  # True
   print(result.error())  # "Value must be positive"

   result = is_valid_percentage(150)  # Invalid
   print(result.is_nothing())  # True
   print(result.error())  # "Value must be less than 100"

Using Logical OR with the `|` Operator
--------------------------------------

Combine validators with logical OR using the `|` operator:

.. code-block:: python

   from valid8r import validators

   # Create individual validators
   is_zero = validators.predicate(lambda x: x == 0, "Value must be zero")
   is_positive = validators.minimum(1, "Value must be positive")

   # Combine validators with logical OR
   is_valid = is_zero | is_positive

   # Test the combined validator
   result = is_valid(0)  # Valid (satisfies is_zero)
   print(result.is_just())  # True

   result = is_valid(10)  # Valid (satisfies is_positive)
   print(result.is_just())  # True

   result = is_valid(-5)  # Invalid (satisfies neither)
   print(result.is_nothing())  # True
   print(result.error())  # "Value must be positive"

Negating Validators with the `~` Operator
-----------------------------------------

Negate a validator using the `~` operator:

.. code-block:: python

   from valid8r import validators

   # Create a validator
   is_even = validators.predicate(lambda x: x % 2 == 0, "Value must be even")

   # Negate the validator
   is_odd = ~is_even

   # Test the negated validator
   result = is_odd(5)  # Valid
   print(result.is_just())  # True

   result = is_odd(4)  # Invalid
   print(result.is_nothing())  # True
   print(result.error())  # "Negated validation failed"

   # Provide a custom error message for the negated validator
   from valid8r.core.combinators import not_validator

   is_odd_custom = not_validator(is_even, "Value must be odd")

   result = is_odd_custom(4)  # Invalid
   print(result.error())  # "Value must be odd"

Complex Validation Chains
-------------------------

Combine multiple validators with complex logic:

.. code-block:: python

   from valid8r import validators

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

   # Test the complex validator
   result = complex_validator(4)   # Valid (positive and even)
   print(result.is_just())  # True

   result = complex_validator(9)   # Valid (multiple of 3 and less than 100)
   print(result.is_just())  # True

   result = complex_validator(99)  # Valid (multiple of 3 and less than 100)
   print(result.is_just())  # True

   result = complex_validator(-2)  # Invalid (not positive)
   print(result.is_nothing())  # True

   result = complex_validator(102)  # Invalid (not even, > 100)
   print(result.is_nothing())  # True

Validation Priority and Short-Circuit Behavior
----------------------------------------------

Validators are evaluated from left to right with short-circuit behavior:

.. code-block:: python

   from valid8r import validators
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

   # Test with invalid input for the first validator
   start = time.time()
   result = slow_first(-5)  # Invalid for slow, won't evaluate is_even
   end = time.time()
   print(f"slow_first took {end - start:.2f} seconds")  # ~1 second

   start = time.time()
   result = even_first(3)  # Invalid for is_even, won't evaluate slow
   end = time.time()
   print(f"even_first took {end - start:.2f} seconds")  # Much less than 1 second

Validator Composition for Form Validation
-----------------------------------------

Use validator chaining to validate form fields:

.. code-block:: python

   from valid8r import validators
   import re

   # Username validation: 3-20 chars, alphanumeric with underscores
   username_validator = (
       validators.length(3, 20, "Username must be between 3 and 20 characters") &
       validators.predicate(
           lambda s: bool(re.match(r'^[a-zA-Z0-9_]+$', s)),
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

   # Test the validators
   username_result = username_validator("john_doe")
   password_result = password_validator("Passw0rd")
   email_result = email_validator("john@example.com")

   print(f"Username valid: {username_result.is_just()}")
   print(f"Password valid: {password_result.is_just()}")
   print(f"Email valid: {email_result.is_just()}")

   # Test with invalid inputs
   invalid_username = username_validator("jo")
   invalid_password = password_validator("password")  # Missing uppercase and digit
   invalid_email = email_validator("not-an-email")

   print(f"Invalid username error: {invalid_username.error()}")
   print(f"Invalid password error: {invalid_password.error()}")
   print(f"Invalid email error: {invalid_email.error()}")

Validator Factory Functions
---------------------------

Create functions that generate validators:

.. code-block:: python

   from valid8r import Maybe, validators

   # Factory function for creating a validator that checks if a value is divisible by n
   def divisible_by(n, error_message=None):
       def validator(value):
           if value % n == 0:
               return Maybe.just(value)
           return Maybe.nothing(
               error_message or f"Value must be divisible by {n}"
           )
       return validators.Validator(validator)

   # Factory function for creating a validator that checks if a value is within a percentage of a target
   def within_percentage(target, percentage, error_message=None):
       def validator(value):
           min_val = target * (1 - percentage / 100)
           max_val = target * (1 + percentage / 100)
           if min_val <= value <= max_val:
               return Maybe.just(value)
           return Maybe.nothing(
               error_message or f"Value must be within {percentage}% of {target}"
           )
       return validators.Validator(validator)

   # Use the factory functions
   is_divisible_by_5 = divisible_by(5)
   is_within_10pct_of_100 = within_percentage(100, 10)

   # Combine with other validators
   valid_number = validators.minimum(0) & is_divisible_by_5 & is_within_10pct_of_100

   # Test
   result = valid_number(100)  # Valid
   print(result.is_just())  # True

   result = valid_number(105)  # Valid
   print(result.is_just())  # True

   result = valid_number(95)  # Valid
   print(result.is_just())  # True

   result = valid_number(85)  # Invalid (not within 10% of 100)
   print(result.is_nothing())  # True

   result = valid_number(7)  # Invalid (not divisible by 5)
   print(result.is_nothing())  # True

Real-world Example: Data Pipeline Validation
--------------------------------------------

Use validator chaining in a data processing pipeline:

.. code-block:: python

   from valid8r import Maybe, validators
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
               return Maybe.nothing("Timestamp cannot be in the future")
           return Maybe.just(dt)
       except ValueError:
           return Maybe.nothing("Invalid timestamp format")

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

   # Validate complete record
   def validate_transaction(record):
       # Check required fields
       required_fields = ["id", "timestamp", "amount", "currency", "status"]
       for field in required_fields:
           if field not in record:
               return Maybe.nothing(f"Missing required field: {field}")

       # Validate each field
       id_result = validate_id(record["id"])
       if id_result.is_nothing():
           return Maybe.nothing(f"Invalid ID: {id_result.error()}")

       timestamp_result = validate_timestamp(record["timestamp"])
       if timestamp_result.is_nothing():
           return Maybe.nothing(f"Invalid timestamp: {timestamp_result.error()}")

       amount_result = validate_amount(record["amount"])
       if amount_result.is_nothing():
           return Maybe.nothing(f"Invalid amount: {amount_result.error()}")

       currency_result = validate_currency(record["currency"])
       if currency_result.is_nothing():
           return Maybe.nothing(f"Invalid currency: {currency_result.error()}")

       status_result = validate_status(record["status"])
       if status_result.is_nothing():
           return Maybe.nothing(f"Invalid status: {status_result.error()}")

       # All validations passed, return validated record
       validated_record = record.copy()
       validated_record["timestamp"] = timestamp_result.value()  # Replace with parsed datetime
       return Maybe.just(validated_record)

   # Process a batch of records
   def process_batch(records):
       valid_records = []
       invalid_records = []

       for record in records:
           result = validate_transaction(record)
           if result.is_just():
               valid_records.append(result.value())
           else:
               invalid_records.append((record, result.error()))

       return valid_records, invalid_records

   # Test with our sample record
   valid, invalid = process_batch([record])
   print(f"Valid records: {len(valid)}")
   print(f"Invalid records: {len(invalid)}")

In the next sections, we'll explore more examples and patterns for custom validators and interactive prompting.