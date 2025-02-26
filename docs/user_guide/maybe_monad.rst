Understanding the Maybe Monad
=============================

The Maybe monad is a functional programming concept that provides a clean way to handle operations that might fail, without using exceptions for control flow. In Valid8r, the Maybe monad is the foundation for handling potential errors during parsing and validation.

Basic Concepts
--------------

The Maybe monad has two states:

1. **Just**: Represents a successful computation with a value.
2. **Nothing**: Represents a failed computation with an error message.

This pattern allows for:

* Clearer error handling without exceptions
* Chaining operations that might fail
* Propagating errors through a chain of operations
* Better type safety

Creating Maybe Instances
------------------------

.. code-block:: python

   from valid8r import Maybe

   # Success case
   success = Maybe.just(42)

   # Failure case
   failure = Maybe.nothing("Invalid input")

Checking Maybe Status
---------------------

.. code-block:: python

   # Check if it's a success
   if success.is_just():
       # Safe to access the value
       value = success.value()

   # Check if it's a failure
   if failure.is_nothing():
       # Safe to access the error
       error_message = failure.error()

Extracting Values Safely
------------------------

.. code-block:: python

   # Safe extraction with a default value
   value = success.value_or(0)  # Returns 42
   value = failure.value_or(0)  # Returns 0 (the default)

   # Unsafe extraction (will raise ValueError if called on the wrong state)
   try:
       value = success.value()    # Works
       value = failure.value()    # Raises ValueError
   except ValueError as e:
       print(f"Error: {e}")

   try:
       error = success.error()    # Raises ValueError
       error = failure.error()    # Works
   except ValueError as e:
       print(f"Error: {e}")

Chaining Operations with `bind`
-------------------------------

The most powerful feature of the Maybe monad is the ability to chain operations with the `bind` method:

.. code-block:: python

   # Define some functions that return Maybe
   def validate_positive(x):
       if x > 0:
           return Maybe.just(x)
       return Maybe.nothing("Value must be positive")

   def validate_even(x):
       if x % 2 == 0:
           return Maybe.just(x)
       return Maybe.nothing("Value must be even")

   # Chain validations
   result = Maybe.just(42).bind(validate_positive).bind(validate_even)
   print(result.is_just())  # True
   print(result.value())    # 42

   # If any step fails, the error is propagated
   result = Maybe.just(-2).bind(validate_positive).bind(validate_even)
   print(result.is_nothing())  # True
   print(result.error())       # "Value must be positive"

   result = Maybe.just(3).bind(validate_positive).bind(validate_even)
   print(result.is_nothing())  # True
   print(result.error())       # "Value must be even"

Transforming Values with `map`
------------------------------

The `map` method allows you to transform the value inside a Maybe without changing its state:

.. code-block:: python

   # Transform the value in a Just
   doubled = Maybe.just(21).map(lambda x: x * 2)
   print(doubled.value())  # 42

   # Nothing remains Nothing when mapped
   still_nothing = Maybe.nothing("Error").map(lambda x: x * 2)
   print(still_nothing.is_nothing())  # True
   print(still_nothing.error())      # "Error"

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

   if result.is_just():
       print(f"Valid value: {result.value()}")
   else:
       print(f"Error: {result.error()}")

Benefits of the Maybe monad approach:

1. **Explicit error handling**: The return type clearly indicates the possibility of failure
2. **No exceptions for control flow**: Errors are handled in a more functional way
3. **Composability**: Easy to chain multiple operations that might fail
4. **Self-documenting**: The code makes it clear that a function might fail
5. **Consistent error handling**: All errors are handled in a uniform way

Advanced Usage
--------------

**Custom error messages:**

.. code-block:: python

   from valid8r import parsers

   # Customize error message
   result = parsers.parse_int("abc", error_message="Please enter a number")
   print(result.error())  # "Please enter a number"

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
   if result.is_just():
       print(f"Valid input: {result.value()}")
   else:
       print(f"Invalid input: {result.error()}")

In the next section, we'll explore the available parsers for converting strings to various data types.