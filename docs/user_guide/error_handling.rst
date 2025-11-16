Error Handling
==============

Valid8r provides structured error handling through the ``ValidationError`` dataclass and ``ErrorCode`` constants. This enables programmatic error handling, machine-readable error responses, and better debugging for validation failures.

Why Structured Errors?
----------------------

Traditional error handling with plain strings makes it difficult to:

* **Handle errors programmatically**: You can't easily distinguish between different error types
* **Build API responses**: Converting errors to JSON requires manual parsing
* **Track error locations**: No standard way to identify which field failed
* **Provide debugging context**: Limited ability to include validation parameters

Valid8r's structured errors solve these problems while maintaining backward compatibility with string-based errors.

ValidationError Dataclass
-------------------------

The ``ValidationError`` dataclass provides a comprehensive error representation:

.. code-block:: python

   from valid8r.core.errors import ValidationError

   error = ValidationError(
       code='INVALID_EMAIL',
       message='Email address format is invalid',
       path='.user.email',
       context={'input': 'not-an-email'}
   )

**Attributes:**

* ``code`` (str): Machine-readable error code (e.g., ``'INVALID_EMAIL'``, ``'OUT_OF_RANGE'``)
* ``message`` (str): Human-readable error message describing the failure
* ``path`` (str): JSON path to the failed field (e.g., ``'.user.email'``, ``'.items[0].name'``)
* ``context`` (dict | None): Additional debugging information (e.g., ``{'min': 0, 'max': 100, 'value': 150}``)

**Methods:**

* ``__str__()``: Returns human-readable format (``'path: message'`` or just ``'message'``)
* ``to_dict()``: Converts error to dictionary for JSON serialization

ErrorCode Constants
-------------------

The ``ErrorCode`` class provides standard error codes organized by category:

.. code-block:: python

   from valid8r.core.errors import ErrorCode

   # Use predefined constants
   error = ValidationError(
       code=ErrorCode.INVALID_EMAIL,
       message='Email address format is invalid'
   )

**Available Error Codes:**

**Parsing Errors:**

* ``INVALID_TYPE`` - Type conversion failed (e.g., string to int)
* ``INVALID_FORMAT`` - Input format does not match expected pattern
* ``PARSE_ERROR`` - General parsing failure

**Numeric Validators:**

* ``OUT_OF_RANGE`` - Value is outside the allowed range
* ``BELOW_MINIMUM`` - Value is below the minimum allowed value
* ``ABOVE_MAXIMUM`` - Value is above the maximum allowed value

**String Validators:**

* ``TOO_SHORT`` - String length is below minimum
* ``TOO_LONG`` - String length exceeds maximum
* ``PATTERN_MISMATCH`` - String does not match required regex pattern
* ``EMPTY_STRING`` - String is empty when a value is required

**Collection Validators:**

* ``NOT_IN_SET`` - Value is not in the allowed set
* ``DUPLICATE_ITEMS`` - Collection contains duplicate items
* ``INVALID_SUBSET`` - Collection is not a valid subset

**Network Validators:**

* ``INVALID_EMAIL`` - Email address format is invalid
* ``INVALID_URL`` - URL format is invalid
* ``INVALID_IP`` - IP address format is invalid
* ``INVALID_PHONE`` - Phone number format is invalid

**Filesystem Validators:**

* ``PATH_NOT_FOUND`` - File or directory path does not exist
* ``NOT_A_FILE`` - Path exists but is not a file
* ``NOT_A_DIRECTORY`` - Path exists but is not a directory
* ``FILE_TOO_LARGE`` - File size exceeds maximum allowed size

**DoS Protection:**

* ``INPUT_TOO_LONG`` - Input exceeds maximum length (DoS protection)

**Generic:**

* ``CUSTOM_ERROR`` - User-defined custom validation error
* ``VALIDATION_ERROR`` - Generic validation failure

Creating Failure with ValidationError
--------------------------------------

The ``Failure`` type now accepts both string errors (backward compatible) and ``ValidationError`` instances:

.. code-block:: python

   from valid8r import Maybe
   from valid8r.core.maybe import Success, Failure
   from valid8r.core.errors import ValidationError, ErrorCode

   # Old way (still works): plain string error
   failure = Maybe.failure('Email address format is invalid')

   # New way: structured error with code
   error = ValidationError(
       code=ErrorCode.INVALID_EMAIL,
       message='Email address format is invalid',
       path='.user.email',
       context={'input': 'not-an-email'}
   )
   failure = Maybe.failure(error)

   # Access the structured error
   match failure:
       case Failure(error_msg):
           # Pattern matching still works with message string
           print(error_msg)  # 'Email address format is invalid'

Accessing Structured Error Information
---------------------------------------

Use the ``error_detail()`` method or ``validation_error`` property to access the full structured error:

.. code-block:: python

   from valid8r import Maybe
   from valid8r.core.maybe import Failure
   from valid8r.core.errors import ValidationError, ErrorCode

   error = ValidationError(
       code=ErrorCode.OUT_OF_RANGE,
       message='Value must be between 0 and 100',
       path='.user.age',
       context={'value': 150, 'min': 0, 'max': 100}
   )
   failure = Maybe.failure(error)

   # Access structured error details using error_detail() (RFC-001 Phase 2)
   match failure:
       case Failure():
           detail = failure.error_detail()
           print(f"Code: {detail.code}")              # Code: OUT_OF_RANGE
           print(f"Message: {detail.message}")        # Message: Value must be between 0 and 100
           print(f"Path: {detail.path}")              # Path: .user.age
           print(f"Context: {detail.context}")        # Context: {'value': 150, 'min': 0, 'max': 100}

   # Alternative: use validation_error property (also available)
   match failure:
       case Failure():
           ve = failure.validation_error
           print(f"Code: {ve.code}")              # Code: OUT_OF_RANGE
           print(f"Message: {ve.message}")        # Message: Value must be between 0 and 100
           print(f"Path: {ve.path}")              # Path: .user.age
           print(f"Context: {ve.context}")        # Context: {'value': 150, 'min': 0, 'max': 100}

Programmatic Error Handling
----------------------------

Use error codes to handle different validation failures programmatically:

.. code-block:: python

   from valid8r import parsers
   from valid8r.core.maybe import Success, Failure
   from valid8r.core.errors import ErrorCode

   def process_email(email_str: str):
       result = parsers.parse_email(email_str)

       match result:
           case Success(email):
               return f"Valid email: {email.local}@{email.domain}"

           case Failure():
               # Access structured error for programmatic handling
               error = result.error_detail()

               # Different handling based on error code
               match error.code:
                   case ErrorCode.INVALID_EMAIL:
                       return "Please enter a valid email address"
                   case ErrorCode.EMPTY_STRING:
                       return "Email is required"
                   case ErrorCode.INPUT_TOO_LONG:
                       return "Email is too long"
                   case _:
                       return f"Validation error: {error.message}"

   print(process_email("user@example.com"))  # Valid email: user@example.com
   print(process_email("not-an-email"))      # Please enter a valid email address
   print(process_email(""))                  # Email is required

Converting Errors to JSON
-------------------------

Use the ``to_dict()`` method to serialize errors for API responses:

.. code-block:: python

   from valid8r import parsers
   from valid8r.core.maybe import Failure
   import json

   def validate_api_request(data: dict) -> dict:
       """Validate API request and return JSON-serializable response."""
       age_result = parsers.parse_int(data.get('age', ''))

       match age_result:
           case Failure():
               error_dict = age_result.error_detail().to_dict()
               return {
                   'status': 'error',
                   'error': error_dict
               }
           case _:
               return {'status': 'success'}

   # Example with invalid data
   response = validate_api_request({'age': 'not-a-number'})
   print(json.dumps(response, indent=2))
   # {
   #   "status": "error",
   #   "error": {
   #     "code": "INVALID_TYPE",
   #     "message": "Input must be a valid integer",
   #     "path": "",
   #     "context": {}
   #   }
   # }

Pattern Matching with Structured Errors
----------------------------------------

Combine pattern matching with structured error codes for elegant error handling:

.. code-block:: python

   from valid8r import parsers, validators
   from valid8r.core.maybe import Success, Failure
   from valid8r.core.errors import ErrorCode

   def validate_age(age_str: str) -> str:
       result = parsers.parse_int(age_str).bind(
           validators.minimum(0) & validators.maximum(120)
       )

       match result:
           case Success(age) if age >= 18:
               return f"Adult: {age} years old"
           case Success(age):
               return f"Minor: {age} years old"
           case Failure() if result.error_detail().code == ErrorCode.INVALID_TYPE:
               return "Please enter a number"
           case Failure() if result.error_detail().code == ErrorCode.BELOW_MINIMUM:
               return "Age cannot be negative"
           case Failure() if result.error_detail().code == ErrorCode.ABOVE_MAXIMUM:
               return "Age seems unrealistic"
           case Failure(error):
               return f"Validation failed: {error}"

   print(validate_age("25"))        # Adult: 25 years old
   print(validate_age("10"))        # Minor: 10 years old
   print(validate_age("abc"))       # Please enter a number
   print(validate_age("-5"))        # Age cannot be negative
   print(validate_age("150"))       # Age seems unrealistic

Multi-Field Validation with Paths
----------------------------------

Use the ``path`` attribute to track which field failed in complex validations:

.. code-block:: python

   from valid8r import parsers, validators
   from valid8r.core.maybe import Success, Failure
   from valid8r.core.errors import ValidationError, ErrorCode

   def validate_user_data(data: dict) -> list[dict]:
       """Validate user data and return list of errors."""
       errors = []

       # Validate name
       name = data.get('name', '')
       if not name:
           errors.append(ValidationError(
               code=ErrorCode.EMPTY_STRING,
               message='Name is required',
               path='.name'
           ).to_dict())

       # Validate email
       email_result = parsers.parse_email(data.get('email', ''))
       match email_result:
           case Failure():
               error = email_result.error_detail()
               errors.append({
                   **error.to_dict(),
                   'path': '.email'  # Set field path
               })

       # Validate age
       age_result = parsers.parse_int(data.get('age', '')).bind(
           validators.minimum(0) & validators.maximum(120)
       )
       match age_result:
           case Failure():
               error = age_result.error_detail()
               errors.append({
                   **error.to_dict(),
                   'path': '.age'  # Set field path
               })

       return errors

   # Example with invalid data
   invalid_data = {
       'name': '',
       'email': 'not-an-email',
       'age': 'abc'
   }

   errors = validate_user_data(invalid_data)
   for error in errors:
       print(f"{error['path']}: {error['message']}")
   # .name: Name is required
   # .email: Email address format is invalid
   # .age: Input must be a valid integer

