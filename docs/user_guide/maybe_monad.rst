Understanding the Maybe Monad
=============================

The Maybe monad is a functional programming concept that provides a clean way to handle operations that might fail, without using exceptions for control flow. In Valid8r, the Maybe monad is the foundation for handling potential errors during parsing and validation.

Basic Concepts
--------------

The Maybe monad has two states:

1. **Success**: Represents a successful computation with a value.
2. **Failure**: Represents a failed computation with an error message.

This pattern allows for:

* Clearer error handling without exceptions
* Chaining operations that might fail
* Propagating errors through a chain of operations
* Better type safety
* Elegant pattern matching with Python's match statement

Creating Maybe Instances
------------------------

.. code-block:: python

   from valid8r import Maybe

   # Success case
   success = Maybe.success(42)

   # Failure case
   failure = Maybe.failure("Invalid input")

Checking Maybe Status
---------------------

.. code-block:: python

   # Check if it's a success
   if success.is_success():
       # Safe to access the value
       value = success.value_or(0)

   # Check if it's a failure
   if failure.is_failure():
       # Safe to access the error
       error_message = failure.error_or("")

Extracting Values and Errors
----------------------------

.. code-block:: python

   # Safe extraction with a default value for Success
   value = success.value_or(0)  # Returns 42
   value = failure.value_or(0)  # Returns 0 (default), since this is a Failure

   # Safe extraction of error information
   err1 = failure.error_or("no error")  # Returns "Invalid input"
   err2 = success.error_or("no error")  # Returns the provided default for Success

   # Optional access to the error
   maybe_error = failure.get_error()  # "Invalid input"
   maybe_error_none = success.get_error()  # None

Pattern Matching with Match Statement
-------------------------------------

One of the most powerful features of the Maybe monad in Valid8r is its support for Python's match statement:

.. code-block:: python

   from valid8r.core.maybe import Success, Failure

   # Pattern matching with match statement
   def process_result(result):
       match result:
           case Success(value):
               return f"Success: got value {value}"
           case Failure(error):
               return f"Error: {error}"
           case _:
               return "Unknown result type"

   # Usage examples
   result1 = Maybe.success(42)
   print(process_result(result1))  # Success: got value 42

   result2 = Maybe.failure("Invalid input")
   print(process_result(result2))  # Error: Invalid input

Advanced Pattern Matching
-------------------------

You can use more complex pattern matching with guards for conditional logic:

.. code-block:: python

   def describe_result(result):
       match result:
           case Success(value) if value > 100:
               return f"Large value: {value}"
           case Success(value) if value % 2 == 0:
               return f"Even value: {value}"
           case Success(value):
               return f"Other value: {value}"
           case Failure(error) if "invalid" in error.lower():
               return f"Validation error: {error}"
           case Failure(error):
               return f"Other error: {error}"

   # Examples
   print(describe_result(Maybe.success(150)))  # Large value: 150
   print(describe_result(Maybe.success(42)))   # Even value: 42
   print(describe_result(Maybe.success(7)))    # Other value: 7
   print(describe_result(Maybe.failure("Invalid format")))  # Validation error: Invalid format
   print(describe_result(Maybe.failure("Timeout")))         # Other error: Timeout

Chaining Operations with `bind`
-------------------------------

The `bind` method allows you to chain operations that might fail:

.. code-block:: python

   # Define some functions that return Maybe
   def validate_positive(x):
       if x > 0:
           return Maybe.success(x)
       return Maybe.failure("Value must be positive")

   def validate_even(x):
       if x % 2 == 0:
           return Maybe.success(x)
       return Maybe.failure("Value must be even")

   # Chain validations
   result = Maybe.success(42).bind(validate_positive).bind(validate_even)

   match result:
       case Success(value):
           print(f"Valid value: {value}")  # Valid value: 42
       case Failure(error):
           print(f"Error: {error}")

   # If any step fails, the error is propagated
   result = Maybe.success(-2).bind(validate_positive).bind(validate_even)

   match result:
       case Success(value):
           print(f"Valid value: {value}")
       case Failure(error):
           print(f"Error: {error}")  # Error: Value must be positive

Transforming Values with `map`
------------------------------

The `map` method allows you to transform the value inside a Maybe without changing its state:

.. code-block:: python

   # Transform the value in a Success
   doubled = Maybe.success(21).map(lambda x: x * 2)

   match doubled:
       case Success(value):
           print(value)  # 42
       case _:
           print("This won't happen")

   # Failure remains Failure when mapped
   still_failure = Maybe.failure("Error").map(lambda x: x * 2)

   match still_failure:
       case Failure(error):
           print(error)  # Error
       case _:
           print("This won't happen")

Why Use the Maybe Monad?
------------------------

Let's compare traditional error handling with the Maybe monad approach:

**Traditional approach with exceptions:**

.. code-block:: python

   def parse_int_traditional(s):
       try:
           return int(s)
       except ValueError:
           raise ValueError("Invalid integer")

   def validate_positive_traditional(x):
       if x <= 0:
           raise ValueError("Must be positive")
       return x

   try:
       value = parse_int_traditional("42")
       validated = validate_positive_traditional(value)
       print(f"Valid value: {validated}")
   except ValueError as e:
       print(f"Error: {e}")

**Maybe monad approach:**

.. code-block:: python

   from valid8r import parsers, validators

   result = parsers.parse_int("42").bind(
       lambda x: validators.minimum(0)(x)
   )

   match result:
       case Success(value):
           print(f"Valid value: {value}")
       case Failure(error):
           print(f"Error: {error}")

Benefits of the Maybe monad approach:

1. **Explicit error handling**: The return type clearly indicates the possibility of failure
2. **No exceptions for control flow**: Errors are handled in a more functional way
3. **Composability**: Easy to chain multiple operations that might fail
4. **Self-documenting**: The code makes it clear that a function might fail
5. **Consistent error handling**: All errors are handled in a uniform way
6. **Pattern matching support**: Elegant handling of different cases with Python's match statement

Advanced Usage
--------------

**Custom error messages:**

.. code-block:: python

   from valid8r import parsers

   # Customize error message
   result = parsers.parse_int("abc", error_message="Please enter a number")

   match result:
       case Failure(error):
           print(error)  # "Please enter a number"
       case _:
           print("This won't happen")

**Handling complex chaining:**

.. code-block:: python

   from valid8r import Maybe, parsers, validators

   # Complex validation chain
   def validate_user_input(input_str):
       return (
           parsers.parse_int(input_str)
           .bind(lambda x: validators.minimum(1)(x))
           .bind(lambda x: validators.maximum(100)(x))
           .bind(lambda x: validators.predicate(
               lambda v: v % 2 == 0,
               "Number must be even"
           )(x))
       )

   result = validate_user_input("42")

   match result:
       case Success(value):
           print(f"Valid input: {value}")  # Valid input: 42
       case Failure(error):
           print(f"Invalid input: {error}")

   # Invalid input
   result = validate_user_input("43")

   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(f"Invalid input: {error}")  # Invalid input: Number must be even

In the next section, we'll explore the available parsers for converting strings to various data types.
