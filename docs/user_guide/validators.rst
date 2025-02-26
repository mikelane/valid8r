Validators
==========

Validators are functions that check if values meet specific criteria. In Valid8r, all validators follow the same pattern - they take a value and return a Maybe object that either contains the validated value or an error message.

Basic Usage
-----------

.. code-block:: python

   from valid8r import validators

   # Validate a value is greater than or equal to 0
   result = validators.minimum(0)(42)
   if result.is_just():
       print(f"Valid value: {result.value()}")
   else:
       print(f"Error: {result.error()}")

   # Validate a value is within a range
   result = validators.between(1, 100)(42)
   if result.is_just():
       print(f"Valid value in range: {result.value()}")
   else:
       print(f"Error: {result.error()}")

Built-in Validators
-------------------

Valid8r includes several built-in validators:

Minimum Validator
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from valid8r import validators

   # Basic usage
   result = validators.minimum(0)(42)

   # With custom error message
   result = validators.minimum(0, "Value must be non-negative")(42)

   # Failed validation
   result = validators.minimum(0)(-42)
   print(result.error())  # "Value must be at least 0"

Maximum Validator
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from valid8r import validators

   # Basic usage
   result = validators.maximum(100)(42)

   # With custom error message
   result = validators.maximum(100, "Value must not exceed 100")(42)

   # Failed validation
   result = validators.maximum(100)(142)
   print(result.error())  # "Value must be at most 100"

Between Validator
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from valid8r import validators

   # Basic usage
   result = validators.between(1, 100)(42)

   # With custom error message
   result = validators.between(
       1, 100, "Value must be between 1 and 100 inclusive"
   )(42)

   # Failed validation
   result = validators.between(1, 100)(142)
   print(result.error())  # "Value must be between 1 and 100"

Length Validator
~~~~~~~~~~~~~~~~

.. code-block:: python

   from valid8r import validators

   # Validate string length
   result = validators.length(3, 10)("hello")

   # Failed validation - too short
   result = validators.length(3, 10)("hi")
   print(result.error())  # "String length must be between 3 and 10"

   # Failed validation - too long
   result = validators.length(3, 10)("hello world")
   print(result.error())  # "String length must be between 3 and 10"

Predicate Validator
~~~~~~~~~~~~~~~~~~~

The most flexible validator is the predicate validator, which uses a custom function:

.. code-block:: python

   from valid8r import validators

   # Validate that a number is even
   is_even = validators.predicate(
       lambda x: x % 2 == 0,
       "Number must be even"
   )

   result = is_even(42)  # Valid
   result = is_even(43)  # Invalid

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
   result = email_validator("not-an-email")      # Invalid

Combining Validators
--------------------

One of the most powerful features of Valid8r is the ability to combine validators using logical operators:

.. code-block:: python

   from valid8r import validators

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
   result = positive_and_even(-2)  # Invalid - not positive
   result = positive_and_even(43)  # Invalid - not even

   # OR operator (|) - at least one validator must pass
   even_or_under_hundred = is_even | under_hundred

   result = even_or_under_hundred(42)   # Valid - even
   result = even_or_under_hundred(99)   # Valid - under 100
   result = even_or_under_hundred(102)  # Invalid - neither even nor under 100

   # NOT operator (~) - negate a validator
   is_odd = ~is_even

   result = is_odd(43)  # Valid
   result = is_odd(42)  # Invalid

   # Complex combinations
   valid_number = is_positive & (is_even | under_hundred)

   result = valid_number(42)   # Valid - positive and even
   result = valid_number(99)   # Valid - positive and under 100
   result = valid_number(-2)   # Invalid - not positive
   result = valid_number(102)  # Valid - positive and even

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

   # Create a validator for divisibility
   def divisible_by(divisor, error_message=None):
       def validator(value):
           if value % divisor == 0:
               return Maybe.just(value)
           return Maybe.nothing(
               error_message or f"Value must be divisible by {divisor}"
           )
       return validators.Validator(validator)

   # Use the custom validator
   is_divisible_by_3 = divisible_by(3)
   result = is_divisible_by_3(9)  # Valid
   result = is_divisible_by_3(10)  # Invalid

   # Combine with other validators
   valid_number = validators.minimum(0) & divisible_by(3)

Use with Parsers
----------------

Validators are often used with parsers to create a complete validation pipeline:

.. code-block:: python

   from valid8r import parsers, validators

   # Parse a string to an integer, then validate it's positive and even
   is_positive = validators.minimum(0)
   is_even = validators.predicate(lambda x: x % 2 == 0, "Value must be even")

   valid_number = is_positive & is_even

   result = parsers.parse_int("42").bind(lambda x: valid_number(x))

   if result.is_just():
       print(f"Valid input: {result.value()}")
   else:
       print(f"Invalid input: {result.error()}")

Validator Limitations and Edge Cases
------------------------------------

Here are some important things to know about validators:

1. **Type compatibility**: Validators assume the input is of the correct type. For example, `minimum(0)` expects a numeric type that can be compared with 0.

2. **Comparison operators**: Validators rely on standard Python comparison operators like `<`, `>`, `<=`, `>=`, etc. This means they work best with built-in Python types with well-defined comparison behavior.

3. **Chaining behavior**: When chaining validators, keep in mind that they are evaluated left-to-right with short-circuit behavior.

4. **Error messages**: While combining validators, only one error message is returned - either the first failing validator in an AND chain or the last failing validator in an OR chain.

5. **Custom validators**: Custom validators should always return a `Maybe` for consistency with the rest of the library.

In the next section, we'll explore how to use Valid8r's prompt module to ask users for input with built-in validation.