Backward Compatibility
----------------------

Structured errors maintain complete backward compatibility with string-based errors:

.. code-block:: python

   from valid8r import Maybe
   from valid8r.core.maybe import Success, Failure
   from valid8r.core.errors import ValidationError, ErrorCode

   # Old code using string errors still works
   failure = Maybe.failure('Something went wrong')

   match failure:
       case Failure(error):
           print(error)  # 'Something went wrong'

   # String errors are automatically wrapped in ValidationError
   match failure:
       case Failure():
           detail = failure.error_detail()
           print(detail.code)     # 'VALIDATION_ERROR'
           print(detail.message)  # 'Something went wrong'

   # New code can use structured errors
   structured_failure = Maybe.failure(
       ValidationError(code=ErrorCode.INVALID_EMAIL, message='Bad email')
   )

   # Pattern matching still works the same way
   match structured_failure:
       case Failure(error):
           print(error)  # 'Bad email'

   # Access structured details from any Failure
   match structured_failure:
       case Failure():
           detail = structured_failure.error_detail()
           print(detail.code)     # 'INVALID_EMAIL'
           print(detail.message)  # 'Bad email'

Migration Guide
---------------

Migrating existing code to use structured errors is optional and can be done incrementally:

**Step 1: Continue using string errors (no changes needed)**

Your existing code continues to work without any modifications:

.. code-block:: python

   # Existing code still works
   result = Maybe.failure('Email format is invalid')

**Step 2: Add structured errors to new code**

Start using ``ValidationError`` in new parsers and validators:

.. code-block:: python

   from valid8r.core.errors import ValidationError, ErrorCode

   # New code with structured errors
   error = ValidationError(
       code=ErrorCode.INVALID_EMAIL,
       message='Email format is invalid'
   )
   result = Maybe.failure(error)

**Step 3: Use programmatic error handling where needed**

Take advantage of error codes in specific places where you need programmatic handling using ``error_detail()``:

.. code-block:: python

   match result:
       case Failure() if result.error_detail().code == ErrorCode.INVALID_EMAIL:
           # Handle email errors specifically
           send_email_format_help()
       case Failure(error):
           # Generic error handling
           log_error(error)

**Step 4: Convert errors to JSON for APIs**

Use ``error_detail().to_dict()`` for API responses without changing your validation logic:

.. code-block:: python

   match result:
       case Failure():
           return {
               'status': 'error',
               'error': result.error_detail().to_dict()
           }

Best Practices
--------------

**Use ErrorCode Constants**

Always use ``ErrorCode`` constants instead of hardcoded strings:

.. code-block:: python

   # Good: Use constants
   error = ValidationError(code=ErrorCode.INVALID_EMAIL, message='Bad email')

   # Bad: Hardcoded string
   error = ValidationError(code='INVALID_EMAIL', message='Bad email')

**Provide Context for Debugging**

Include validation parameters in the context for better debugging:

.. code-block:: python

   # Good: Include context
   error = ValidationError(
       code=ErrorCode.OUT_OF_RANGE,
       message='Value must be between 0 and 100',
       context={'value': 150, 'min': 0, 'max': 100}
   )

   # OK: No context (when not needed)
   error = ValidationError(
       code=ErrorCode.INVALID_EMAIL,
       message='Email format is invalid'
   )

**Set Paths for Multi-Field Validation**

Always set the ``path`` attribute when validating multiple fields:

.. code-block:: python

   # Good: Set path
   error = ValidationError(
       code=ErrorCode.INVALID_EMAIL,
       message='Email format is invalid',
       path='.user.email'
   )

   # OK: No path for single-field validation
   error = ValidationError(
       code=ErrorCode.INVALID_EMAIL,
       message='Email format is invalid'
   )

**Keep Error Messages User-Friendly**

Write messages for end users, not developers:

.. code-block:: python

   # Good: User-friendly message
   error = ValidationError(
       code=ErrorCode.INVALID_EMAIL,
       message='Please enter a valid email address'
   )

   # Bad: Technical jargon
   error = ValidationError(
       code=ErrorCode.INVALID_EMAIL,
       message='Regex pattern match failed for email validation'
   )

Next Steps
----------

Now that you understand structured error handling, you can:

* Use :doc:`parsers </user_guide/parsers>` that return structured errors
* Build :doc:`custom validators </user_guide/validators>` with error codes
* Create robust :doc:`API integrations </user_guide/advanced_usage>` with JSON error responses
* See practical examples in the :doc:`examples section </examples/basic_example>`
