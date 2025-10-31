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

Matches Regex Validator
~~~~~~~~~~~~~~~~~~~~~~~

Validate that a string matches a regular expression pattern:

.. code-block:: python

   from valid8r import validators
   from valid8r.core.maybe import Success, Failure
   import re

   # Basic usage with string pattern
   ssn_validator = validators.matches_regex(r'^\d{3}-\d{2}-\d{4}$')

   result = ssn_validator("123-45-6789")  # Valid
   match result:
       case Success(value):
           print(value)  # "123-45-6789"
       case Failure(_):
           print("This won't happen")

   result = ssn_validator("123456789")  # Invalid
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "Value must match pattern ^\d{3}-\d{2}-\d{4}$"

   # With compiled regex pattern
   pattern = re.compile(r'^[A-Z]{2}\d{4}$')
   code_validator = validators.matches_regex(pattern)

   result = code_validator("AB1234")  # Valid
   match result:
       case Success(value):
           print(value)  # "AB1234"
       case Failure(_):
           print("This won't happen")

   # With custom error message
   email_validator = validators.matches_regex(
       r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
       error_message="Invalid email format"
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

In Set Validator
~~~~~~~~~~~~~~~~

Validate that a value is in a set of allowed values:

.. code-block:: python

   from valid8r import validators
   from valid8r.core.maybe import Success, Failure

   # Basic usage
   color_validator = validators.in_set({'red', 'green', 'blue'})

   result = color_validator("red")  # Valid
   match result:
       case Success(value):
           print(value)  # "red"
       case Failure(_):
           print("This won't happen")

   result = color_validator("yellow")  # Invalid
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "Value must be one of: blue, green, red"

   # With custom error message
   size_validator = validators.in_set(
       {'S', 'M', 'L', 'XL'},
       error_message="Size must be S, M, L, or XL"
   )

   result = size_validator("XXL")  # Invalid
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "Size must be S, M, L, or XL"

Non-Empty String Validator
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Validate that a string is not empty or whitespace-only:

.. code-block:: python

   from valid8r import validators
   from valid8r.core.maybe import Success, Failure

   # Basic usage
   name_validator = validators.non_empty_string()

   result = name_validator("Alice")  # Valid
   match result:
       case Success(value):
           print(value)  # "Alice"
       case Failure(_):
           print("This won't happen")

   result = name_validator("")  # Invalid - empty string
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "String must not be empty"

   result = name_validator("   ")  # Invalid - whitespace only
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "String must not be empty"

   # With custom error message
   username_validator = validators.non_empty_string("Username is required")

   result = username_validator("")  # Invalid
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "Username is required"

Unique Items Validator
~~~~~~~~~~~~~~~~~~~~~~

Validate that all items in a list are unique:

.. code-block:: python

   from valid8r import validators
   from valid8r.core.maybe import Success, Failure

   # Basic usage
   unique_validator = validators.unique_items()

   result = unique_validator([1, 2, 3, 4, 5])  # Valid
   match result:
       case Success(value):
           print(value)  # [1, 2, 3, 4, 5]
       case Failure(_):
           print("This won't happen")

   result = unique_validator([1, 2, 2, 3, 4])  # Invalid - duplicate 2
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "All items must be unique"

   # With custom error message
   tag_validator = validators.unique_items("Tags must not contain duplicates")

   result = tag_validator(["python", "valid8r", "python"])  # Invalid
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "Tags must not contain duplicates"

Subset Of Validator
~~~~~~~~~~~~~~~~~~~

Validate that a set is a subset of allowed values:

.. code-block:: python

   from valid8r import validators
   from valid8r.core.maybe import Success, Failure

   # Basic usage
   allowed_tags = {'python', 'javascript', 'typescript', 'rust', 'go'}
   tag_validator = validators.subset_of(allowed_tags)

   result = tag_validator({'python', 'rust'})  # Valid
   match result:
       case Success(value):
           print(value)  # {'python', 'rust'}
       case Failure(_):
           print("This won't happen")

   result = tag_validator({'python', 'java', 'c++'})  # Invalid
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "Value must be a subset of: go, javascript, python, rust, typescript"

   # With custom error message
   permissions_validator = validators.subset_of(
       {'read', 'write', 'delete'},
       error_message="Invalid permissions specified"
   )

   result = permissions_validator({'read', 'execute'})  # Invalid
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "Invalid permissions specified"

Superset Of Validator
~~~~~~~~~~~~~~~~~~~~~

Validate that a set is a superset of required values:

.. code-block:: python

   from valid8r import validators
   from valid8r.core.maybe import Success, Failure

   # Basic usage
   required_fields = {'id', 'name', 'email'}
   fields_validator = validators.superset_of(required_fields)

   result = fields_validator({'id', 'name', 'email', 'phone'})  # Valid
   match result:
       case Success(value):
           print(value)  # {'id', 'name', 'email', 'phone'}
       case Failure(_):
           print("This won't happen")

   result = fields_validator({'id', 'name'})  # Invalid - missing 'email'
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "Value must be a superset of: email, id, name"

   # With custom error message
   features_validator = validators.superset_of(
       {'authentication', 'logging'},
       error_message="Must include authentication and logging features"
   )

   result = features_validator({'authentication'})  # Invalid
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "Must include authentication and logging features"

Is Sorted Validator
~~~~~~~~~~~~~~~~~~~

Validate that a list is sorted in ascending or descending order:

.. code-block:: python

   from valid8r import validators
   from valid8r.core.maybe import Success, Failure

   # Basic usage - ascending order
   sorted_validator = validators.is_sorted()

   result = sorted_validator([1, 2, 3, 4, 5])  # Valid
   match result:
       case Success(value):
           print(value)  # [1, 2, 3, 4, 5]
       case Failure(_):
           print("This won't happen")

   result = sorted_validator([3, 1, 4, 2, 5])  # Invalid
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "List must be sorted in ascending order"

   # Descending order (use keyword-only parameter)
   reverse_sorted_validator = validators.is_sorted(reverse=True)

   result = reverse_sorted_validator([5, 4, 3, 2, 1])  # Valid
   match result:
       case Success(value):
           print(value)  # [5, 4, 3, 2, 1]
       case Failure(_):
           print("This won't happen")

   result = reverse_sorted_validator([1, 2, 3])  # Invalid
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "List must be sorted in descending order"

   # With custom error message
   priority_validator = validators.is_sorted(
       reverse=True,
       error_message="Priorities must be in descending order"
   )

   result = priority_validator([10, 8, 5, 3])  # Valid
   match result:
       case Success(value):
           print(value)  # [10, 8, 5, 3]
       case Failure(_):
           print("This won't happen")

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
