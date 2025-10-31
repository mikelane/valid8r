Custom Validators
=================

This section demonstrates how to create custom validators to extend Valid8r's capabilities for specific validation scenarios. While Valid8r provides many built-in validators, you can easily create your own validators for domain-specific validation needs.

Creating a Simple Custom Validator
----------------------------------

Custom validators are functions that take a value and return a Maybe object. To create a custom validator:

.. code-block:: python

   from valid8r import Maybe, validators
   from valid8r.core.maybe import Success, Failure

   # Create a custom validator for even numbers
   def validate_even(value):
       if value % 2 == 0:
           return Maybe.success(value)
       return Maybe.failure("Value must be even")

   # Convert to a Validator instance for operator overloading
   is_even = validators.Validator(validate_even)

   # Use the custom validator with pattern matching
   result = is_even(42)  # Valid
   match result:
       case Success(value):
           print(f"Valid even number: {value}")  # Valid even number: 42
       case Failure(_):
           print("This won't happen")

   # Invalid case
   result = is_even(43)  # Invalid
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(f"Error: {error}")  # Error: Value must be even

Creating a Validator Factory Function
-------------------------------------

For reusable validators with parameters, create factory functions that return validator instances:

.. code-block:: python

   from valid8r import Maybe, validators
   from valid8r.core.maybe import Success, Failure

   # Validator factory for divisibility check
   def divisible_by(n, error_message=None):
       def validator(value):
           if value % n == 0:
               return Maybe.success(value)
           return Maybe.failure(
               error_message or f"Value must be divisible by {n}"
           )
       return validators.Validator(validator)

   # Create validators using the factory
   is_divisible_by_3 = divisible_by(3)
   is_divisible_by_5 = divisible_by(5)

   # Process results with pattern matching
   def check_divisibility(value):
       div3_result = is_divisible_by_3(value)
       div5_result = is_divisible_by_5(value)

       match (div3_result, div5_result):
           case (Success(_), Success(_)):
               return f"{value} is divisible by both 3 and 5"
           case (Success(_), Failure(_)):
               return f"{value} is divisible by 3 but not by 5"
           case (Failure(_), Success(_)):
               return f"{value} is divisible by 5 but not by 3"
           case (Failure(_), Failure(_)):
               return f"{value} is divisible by neither 3 nor 5"

   # Test with different values
   for value in [9, 10, 15, 7]:
       print(check_divisibility(value))

   # Custom error message
   is_multiple_of_10 = divisible_by(10, "Must be a multiple of 10")
   result = is_multiple_of_10(15)
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(f"Error: {error}")  # Error: Must be a multiple of 10

String Validation Examples
--------------------------

Custom validators for common string validation scenarios:

.. code-block:: python

   from valid8r import Maybe, validators
   from valid8r.core.maybe import Success, Failure
   import re

   # Email validation using matches_regex
   def email_validator(error_message=None):
       return validators.matches_regex(
           r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
           error_message=error_message or "Invalid email format"
       )

   # URL validation using matches_regex
   def url_validator(error_message=None):
       return validators.matches_regex(
           r"^https?://(?:www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_+.~#?&/=]*)$",
           error_message=error_message or "Invalid URL format"
       )

   # Phone number validation using matches_regex
   def phone_validator(country="international", error_message=None):
       patterns = {
           "us": r"^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$",
           "international": r"^\+[1-9]\d{1,14}$"
       }

       pattern = patterns.get(country.lower(), patterns["international"])

       return validators.matches_regex(
           pattern,
           error_message=error_message or f"Invalid phone number for {country} format"
       )

   # Validate contact information with pattern matching
   def validate_contact_info(email, url, phone):
       is_valid_email = email_validator()
       is_valid_url = url_validator()
       is_valid_us_phone = phone_validator("us")

       email_result = is_valid_email(email)
       url_result = is_valid_url(url)
       phone_result = is_valid_us_phone(phone)

       # Process all validation results at once
       match (email_result, url_result, phone_result):
           case (Success(e), Success(u), Success(p)):
               return {
                   "status": "valid",
                   "contact": {
                       "email": e,
                       "website": u,
                       "phone": p
                   }
               }
           case (Failure(error), _, _):
               return {
                   "status": "invalid",
                   "field": "email",
                   "error": error
               }
           case (_, Failure(error), _):
               return {
                   "status": "invalid",
                   "field": "website",
                   "error": error
               }
           case (_, _, Failure(error)):
               return {
                   "status": "invalid",
                   "field": "phone",
                   "error": error
               }

   # Test with valid data
   result = validate_contact_info(
       "user@example.com",
       "https://example.com",
       "555-123-4567"
   )
   print(result["status"])  # valid

   # Test with invalid data
   result = validate_contact_info(
       "not-an-email",
       "https://example.com",
       "555-123-4567"
   )
   print(f"{result['status']}: {result['field']} - {result['error']}")

Date and Time Validators
------------------------

Custom validators for date and time validation:

.. code-block:: python

   from valid8r import Maybe, validators
   from valid8r.core.maybe import Success, Failure
   from datetime import date, timedelta

   # Date range validator
   def date_between(start_date, end_date, error_message=None):
       def validator(value):
           if start_date <= value <= end_date:
               return Maybe.success(value)
           return Maybe.failure(
               error_message or f"Date must be between {start_date} and {end_date}"
           )
       return validators.Validator(validator)

   # Future date validator
   def future_date(include_today=True, error_message=None):
       def validator(value):
           today = date.today()
           if include_today and value >= today:
               return Maybe.success(value)
           elif not include_today and value > today:
               return Maybe.success(value)
           return Maybe.failure(
               error_message or "Date must be in the future"
           )
       return validators.Validator(validator)

   # Past date validator
   def past_date(include_today=True, error_message=None):
       def validator(value):
           today = date.today()
           if include_today and value <= today:
               return Maybe.success(value)
           elif not include_today and value < today:
               return Maybe.success(value)
           return Maybe.failure(
               error_message or "Date must be in the past"
           )
       return validators.Validator(validator)

   # Weekday validator
   def is_weekday(error_message=None):
       def validator(value):
           if value.weekday() < 5:  # Monday(0) to Friday(4)
               return Maybe.success(value)
           return Maybe.failure(
               error_message or "Date must be a weekday"
           )
       return validators.Validator(validator)

   # Weekend validator
   def is_weekend(error_message=None):
       def validator(value):
           if value.weekday() >= 5:  # Saturday(5) and Sunday(6)
               return Maybe.success(value)
           return Maybe.failure(
               error_message or "Date must be a weekend"
           )
       return validators.Validator(validator)

   # Process date with pattern matching
   def validate_appointment_date(appointment_date):
       today = date.today()
       next_month = today + timedelta(days=30)

       # Create validators
       is_this_month = date_between(today, next_month)
       is_weekday = is_weekday()

       # Check if date is valid for appointment
       month_result = is_this_month(appointment_date)
       weekday_result = is_weekday(appointment_date)

       match (month_result, weekday_result):
           case (Success(_), Success(_)):
               return f"Appointment on {appointment_date.isoformat()} is valid (weekday this month)"
           case (Failure(_), Success(_)):
               return f"Appointment on {appointment_date.isoformat()} is invalid (not within a month)"
           case (Success(_), Failure(_)):
               return f"Appointment on {appointment_date.isoformat()} is invalid (not a weekday)"
           case (Failure(err1), Failure(err2)):
               return f"Appointment on {appointment_date.isoformat()} is invalid: {err1} and {err2}"

   # Test with different dates
   valid_date = date.today() + timedelta(days=5)
   weekend_date = date.today() + timedelta(days=(5 - date.today().weekday() + 6) % 7)
   future_date = date.today() + timedelta(days=60)

   print(validate_appointment_date(valid_date))
   print(validate_appointment_date(weekend_date))
   print(validate_appointment_date(future_date))

Collection Validators
---------------------

Custom validators for collections like lists and dictionaries:

.. code-block:: python

   from valid8r import Maybe, validators
   from valid8r.core.maybe import Success, Failure

   # List length validator
   def list_length(min_length, max_length=None, error_message=None):
       if max_length is None:
           max_length = float('inf')

       def validator(value):
           if not isinstance(value, list):
               return Maybe.failure("Value must be a list")

           if min_length <= len(value) <= max_length:
               return Maybe.success(value)

           if min_length == max_length:
               return Maybe.failure(
                   error_message or f"List must contain exactly {min_length} items"
               )

           return Maybe.failure(
               error_message or f"List must contain between {min_length} and {max_length} items"
           )
       return validators.Validator(validator)

   # Validator for all list items
   def each_item(item_validator, error_message=None):
       def validator(value):
           if not isinstance(value, list):
               return Maybe.failure("Value must be a list")

           errors = []
           results = []

           for i, item in enumerate(value):
               result = item_validator(item)
               match result:
                   case Success(validated_item):
                       results.append(validated_item)
                   case Failure(error):
                       errors.append(f"Item {i}: {error}")

           if errors:
               return Maybe.failure(
                   error_message or "\n".join(errors)
               )

           return Maybe.success(results)
       return validators.Validator(validator)

   # Dictionary validator with required keys
   def has_keys(required_keys, error_message=None):
       def validator(value):
           if not isinstance(value, dict):
               return Maybe.failure("Value must be a dictionary")

           missing_keys = [key for key in required_keys if key not in value]

           if missing_keys:
               return Maybe.failure(
                   error_message or f"Missing required keys: {', '.join(missing_keys)}"
               )

           return Maybe.success(value)
       return validators.Validator(validator)

   # Validate a product catalog with pattern matching
   def validate_product_catalog(products):
       is_non_empty_list = list_length(1)
       is_positive_price = validators.minimum(0)
       all_valid_prices = each_item(is_positive_price)
       has_required_product_fields = has_keys(["name", "price", "stock"])

       # First validate that we have a non-empty list
       list_result = is_non_empty_list(products)
       match list_result:
           case Failure(error):
               return f"Invalid product catalog: {error}"
           case Success(_):
               pass  # Continue validation

       # Then validate each product
       valid_products = []
       invalid_products = []

       for i, product in enumerate(products):
           # Validate product structure
           structure_result = has_required_product_fields(product)

           match structure_result:
               case Failure(error):
                   invalid_products.append({
                       "index": i,
                       "product": product,
                       "error": error
                   })
                   continue
               case Success(_):
                   # Validate price
                   price_result = is_positive_price(product.get("price", 0))
                   match price_result:
                       case Failure(error):
                           invalid_products.append({
                               "index": i,
                               "product": product,
                               "error": f"Price is invalid: {error}"
                           })
                           continue
                       case Success(_):
                           valid_products.append(product)

       if invalid_products:
           return {
               "status": "partial",
               "valid_count": len(valid_products),
               "invalid_count": len(invalid_products),
               "invalid_products": invalid_products
           }

       return {
           "status": "success",
           "product_count": len(valid_products),
           "products": valid_products
       }

   # Test with a product catalog
   products = [
       {"name": "Laptop", "price": 999.99, "stock": 10},
       {"name": "Phone", "price": 499.99, "stock": 20},
       {"name": "Headphones", "price": -49.99, "stock": 30},  # Invalid price
       {"name": "Tablet", "stock": 15}  # Missing price
   ]

   result = validate_product_catalog(products)
   print(f"Status: {result['status']}")
   if result["status"] == "partial":
       print(f"Valid products: {result['valid_count']}")
       print(f"Invalid products: {result['invalid_count']}")
       for invalid in result["invalid_products"]:
           print(f"  Product #{invalid['index']}: {invalid['error']}")

