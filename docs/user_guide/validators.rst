Validators
==========

Validators are functions that check if values meet specific criteria. In Valid8r, all validators follow the same pattern - they take a value and return a Maybe object that either contains the validated value or an error message.

Basic Usage
-----------

.. code-block:: python

   from valid8r import validators
   from valid8r.core.maybe import Success, Failure

   # Validate a value is greater than or equal to 0
   result = validators.minimum(0)(42)
   match result:
       case Success(value):
           print(f"Valid value: {value}")  # Valid value: 42
       case Failure(error):
           print(f"Error: {error}")

   # Validate a value is within a range
   result = validators.between(1, 100)(42)
   match result:
       case Success(value):
           print(f"Valid value in range: {value}")  # Valid value in range: 42
       case Failure(error):
           print(f"Error: {error}")

Built-in Validators
-------------------

Valid8r includes several built-in validators:

Minimum Validator
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from valid8r import validators
   from valid8r.core.maybe import Success, Failure

   # Basic usage
   result = validators.minimum(0)(42)
   match result:
       case Success(value):
           print(value)  # 42
       case Failure(_):
           print("This won't happen")

   # With custom error message
   result = validators.minimum(0, "Value must be non-negative")(42)
   match result:
       case Success(value):
           print(value)  # 42
       case Failure(_):
           print("This won't happen")

   # Failed validation
   result = validators.minimum(0)(-42)
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "Value must be at least 0"

Maximum Validator
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from valid8r import validators
   from valid8r.core.maybe import Success, Failure

   # Basic usage
   result = validators.maximum(100)(42)
   match result:
       case Success(value):
           print(value)  # 42
       case Failure(_):
           print("This won't happen")

   # With custom error message
   result = validators.maximum(100, "Value must not exceed 100")(42)
   match result:
       case Success(value):
           print(value)  # 42
       case Failure(_):
           print("This won't happen")

   # Failed validation
   result = validators.maximum(100)(142)
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "Value must be at most 100"

Between Validator
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from valid8r import validators
   from valid8r.core.maybe import Success, Failure

   # Basic usage
   result = validators.between(1, 100)(42)
   match result:
       case Success(value):
           print(value)  # 42
       case Failure(_):
           print("This won't happen")

   # With custom error message
   result = validators.between(
       1, 100, "Value must be between 1 and 100 inclusive"
   )(42)
   match result:
       case Success(value):
           print(value)  # 42
       case Failure(_):
           print("This won't happen")

   # Failed validation
   result = validators.between(1, 100)(142)
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "Value must be between 1 and 100"

Length Validator
~~~~~~~~~~~~~~~~

.. code-block:: python

   from valid8r import validators
   from valid8r.core.maybe import Success, Failure

   # Validate string length
   result = validators.length(3, 10)("hello")
   match result:
       case Success(value):
           print(value)  # "hello"
       case Failure(_):
           print("This won't happen")

   # Failed validation - too short
   result = validators.length(3, 10)("hi")
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "String length must be between 3 and 10"

   # Failed validation - too long
   result = validators.length(3, 10)("hello world")
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "String length must be between 3 and 10"

Predicate Validator
~~~~~~~~~~~~~~~~~~~

The most flexible validator is the predicate validator, which uses a custom function:

.. code-block:: python

   from valid8r import validators
   from valid8r.core.maybe import Success, Failure

   # Validate that a number is even
   is_even = validators.predicate(
       lambda x: x % 2 == 0,
       "Number must be even"
   )

   result = is_even(42)  # Valid
   match result:
       case Success(value):
           print(value)  # 42
       case Failure(_):
           print("This won't happen")

   result = is_even(43)  # Invalid
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "Number must be even"

   # More complex example - validate email format
   import re

   def is_valid_email(email):
       pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
       return bool(re.match(pattern, email))

   email_validator = validators.predicate(
       is_valid_email,
       "Invalid email format"
   )

   result = email_validator("user@example.com")  # Valid
   match result:
       case Success(value):
           print(value)  # "user@example.com"
       case Failure(_):
           print("This won't happen")

   result = email_validator("not-an-email")  # Invalid
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "Invalid email format"

Combining Validators
--------------------

One of the most powerful features of Valid8r is the ability to combine validators using logical operators:

