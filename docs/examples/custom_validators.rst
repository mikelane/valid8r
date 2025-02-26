Custom Validators
=================

This section demonstrates how to create custom validators to extend Valid8r's capabilities for specific validation scenarios.

Creating a Simple Custom Validator
----------------------------------

Custom validators are functions that take a value and return a Maybe object:

.. code-block:: python

   from valid8r import Maybe, validators

   # Create a custom validator for even numbers
   def validate_even(value):
       if value % 2 == 0:
           return Maybe.just(value)
       return Maybe.nothing("Value must be even")

   # Convert to a Validator instance for operator overloading
   is_even = validators.Validator(validate_even)

   # Use the custom validator
   result = is_even(42)  # Valid
   print(result.is_just())  # True

   result = is_even(43)  # Invalid
   print(result.is_nothing())  # True
   print(result.error())  # "Value must be even"

Creating a Validator Factory Function
-------------------------------------

For reusable validators with parameters, create factory functions:

.. code-block:: python

   from valid8r import Maybe, validators

   # Validator factory for divisibility check
   def divisible_by(n, error_message=None):
       def validator(value):
           if value % n == 0:
               return Maybe.just(value)
           return Maybe.nothing(
               error_message or f"Value must be divisible by {n}"
           )
       return validators.Validator(validator)

   # Create validators using the factory
   is_divisible_by_3 = divisible_by(3)
   is_divisible_by_5 = divisible_by(5)

   # Use the validators
   result = is_divisible_by_3(9)  # Valid
   print(result.is_just())  # True

   result = is_divisible_by_5(7)  # Invalid
   print(result.is_nothing())  # True
   print(result.error())  # "Value must be divisible by 5"

   # Custom error message
   is_multiple_of_10 = divisible_by(10, "Must be a multiple of 10")
   result = is_multiple_of_10(15)
   print(result.error())  # "Must be a multiple of 10"

String Validation Examples
--------------------------

Custom validators for common string validation scenarios:

.. code-block:: python

   from valid8r import Maybe, validators
   import re

   # Email validation
   def email_validator(error_message=None):
       pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

       def validator(value):
           if re.match(pattern, value):
               return Maybe.just(value)
           return Maybe.nothing(
               error_message or "Invalid email format"
           )
       return validators.Validator(validator)

   # URL validation
   def url_validator(error_message=None):
       pattern = r"^https?://(?:www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_+.~#?&/=]*)$"

       def validator(value):
           if re.match(pattern, value):
               return Maybe.just(value)
           return Maybe.nothing(
               error_message or "Invalid URL format"
           )
       return validators.Validator(validator)

   # Phone number validation
   def phone_validator(country="international", error_message=None):
       patterns = {
           "us": r"^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$",
           "international": r"^\+[1-9]\d{1,14}$"
       }

       pattern = patterns.get(country.lower(), patterns["international"])

       def validator(value):
           if re.match(pattern, value):
               return Maybe.just(value)
           return Maybe.nothing(
               error_message or f"Invalid phone number for {country} format"
           )
       return validators.Validator(validator)

   # Use the validators
   is_valid_email = email_validator()
   is_valid_url = url_validator()
   is_valid_us_phone = phone_validator("us")

   email_result = is_valid_email("user@example.com")  # Valid
   print(email_result.is_just())  # True

   url_result = is_valid_url("https://example.com/path")  # Valid
   print(url_result.is_just())  # True

   phone_result = is_valid_us_phone("555-123-4567")  # Valid
   print(phone_result.is_just())  # True

   # Invalid examples
   email_result = is_valid_email("not-an-email")
   print(email_result.error())  # "Invalid email format"

   url_result = is_valid_url("not-a-url")
   print(url_result.error())  # "Invalid URL format"

   phone_result = is_valid_us_phone("123")
   print(phone_result.error())  # "Invalid phone number for us format"

Date and Time Validators
------------------------

Custom validators for date and time validation:

.. code-block:: python

   from valid8r import Maybe, validators
   from datetime import date, timedelta

   # Date range validator
   def date_between(start_date, end_date, error_message=None):
       def validator(value):
           if start_date <= value <= end_date:
               return Maybe.just(value)
           return Maybe.nothing(
               error_message or f"Date must be between {start_date} and {end_date}"
           )
       return validators.Validator(validator)

   # Future date validator
   def future_date(include_today=True, error_message=None):
       def validator(value):
           today = date.today()
           if include_today and value >= today:
               return Maybe.just(value)
           elif not include_today and value > today:
               return Maybe.just(value)
           return Maybe.nothing(
               error_message or "Date must be in the future"
           )
       return validators.Validator(validator)

   # Past date validator
   def past_date(include_today=True, error_message=None):
       def validator(value):
           today = date.today()
           if include_today and value <= today:
               return Maybe.just(value)
           elif not include_today and value < today:
               return Maybe.just(value)
           return Maybe.nothing(
               error_message or "Date must be in the past"
           )
       return validators.Validator(validator)

   # Weekday validator
   def is_weekday(error_message=None):
       def validator(value):
           if value.weekday() < 5:  # Monday(0) to Friday(4)
               return Maybe.just(value)
           return Maybe.nothing(
               error_message or "Date must be a weekday"
           )
       return validators.Validator(validator)

   # Weekend validator
   def is_weekend(error_message=None):
       def validator(value):
           if value.weekday() >= 5:  # Saturday(5) and Sunday(6)
               return Maybe.just(value)
           return Maybe.nothing(
               error_message or "Date must be a weekend"
           )
       return validators.Validator(validator)

   # Use the validators
   today = date.today()
   next_month = today + timedelta(days=30)

   # Create validators
   is_this_month = date_between(today, next_month)
   is_future = future_date(include_today=False)
   is_past = past_date(include_today=False)
   is_business_day = is_weekday()
   is_weekend_day = is_weekend()

   # Test with a specific date
   test_date = date(2023, 4, 15)  # A Saturday in April 2023

   result = is_weekend_day(test_date)  # Valid (it's a Saturday)
   print(result.is_just())  # True

   result = is_business_day(test_date)  # Invalid (it's not a weekday)
   print(result.is_nothing())  # True
   print(result.error())  # "Date must be a weekday"

Collection Validators
---------------------

Custom validators for collections like lists and dictionaries:

.. code-block:: python

   from valid8r import Maybe, validators

   # List length validator
   def list_length(min_length, max_length=None, error_message=None):
       if max_length is None:
           max_length = float('inf')

       def validator(value):
           if not isinstance(value, list):
               return Maybe.nothing("Value must be a list")

           if min_length <= len(value) <= max_length:
               return Maybe.just(value)

           if min_length == max_length:
               return Maybe.nothing(
                   error_message or f"List must contain exactly {min_length} items"
               )

           return Maybe.nothing(
               error_message or f"List must contain between {min_length} and {max_length} items"
           )
       return validators.Validator(validator)

   # Validator for all list items
   def each_item(item_validator, error_message=None):
       def validator(value):
           if not isinstance(value, list):
               return Maybe.nothing("Value must be a list")

           errors = []
           results = []

           for i, item in enumerate(value):
               result = item_validator(item)
               if result.is_just():
                   results.append(result.value())
               else:
                   errors.append(f"Item {i}: {result.error()}")

           if errors:
               return Maybe.nothing(
                   error_message or "\n".join(errors)
               )

           return Maybe.just(results)
       return validators.Validator(validator)

   # Dictionary validator with required keys
   def has_keys(required_keys, error_message=None):
       def validator(value):
           if not isinstance(value, dict):
               return Maybe.nothing("Value must be a dictionary")

           missing_keys = [key for key in required_keys if key not in value]

           if missing_keys:
               return Maybe.nothing(
                   error_message or f"Missing required keys: {', '.join(missing_keys)}"
               )

           return Maybe.just(value)
       return validators.Validator(validator)

   # Use the validators
   is_non_empty_list = list_length(1)
   has_max_5_items = list_length(0, 5, "List cannot have more than 5 items")
   all_positive = each_item(validators.minimum(0))

   # Test list validators
   result = is_non_empty_list([1, 2, 3])  # Valid
   print(result.is_just())  # True

   result = has_max_5_items([1, 2, 3, 4, 5, 6])  # Invalid
   print(result.error())  # "List cannot have more than 5 items"

   result = all_positive([1, 2, 3, -4, 5])  # Invalid
   print(result.error())  # "Item 3: Value must be at least 0"

   # Test dictionary validator
   has_required_fields = has_keys(["name", "email", "age"])

   result = has_required_fields({"name": "John", "email": "john@example.com", "age": 30})  # Valid
   print(result.is_just())  # True

   result = has_required_fields({"name": "John", "email": "john@example.com"})  # Invalid
   print(result.error())  # "Missing required keys: age"

Custom Domain-Specific Validators
---------------------------------

Creating validators for specific business domains:

.. code-block:: python

   from valid8r import Maybe, validators

   # Credit card validator
   def credit_card_validator(error_message=None):
       def luhn_check(card_number):
           """Luhn algorithm for credit card validation."""
           digits = [int(d) for d in card_number if d.isdigit()]

           if not digits or len(digits) < 13 or len(digits) > 19:
               return False

           # Luhn algorithm
           checksum = 0
           odd_even = len(digits) % 2

           for i, digit in enumerate(digits):
               if ((i + odd_even) % 2) == 0:
                   doubled = digit * 2
                   checksum += doubled if doubled < 10 else doubled - 9
               else:
                   checksum += digit

           return checksum % 10 == 0

       def validator(value):
           # Remove spaces and dashes
           card_number = ''.join(c for c in value if c.isdigit() or c.isalpha())

           if luhn_check(card_number):
               return Maybe.just(value)
           return Maybe.nothing(
               error_message or "Invalid credit card number"
           )
       return validators.Validator(validator)

   # ISBN validator
   def isbn_validator(error_message=None):
       def validate_isbn10(isbn):
           if len(isbn) != 10:
               return False

           # ISBN-10 validation
           digits = [int(c) if c.isdigit() else 10 if c == 'X' else -1 for c in isbn]

           if -1 in digits:
               return False

           checksum = sum((10 - i) * digit for i, digit in enumerate(digits))
           return checksum % 11 == 0

       def validate_isbn13(isbn):
           if len(isbn) != 13:
               return False

           # ISBN-13 validation
           digits = [int(c) for c in isbn if c.isdigit()]

           if len(digits) != 13:
               return False

           checksum = sum(digit if i % 2 == 0 else digit * 3 for i, digit in enumerate(digits))
           return checksum % 10 == 0

       def validator(value):
           # Remove dashes and spaces
           isbn = ''.join(c for c in value if c.isdigit() or c == 'X')

           if validate_isbn10(isbn) or validate_isbn13(isbn):
               return Maybe.just(value)
           return Maybe.nothing(
               error_message or "Invalid ISBN"
           )
       return validators.Validator(validator)

   # Postcode/Zip code validator
   def postcode_validator(country="US", error_message=None):
       patterns = {
           "US": r"^\d{5}(-\d{4})?$",
           "UK": r"^[A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2}$",
           "CA": r"^[A-Z]\d[A-Z] \d[A-Z]\d$",
           "AU": r"^\d{4}$"
       }

       pattern = patterns.get(country, patterns["US"])

       def validator(value):
           import re
           if re.match(pattern, value, re.IGNORECASE):
               return Maybe.just(value)
           return Maybe.nothing(
               error_message or f"Invalid {country} postal code"
           )
       return validators.Validator(validator)

   # Use the domain-specific validators
   is_valid_credit_card = credit_card_validator()
   is_valid_isbn = isbn_validator()
   is_valid_us_zip = postcode_validator("US")
   is_valid_uk_postcode = postcode_validator("UK")

   # Test with valid values
   cc_result = is_valid_credit_card("4111 1111 1111 1111")  # Valid test number
   print(cc_result.is_just())  # True

   isbn_result = is_valid_isbn("978-3-16-148410-0")  # Valid ISBN-13
   print(isbn_result.is_just())  # True

   zip_result = is_valid_us_zip("90210")  # Valid US ZIP
   print(zip_result.is_just())  # True

   postcode_result = is_valid_uk_postcode("SW1A 1AA")  # Valid UK postcode
   print(postcode_result.is_just())  # True

Creating Stateful Validators
----------------------------

Validators that maintain state or depend on external resources:

.. code-block:: python

   from valid8r import Maybe, validators

   # Validator that ensures uniqueness within a session
   class UniqueValidator:
       def __init__(self, error_message=None):
           self.seen_values = set()
           self.error_message = error_message or "Value must be unique"

       def __call__(self, value):
           if value in self.seen_values:
               return Maybe.nothing(self.error_message)
           self.seen_values.add(value)
           return Maybe.just(value)

       def reset(self):
           self.seen_values.clear()

   # Validator that checks against a database
   class DatabaseValidator:
       def __init__(self, db_connection, query_template, error_message=None):
           self.db_connection = db_connection
           self.query_template = query_template
           self.error_message = error_message

       def __call__(self, value):
           cursor = self.db_connection.cursor()
           query = self.query_template.format(value=value)
           cursor.execute(query)
           result = cursor.fetchone()

           if result:
               return Maybe.just(value)
           return Maybe.nothing(self.error_message or "Invalid value")

   # Usage example (simulated)
   # Create a unique validator
   is_unique = UniqueValidator("This value has already been used")

   # Test with sequential values
   result1 = is_unique("apple")  # Valid
   print(result1.is_just())  # True

   result2 = is_unique("banana")  # Valid
   print(result2.is_just())  # True

   result3 = is_unique("apple")  # Invalid (already seen)
   print(result3.is_nothing())  # True
   print(result3.error())  # "This value has already been used"

   # Reset the unique validator
   is_unique.reset()

   result4 = is_unique("apple")  # Valid again after reset
   print(result4.is_just())  # True

In the next section, we'll explore interactive prompting techniques with validation.