Custom Domain-Specific Validators
---------------------------------

Creating validators for specific business domains:

.. code-block:: python

   from valid8r import Maybe, validators
   from valid8r.core.maybe import Success, Failure

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
               return Maybe.success(value)
           return Maybe.failure(
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
               return Maybe.success(value)
           return Maybe.failure(
               error_message or "Invalid ISBN"
           )
       return validators.Validator(validator)

   # Validate payment and product information
   def validate_purchase(credit_card, isbn):
       cc_validator = credit_card_validator()
       book_validator = isbn_validator()

       cc_result = cc_validator(credit_card)
       isbn_result = book_validator(isbn)

       match (cc_result, isbn_result):
           case (Success(cc), Success(book)):
               return {
                   "status": "approved",
                   "message": "Purchase approved",
                   "payment": f"xxxx-xxxx-xxxx-{cc[-4:]}",
                   "product": book
               }
           case (Failure(error), _):
               return {
                   "status": "declined",
                   "reason": "payment",
                   "message": error
               }
           case (_, Failure(error)):
               return {
                   "status": "declined",
                   "reason": "product",
                   "message": error
               }

   # Test with valid values
   purchase_result = validate_purchase(
       "4111 1111 1111 1111",  # Valid test number
       "978-3-16-148410-0"     # Valid ISBN-13
   )
   print(f"Purchase status: {purchase_result['status']}")

   # Test with invalid values
   purchase_result = validate_purchase(
       "4111 1111 1111 1112",  # Invalid number
       "978-3-16-148410-0"     # Valid ISBN-13
   )
   print(f"Purchase status: {purchase_result['status']}")
   print(f"Reason: {purchase_result['reason']}")
   print(f"Message: {purchase_result['message']}")

Creating Stateful Validators
----------------------------

Validators that maintain state or depend on external resources:

.. code-block:: python

   from valid8r import Maybe, validators
   from valid8r.core.maybe import Success, Failure

   # Validator that ensures uniqueness within a session
   class UniqueValidator:
       def __init__(self, error_message=None):
           self.seen_values = set()
           self.error_message = error_message or "Value must be unique"

       def __call__(self, value):
           if value in self.seen_values:
               return Maybe.failure(self.error_message)
           self.seen_values.add(value)
           return Maybe.success(value)

       def reset(self):
           self.seen_values.clear()

   # Use stateful validators with pattern matching
   def register_usernames(usernames):
       is_unique = UniqueValidator("This username has already been registered")

       registered = []
       errors = []

       for i, username in enumerate(usernames):
           result = is_unique(username)
           match result:
               case Success(value):
                   registered.append(value)
               case Failure(error):
                   errors.append({"index": i, "username": username, "error": error})

       return {
           "registered": registered,
           "errors": errors,
           "success_count": len(registered),
           "error_count": len(errors)
       }

   # Test with a list of usernames
   result = register_usernames(["alice", "bob", "charlie", "alice", "david", "bob"])
   print(f"Registered {result['success_count']} users:")
   for user in result["registered"]:
       print(f"  - {user}")

   print(f"Encountered {result['error_count']} errors:")
   for error in result["errors"]:
       print(f"  - {error['username']}: {error['error']}")

In the next section, we'll explore interactive prompting techniques with validation.