.. code-block:: python

   from valid8r import validators
   from valid8r.core.maybe import Success, Failure

   # Create individual validators
   is_positive = validators.minimum(0, "Value must be positive")
   is_even = validators.predicate(
       lambda x: x % 2 == 0,
       "Value must be even"
   )
   under_hundred = validators.maximum(100, "Value must be under 100")

   # AND operator (&) - both validators must pass
   positive_and_even = is_positive & is_even

   result = positive_and_even(42)  # Valid
   match result:
       case Success(value):
           print(f"Valid positive even number: {value}")  # Valid positive even number: 42
       case Failure(_):
           print("This won't happen")

   result = positive_and_even(-2)  # Invalid - not positive
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(f"Error: {error}")  # Error: Value must be positive

   result = positive_and_even(43)  # Invalid - not even
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(f"Error: {error}")  # Error: Value must be even

   # OR operator (|) - at least one validator must pass
   even_or_under_hundred = is_even | under_hundred

   result = even_or_under_hundred(42)   # Valid - even
   match result:
       case Success(value):
           print(f"Valid: {value}")  # Valid: 42
       case Failure(_):
           print("This won't happen")

   result = even_or_under_hundred(99)   # Valid - under 100
   match result:
       case Success(value):
           print(f"Valid: {value}")  # Valid: 99
       case Failure(_):
           print("This won't happen")

   result = even_or_under_hundred(102)  # Invalid - neither even nor under 100
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(f"Error: {error}")  # Error: Value must be under 100

   # NOT operator (~) - negate a validator
   is_odd = ~is_even

   result = is_odd(43)  # Valid
   match result:
       case Success(value):
           print(f"Valid odd number: {value}")  # Valid odd number: 43
       case Failure(_):
           print("This won't happen")

   result = is_odd(42)  # Invalid
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(f"Error: {error}")  # Error: Negated validation failed

   # Complex combinations
   valid_number = is_positive & (is_even | under_hundred)

   result = valid_number(42)   # Valid - positive and even
   match result:
       case Success(value):
           print(f"Valid: {value}")  # Valid: 42
       case Failure(_):
           print("This won't happen")

   result = valid_number(99)   # Valid - positive and under 100
   match result:
       case Success(value):
           print(f"Valid: {value}")  # Valid: 99
       case Failure(_):
           print("This won't happen")

   result = valid_number(-2)   # Invalid - not positive
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(f"Error: {error}")  # Error: Value must be positive

   result = valid_number(102)  # Valid - positive and even
   match result:
       case Success(value):
           print(f"Valid: {value}")  # Valid: 102 (positive and even)
       case Failure(_):
           print("This won't happen")

Error Messages in Combined Validators
-------------------------------------

When validators are combined, error messages follow these rules:

1. For AND combinations, the first failed validator's error message is used
2. For OR combinations, the last failed validator's error message is used
3. For NOT combinations, the default error is "Negated validation failed" unless a custom message is provided

Custom Validators
-----------------

You can create your own validators by following the validator pattern:

.. code-block:: python

   from valid8r import Maybe, validators
   from valid8r.core.maybe import Success, Failure

   # Create a validator for divisibility
   def divisible_by(divisor, error_message=None):
       def validator(value):
           if value % divisor == 0:
               return Maybe.success(value)
           return Maybe.failure(
               error_message or f"Value must be divisible by {divisor}"
           )
       return validators.Validator(validator)

   # Use the custom validator
   is_divisible_by_3 = divisible_by(3)
   result = is_divisible_by_3(9)  # Valid
   match result:
       case Success(value):
           print(f"Valid: {value}")  # Valid: 9
       case Failure(_):
           print("This won't happen")

   result = is_divisible_by_3(10)  # Invalid
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(f"Error: {error}")  # Error: Value must be divisible by 3

   # Combine with other validators
   valid_number = validators.minimum(0) & divisible_by(3)

   result = valid_number(9)  # Valid
   match result:
       case Success(value):
           print(f"Valid: {value}")  # Valid: 9
       case Failure(_):
           print("This won't happen")

Use with Parsers
----------------

Validators are often used with parsers to create a complete validation pipeline:

.. code-block:: python

   from valid8r import parsers, validators
   from valid8r.core.maybe import Success, Failure

   # Parse a string to an integer, then validate it's positive and even
   is_positive = validators.minimum(0)
   is_even = validators.predicate(lambda x: x % 2 == 0, "Value must be even")

   valid_number = is_positive & is_even

   result = parsers.parse_int("42").bind(lambda x: valid_number(x))

   match result:
       case Success(value):
           print(f"Valid input: {value}")  # Valid input: 42
       case Failure(error):
           print(f"Invalid input: {error}")

   # Test with invalid input
   result = parsers.parse_int("-2").bind(lambda x: valid_number(x))
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(f"Invalid input: {error}")  # Invalid input: Value must be at least 0

Processing Validation Results
-----------------------------

Using pattern matching to handle different validation scenarios:

.. code-block:: python

   from valid8r import validators
   from valid8r.core.maybe import Success, Failure

   # Define a function to process validation results
   def process_validation(result, context_name):
       match result:
           case Success(value):
               return f"{context_name} is valid: {value}"
           case Failure(error) if "minimum" in error:
               return f"{context_name} is too small: {error}"
           case Failure(error) if "maximum" in error:
               return f"{context_name} is too large: {error}"
           case Failure(error):
               return f"{context_name} is invalid: {error}"

   # Use with different validations
   age_validator = validators.between(0, 120)

   print(process_validation(age_validator(25), "Age"))  # Age is valid: 25
   print(process_validation(age_validator(-5), "Age"))  # Age is too small: Value must be at least 0
   print(process_validation(age_validator(130), "Age"))  # Age is too large: Value must be at most 120

Validator Limitations and Edge Cases
------------------------------------

Here are some important things to know about validators:

1. **Type compatibility**: Validators assume the input is of the correct type. For example, `minimum(0)` expects a numeric type that can be compared with 0.

2. **Comparison operators**: Validators rely on standard Python comparison operators like `<`, `>`, `<=`, `>=`, etc. This means they work best with built-in Python types with well-defined comparison behavior.

3. **Chaining behavior**: When chaining validators, keep in mind that they are evaluated left-to-right with short-circuit behavior.

4. **Error messages**: While combining validators, only one error message is returned - either the first failing validator in an AND chain or the last failing validator in an OR chain.

5. **Custom validators**: Custom validators should always return a `Maybe` for consistency with the rest of the library.

In the next section, we'll explore how to use Valid8r's prompt module to ask users for input with built-in validation.
