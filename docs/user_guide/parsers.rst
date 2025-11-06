Parsers
=======

Parsers are functions that convert string inputs into other data types, returning Maybe objects to handle potential parsing errors.

Basic Usage
-----------

.. code-block:: python

   from valid8r import parsers

   # Parse a string to an integer
   result = parsers.parse_int("42")
   match result:
       case Success(value):
           print(f"Parsed integer: {value}")  # Parsed integer: 42
       case Failure(error):
           print(f"Error: {error}")

   # Parse a string to a float
   result = parsers.parse_float("3.14")
   match result:
       case Success(value):
           print(f"Parsed float: {value}")  # Parsed float: 3.14
       case Failure(error):
           print(f"Error: {error}")

Available Parsers
-----------------

Valid8r includes parsers for several common data types:

Security Considerations
-----------------------

.. warning::
   All parsers include built-in DoS protection with early length validation.
   However, **always enforce application-level size limits** before parsing.
   See :doc:`/security/production-deployment` for framework-specific examples.

Parser Input Limits
~~~~~~~~~~~~~~~~~~~

Valid8r parsers reject oversized inputs to prevent resource exhaustion:

+------------------+------------+----------------------------------+
| Parser           | Max Length | Rationale                        |
+==================+============+==================================+
| parse_email()    | 254 chars  | RFC 5321 maximum                 |
+------------------+------------+----------------------------------+
| parse_phone()    | 100 chars  | NANP + international extensions  |
+------------------+------------+----------------------------------+
| parse_url()      | 2048 chars | Common browser URL limit         |
+------------------+------------+----------------------------------+
| parse_uuid()     | 36 chars   | Standard UUID format             |
+------------------+------------+----------------------------------+
| parse_ip()       | 45 chars   | IPv6 maximum length              |
+------------------+------------+----------------------------------+

.. seealso::
   - :doc:`/security/production-deployment` - Framework integration patterns
   - :doc:`/security/secure-parser-development` - Writing secure custom parsers

Integer Parser
~~~~~~~~~~~~~~

.. code-block:: python

   from valid8r import parsers
   from valid8r.core.maybe import Success, Failure

   # Basic usage
   result = parsers.parse_int("42")
   match result:
       case Success(value):
           print(value)  # 42
       case Failure(_):
           print("This won't happen")

   # Custom error message
   result = parsers.parse_int("abc", error_message="Please enter a valid number")
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "Please enter a valid number"

   # Handles whitespace
   result = parsers.parse_int("  42  ")
   match result:
       case Success(value):
           print(value)  # 42
       case Failure(_):
           print("This won't happen")

   # Parses integers with integer-equivalent float notation
   result = parsers.parse_int("42.0")
   match result:
       case Success(value):
           print(value)  # 42
       case Failure(_):
           print("This won't happen")

Float Parser
~~~~~~~~~~~~

.. code-block:: python

   from valid8r import parsers
   from valid8r.core.maybe import Success, Failure

   # Basic usage
   result = parsers.parse_float("3.14")
   match result:
       case Success(value):
           print(value)  # 3.14
       case Failure(_):
           print("This won't happen")

   # Scientific notation
   result = parsers.parse_float("1.23e-4")
   match result:
       case Success(value):
           print(value)  # 0.000123
       case Failure(_):
           print("This won't happen")

   # Handles whitespace
   result = parsers.parse_float("  3.14  ")
   match result:
       case Success(value):
           print(value)  # 3.14
       case Failure(_):
           print("This won't happen")

   # Integer as float
   result = parsers.parse_float("42")
   match result:
       case Success(value):
           print(value)  # 42.0
       case Failure(_):
           print("This won't happen")

Boolean Parser
~~~~~~~~~~~~~~

.. code-block:: python

   from valid8r import parsers
   from valid8r.core.maybe import Success, Failure

   # Parse various true values
   true_values = ["true", "True", "TRUE", "t", "T", "yes", "y", "1"]
   for value in true_values:
       result = parsers.parse_bool(value)
       match result:
           case Success(value):
               assert value is True  # All parse to True
           case Failure(_):
               print("This won't happen")

   # Parse various false values
   false_values = ["false", "False", "FALSE", "f", "F", "no", "n", "0"]
   for value in false_values:
       result = parsers.parse_bool(value)
       match result:
           case Success(value):
               assert value is False  # All parse to False
           case Failure(_):
               print("This won't happen")

   # Parse invalid boolean string
   result = parsers.parse_bool("maybe")
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "Input must be a valid boolean"

Date Parser
~~~~~~~~~~~

.. code-block:: python

   from valid8r import parsers
   from valid8r.core.maybe import Success, Failure
   from datetime import date

   # ISO format (default)
   result = parsers.parse_date("2023-01-15")
   match result:
       case Success(value):
           print(value)  # date(2023, 1, 15)
       case Failure(_):
           print("This won't happen")

   # Custom format
   result = parsers.parse_date("15/01/2023", date_format="%d/%m/%Y")
   match result:
       case Success(value):
           print(value)  # date(2023, 1, 15)
       case Failure(_):
           print("This won't happen")

   # Process date attributes
   result = parsers.parse_date("Jan 15, 2023", date_format="%b %d, %Y")
   match result:
       case Success(value):
           print(f"Year: {value.year}, Month: {value.month}, Day: {value.day}")
       case Failure(_):
           print("This won't happen")

Complex Number Parser
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from valid8r import parsers
   from valid8r.core.maybe import Success, Failure

   # Standard notation
   result = parsers.parse_complex("3+4j")
   match result:
       case Success(value):
           print(value)  # (3+4j)
       case Failure(_):
           print("This won't happen")

   # Alternative notation
   result = parsers.parse_complex("3+4i")
   match result:
       case Success(value):
           print(value)  # (3+4j)
       case Failure(_):
           print("This won't happen")

   # Just real part
   result = parsers.parse_complex("5")
   match result:
       case Success(value):
           print(value)  # (5+0j)
       case Failure(_):
           print("This won't happen")

   # Just imaginary part
   result = parsers.parse_complex("3j")
   match result:
       case Success(value):
           print(value)  # (0+3j)
       case Failure(_):
           print("This won't happen")

Decimal Parser
~~~~~~~~~~~~~~

The ``parse_decimal`` parser provides arbitrary-precision decimal arithmetic using Python's ``Decimal`` type, which avoids floating-point precision issues:

.. code-block:: python

   from valid8r import parsers
   from valid8r.core.maybe import Success, Failure
   from decimal import Decimal

   # Parse a decimal value
   result = parsers.parse_decimal("99.99")
   match result:
       case Success(value):
           print(value)  # Decimal('99.99')
           print(type(value))  # <class 'decimal.Decimal'>
       case Failure(_):
           print("This won't happen")

   # Precise decimal arithmetic (no floating-point errors)
   result = parsers.parse_decimal("0.1")
   match result:
       case Success(value):
           # With Decimal: 0.1 + 0.1 + 0.1 = 0.3 (exact)
           total = value + value + value
           print(total == Decimal('0.3'))  # True
       case Failure(_):
           print("This won't happen")

   # Compare with float precision issue
   float_result = 0.1 + 0.1 + 0.1
   print(float_result == 0.3)  # False (floating-point error)

   # Scientific notation support
   result = parsers.parse_decimal("1.23E-4")
   match result:
       case Success(value):
           print(value)  # Decimal('0.000123')
       case Failure(_):
           print("This won't happen")

   # Very large numbers with precision
   result = parsers.parse_decimal("123456789012345678901234567890.123456789")
   match result:
       case Success(value):
           print(value)  # Full precision maintained
       case Failure(_):
           print("This won't happen")

   # Use with financial calculations
   def calculate_total_with_tax(price_str: str, tax_rate_str: str):
       price_result = parsers.parse_decimal(price_str)
       tax_result = parsers.parse_decimal(tax_rate_str)

       match (price_result, tax_result):
           case (Success(price), Success(rate)):
               total = price * (Decimal('1') + rate)
               return f"Total: ${total:.2f}"
           case (Failure(error), _):
               return f"Invalid price: {error}"
           case (_, Failure(error)):
               return f"Invalid tax rate: {error}"

   print(calculate_total_with_tax("99.99", "0.0825"))  # Total: $108.24

Enum Parser
~~~~~~~~~~~

.. code-block:: python

   from enum import Enum
   from valid8r import parsers
   from valid8r.core.maybe import Success, Failure

   # Define an enum
   class Color(Enum):
       RED = "RED"
       GREEN = "GREEN"
       BLUE = "BLUE"

   # Parse to enum
   result = parsers.parse_enum("RED", Color)
   match result:
       case Success(value):
           print(value == Color.RED)  # True
       case Failure(_):
           print("This won't happen")

   # Invalid enum value
   result = parsers.parse_enum("YELLOW", Color)
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "Input must be a valid enumeration value"

UUID Parser
~~~~~~~~~~~

The ``parse_uuid`` parser converts string representations into UUID objects with optional version validation:

.. code-block:: python

   from valid8r import parsers
   from valid8r.core.maybe import Success, Failure
   from uuid import UUID

   # Parse a UUID string (any version)
   result = parsers.parse_uuid("550e8400-e29b-41d4-a716-446655440000")
   match result:
       case Success(uuid_obj):
           print(f"UUID: {uuid_obj}")
           print(f"Version: {uuid_obj.version}")  # Version: 4
       case Failure(error):
           print(f"Error: {error}")

   # Parse with version validation (strict mode - default)
   result = parsers.parse_uuid("550e8400-e29b-41d4-a716-446655440000", version=4)
   match result:
       case Success(uuid_obj):
           print(f"Valid UUID v4: {uuid_obj}")
       case Failure(_):
           print("This won't happen")

   # Version mismatch in strict mode
   result = parsers.parse_uuid("550e8400-e29b-41d4-a716-446655440000", version=1, strict=True)
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "UUID version mismatch: expected v1, got v4"

   # Non-strict mode allows version mismatch
   result = parsers.parse_uuid("550e8400-e29b-41d4-a716-446655440000", version=1, strict=False)
   match result:
       case Success(uuid_obj):
           print(f"Parsed UUID (ignoring version mismatch): {uuid_obj}")
       case Failure(_):
           print("This won't happen")

   # Supported UUID versions: 1, 3, 4, 5, 6, 7, 8
   result = parsers.parse_uuid("invalid-uuid")
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "Input must be a valid UUID"

   # Use case: Validating API identifiers
   def validate_resource_id(id_str: str):
       result = parsers.parse_uuid(id_str, version=4)
       match result:
           case Success(uuid_obj):
               return {"valid": True, "id": str(uuid_obj)}
           case Failure(error) if "version mismatch" in error:
               return {"valid": False, "error": "Must be a UUID v4"}
           case Failure(error):
               return {"valid": False, "error": error}

   print(validate_resource_id("550e8400-e29b-41d4-a716-446655440000"))
   # {'valid': True, 'id': '550e8400-e29b-41d4-a716-446655440000'}

Collection Type Parsing
-----------------------

Valid8r supports parsing strings into collection types like lists and dictionaries:

.. code-block:: python

   from valid8r import parsers
   from valid8r.core.maybe import Success, Failure

   # Parse a string to a list of integers
   result = parsers.parse_list("1,2,3", element_parser=parsers.parse_int)
   match result:
       case Success(value):
           print(f"Parsed list: {value}")  # Parsed list: [1, 2, 3]
       case Failure(error):
           print(f"Error: {error}")

   # Parse with custom separator
   result = parsers.parse_list("1|2|3", element_parser=parsers.parse_int, separator="|")
   match result:
       case Success(value):
           print(f"Parsed list: {value}")  # Parsed list: [1, 2, 3]
       case Failure(error):
           print(f"Error: {error}")

   # Parse a string to a dictionary
   result = parsers.parse_dict("name:John,age:30",
                               value_parser=parsers.parse_int)
   match result:
       case Success(value):
           print(f"Parsed dict: {value}")  # Parsed dict: {'name': 'John', 'age': 30}
       case Failure(error):
           print(f"Error: {error}")

   # Parse a set (removes duplicates)
   result = parsers.parse_set("1,2,3,2,1", element_parser=parsers.parse_int)
   match result:
       case Success(value):
           print(f"Parsed set: {value}")  # Parsed set: {1, 2, 3}
       case Failure(error):
           print(f"Error: {error}")

IP Address and CIDR Parsers
---------------------------

Valid8r provides built-in helpers for parsing IPv4, IPv6, generic IP addresses, and CIDR networks using Python's ``ipaddress``.

.. code-block:: python

   from valid8r.core.maybe import Success, Failure
   from valid8r import parsers

   # IPv4
   match parsers.parse_ipv4("192.168.0.1"):
       case Success(addr):
           print(addr)  # 192.168.0.1
       case Failure(error):
           print(error)

   # IPv6 (normalized to canonical form)
   match parsers.parse_ipv6("2001:db8:0:0:0:0:2:1"):
       case Success(addr):
           print(addr)  # 2001:db8::2:1
       case Failure(error):
           print(error)

   # Generic IP (either IPv4 or IPv6)
   match parsers.parse_ip("::1"):
       case Success(addr):
           print(type(addr), addr)  # <class 'ipaddress.IPv6Address'> ::1
       case Failure(error):
           print(error)

   # CIDR networks (strict by default)
   match parsers.parse_cidr("10.0.0.0/8"):
       case Success(net):
           print(net)  # 10.0.0.0/8
       case Failure(error):
           print(error)

   # Non-strict CIDR masks host bits instead of failing
   match parsers.parse_cidr("10.0.0.1/24", strict=False):
       case Success(net):
           print(net)  # 10.0.0.0/24
       case Failure(error):
           print(error)

Error messages are short and deterministic:

- "value must be a string" for non-string inputs
- "value is empty" for empty strings
- "not a valid IPv4 address" or "not a valid IPv6 address" for address-specific failures
- "not a valid IP address" for generic IP failures
- "not a valid network" for invalid CIDR/prefix formats
- "has host bits set" when strict CIDR parsing is enabled and input contains host bits

URL Parser with Structured Results
-----------------------------------

The ``parse_url`` parser validates and decomposes URLs into a structured ``UrlParts`` dataclass:

.. code-block:: python

   from valid8r import parsers
   from valid8r.core.maybe import Success, Failure

   # Parse a complete URL
   result = parsers.parse_url("https://user:pass@api.example.com:8080/v1/users?active=true#section")
   match result:
       case Success(url):
           print(f"Scheme: {url.scheme}")       # https
           print(f"Host: {url.host}")           # api.example.com
           print(f"Port: {url.port}")           # 8080
           print(f"Path: {url.path}")           # /v1/users
           print(f"Query: {url.query}")         # active=true
           print(f"Fragment: {url.fragment}")   # section
           print(f"Username: {url.username}")   # user
           print(f"Password: {url.password}")   # pass
       case Failure(error):
           print(f"Error: {error}")

   # Simple URL without credentials
   result = parsers.parse_url("https://example.com/page")
   match result:
       case Success(url):
           print(f"Clean URL: {url.scheme}://{url.host}{url.path}")
           # username and password are None
           print(url.username)  # None
       case Failure(_):
           print("This won't happen")

   # URL validation use case
   def validate_api_endpoint(url_str: str):
       result = parsers.parse_url(url_str)
       match result:
           case Success(url) if url.scheme in ('http', 'https'):
               return {"valid": True, "secure": url.scheme == 'https'}
           case Success(url):
               return {"valid": False, "error": f"Unsupported scheme: {url.scheme}"}
           case Failure(error):
               return {"valid": False, "error": error}

   print(validate_api_endpoint("https://api.example.com/users"))
   # {'valid': True, 'secure': True}

Email Parser with Structured Results
-------------------------------------

The ``parse_email`` parser validates email addresses and returns an ``EmailAddress`` dataclass with normalized components:

.. code-block:: python

   from valid8r import parsers
   from valid8r.core.maybe import Success, Failure

   # Parse an email address
   result = parsers.parse_email("User.Name+tag@Example.COM")
   match result:
       case Success(email):
           print(f"Local part: {email.local}")     # User.Name+tag (case preserved)
           print(f"Domain: {email.domain}")        # example.com (normalized lowercase)
           print(f"Full: {email.local}@{email.domain}")
       case Failure(error):
           print(f"Error: {error}")

   # Email validation for user registration
   def validate_registration_email(email_str: str):
       result = parsers.parse_email(email_str)
       match result:
           case Success(email) if email.domain in ('gmail.com', 'yahoo.com', 'outlook.com'):
               return {"valid": True, "provider": email.domain}
           case Success(email):
               return {"valid": True, "provider": "other"}
           case Failure(error):
               return {"valid": False, "error": error}

   print(validate_registration_email("user@gmail.com"))
   # {'valid': True, 'provider': 'gmail.com'}

   # Invalid email
   result = parsers.parse_email("not-an-email")
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "Invalid email format"

Phone Number Parser (North American)
-------------------------------------

The ``parse_phone`` parser handles North American Numbering Plan (NANP) phone numbers and returns a structured ``PhoneNumber`` dataclass:

.. code-block:: python

   from valid8r import parsers
   from valid8r.core.maybe import Success, Failure

   # Parse a formatted phone number
   result = parsers.parse_phone("(415) 555-2671")
   match result:
       case Success(phone):
           print(f"Area code: {phone.area_code}")      # 415
           print(f"Exchange: {phone.exchange}")        # 555
           print(f"Subscriber: {phone.subscriber}")    # 2671
           print(f"E.164 format: {phone.e164}")        # +14155552671
           print(f"National format: {phone.national}") # (415) 555-2671
       case Failure(error):
           print(f"Error: {error}")

   # Parse with extension
   result = parsers.parse_phone("415-555-2671 ext 123")
   match result:
       case Success(phone):
           print(f"Extension: {phone.extension}")  # 123
       case Failure(_):
           print("This won't happen")

   # Different input formats - all valid
   formats = [
       "(415) 555-2671",
       "415-555-2671",
       "415.555.2671",
       "4155552671",
       "+1 415 555 2671",
       "+1-415-555-2671"
   ]

   for fmt in formats:
       result = parsers.parse_phone(fmt)
       match result:
           case Success(phone):
               print(f"{fmt} -> {phone.national}")
           case Failure(_):
               print(f"{fmt} -> INVALID")

   # Canadian phone number
   result = parsers.parse_phone("+1 604 555 1234", region='CA')
   match result:
       case Success(phone):
           print(f"Region: {phone.region}")  # CA
           print(f"E.164: {phone.e164}")     # +16045551234
       case Failure(_):
           print("This won't happen")

   # Strict mode requires formatting characters
   result = parsers.parse_phone("4155552671", strict=True)
   match result:
       case Success(_):
           print("This won't happen in strict mode")
       case Failure(error):
           print(error)  # "Strict mode requires formatting characters"

   # Properly formatted passes strict mode
   result = parsers.parse_phone("(415) 555-2671", strict=True)
   match result:
       case Success(phone):
           print(f"Valid in strict mode: {phone.national}")
       case Failure(_):
           print("This won't happen")

   # Validation with pattern matching guards
   def validate_business_phone(phone_str: str):
       result = parsers.parse_phone(phone_str)
       match result:
           case Success(phone) if phone.area_code in ('800', '888', '877', '866'):
               return {"valid": True, "type": "toll-free"}
           case Success(phone) if phone.area_code == '555':
               return {"valid": False, "error": "555 is not a real area code"}
           case Success(phone):
               return {"valid": True, "type": "standard", "area": phone.area_code}
           case Failure(error):
               return {"valid": False, "error": error}

   print(validate_business_phone("(800) 555-1234"))
   # {'valid': True, 'type': 'toll-free'}

Creating Custom Parsers
------------------------

Valid8r offers two approaches for creating custom parsers:

Using the ``create_parser`` Function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``create_parser`` function allows you to create a parser from any function that converts a string to another type:

.. code-block:: python

   from valid8r.core.parsers import create_parser
   from valid8r.core.maybe import Maybe, Success, Failure
   # You can still create custom parsers with create_parser for other types.

   # Parse a string to an IP address
   # (Built-in helpers exist: parse_ipv4/parse_ipv6/parse_ip/parse_cidr)
   result = create_parser(int, "Not a valid integer")("123")
   match result:
       case Success(value):
           print(f"Parsed: {value}")  # Parsed: 123
       case Failure(error):
           print(f"Error: {error}")

Using the ``make_parser`` Decorator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``make_parser`` decorator converts a function into a parser:

.. code-block:: python

   from valid8r.core.parsers import make_parser
   from decimal import Decimal

   # Create a parser using the decorator
   @make_parser
   def parse_decimal(s: str) -> Decimal:
       return Decimal(s)

   # Parse with custom error message
   @make_parser
   def parse_percentage(s: str) -> float:
       value = float(s.strip('%')) / 100
       return value

   # Use the parsers
   result = parse_decimal("42.5")
   match result:
       case Success(value):
           print(f"Parsed decimal: {value}")  # Parsed decimal: 42.5
       case Failure(error):
           print(f"Error: {error}")

   result = parse_percentage("75%")
   match result:
       case Success(value):
           print(f"Parsed percentage: {value}")  # Parsed percentage: 0.75
       case Failure(error):
           print(f"Error: {error}")

Validated Parsers
----------------

For cases where you want to combine parsing and validation in a single step:

.. code-block:: python

   from valid8r.core.parsers import validated_parser
   from valid8r.core.validators import minimum, maximum
   from decimal import Decimal

   # Create a parser that only accepts positive numbers
   positive_decimal = validated_parser(
       Decimal,  # Convert function
       lambda x: minimum(Decimal('0'))(x),  # Validator function
       "Not a valid positive decimal"  # Error message
   )

   # Use the validated parser
   result = positive_decimal("42.5")  # Valid
   match result:
       case Success(value):
           print(f"Valid positive decimal: {value}")  # Valid positive decimal: 42.5
       case Failure(error):
           print(f"Error: {error}")

   result = positive_decimal("-10.5")  # Invalid
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(f"Error: {error}")  # Error: Value must be at least 0

Error Handling
--------------

All parsers follow consistent error handling patterns:

1. If the input is empty, the error is "Input must not be empty"
2. If the input cannot be parsed, a type-specific error is returned (e.g., "Input must be a valid integer")
3. You can provide a custom error message to override the default ones

.. code-block:: python

   from valid8r import parsers
   from valid8r.core.maybe import Success, Failure

   # Empty input
   result = parsers.parse_int("")
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "Input must not be empty"

   # Invalid input
   result = parsers.parse_int("abc")
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "Input must be a valid integer"

   # Custom error message
   result = parsers.parse_int("abc", error_message="Please enter a number")
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "Please enter a number"

Common Parser Features
----------------------

All parsers have these common features:

1. **Whitespace handling**: Leading and trailing whitespace is automatically removed
2. **Maybe return value**: All parsers return a Maybe object that can be pattern matched
3. **Custom error messages**: All parsers accept an optional error_message parameter
4. **Empty input handling**: All parsers check for empty input first

Combining Parsers with Validators
---------------------------------

Parsers are often used together with validators to create a complete validation pipeline:

.. code-block:: python

   from valid8r import parsers, validators
   from valid8r.core.maybe import Success, Failure

   # Parse a string to an integer, then validate it's positive
   result = parsers.parse_int("42").bind(
       lambda x: validators.minimum(0)(x)
   )

   match result:
       case Success(value):
           print(f"Valid positive number: {value}")  # Valid positive number: 42
       case Failure(error):
           print(f"Error: {error}")

   # Parse a string to a date, then validate it's in the future
   from datetime import date

   def is_future_date(d):
       if d > date.today():
           return Maybe.success(d)
       return Maybe.failure("Date must be in the future")

   result = parsers.parse_date("2025-01-01").bind(is_future_date)

   match result:
       case Success(value):
           print(f"Valid future date: {value}")  # Valid future date: 2025-01-01
       case Failure(error):
           print(f"Error: {error}")

Parser Function Errors vs Validation Logic
------------------------------------------

When deciding between handling errors in parser functions versus validation logic:

.. code-block:: python

   from valid8r import parsers, validators
   from valid8r.core.maybe import Success, Failure

   # Approach 1: Handle it in the parser directly
   result = parsers.parse_int("42.5")  # Will fail because it's not an integer
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "Input must be a valid integer"

   # Approach 2: Parse as float, then validate it's an integer
   def validate_integer_value(x):
       if x.is_integer():
           return Maybe.success(int(x))
       return Maybe.failure("Value must be an integer")

   result = parsers.parse_float("42.5").bind(validate_integer_value)
   match result:
       case Success(_):
           print("This won't happen")
       case Failure(error):
           print(error)  # "Value must be an integer"

Parsing with Validation
-----------------------

Valid8r provides parser functions with built-in validation:

.. code-block:: python

   from valid8r import parsers
   from valid8r.core.maybe import Success, Failure

   # Parse an integer with validation
   result = parsers.parse_int_with_validation("42", min_value=0, max_value=100)
   match result:
       case Success(value):
           print(f"Valid integer: {value}")  # Valid integer: 42
       case Failure(error):
           print(f"Error: {error}")

   # Parse a list with length validation
   result = parsers.parse_list_with_validation(
       "1,2,3,4,5",
       element_parser=parsers.parse_int,
       min_length=3,
       max_length=10
   )
   match result:
       case Success(value):
           print(f"Valid list: {value}")  # Valid list: [1, 2, 3, 4, 5]
       case Failure(error):
           print(f"Error: {error}")

   # Parse a dictionary with required keys
   result = parsers.parse_dict_with_validation(
       "name:John,age:30,city:New York",
       value_parser=parsers.parse_int,
       required_keys=["name", "age"]
   )
   match result:
       case Success(value):
           print(f"Valid dict: {value}")  # Valid dict: {'name': 'John', 'age': 30, 'city': 'New York'}
       case Failure(error):
           print(f"Error: {error}")

Parser Limitations and Edge Cases
---------------------------------

Here are some important things to know about the parsers:

Integer Parser
~~~~~~~~~~~~~~

- Handles decimals that convert exactly to integers (e.g., "42.0")
- Rejects decimals with fractional parts (e.g., "42.5")
- Handles leading zeros (e.g., "007" → 7)
- Handles large integers automatically

Float Parser
~~~~~~~~~~~~

- Accepts special values like "inf", "-inf", and "NaN"
- Scientific notation is supported
- Very large or small values near the limits of float precision may have representation issues

Boolean Parser
~~~~~~~~~~~~~~

- Only recognizes specific strings for true/false values
- Case-insensitive for string-based inputs

Date Parser
~~~~~~~~~~~

- When using custom formats, use strftime/strptime codes (e.g., %Y, %m, %d)
- ISO format (YYYY-MM-DD) is the default when no format is specified
- Compact formats without separators (e.g., "20230115") need explicit format strings

Complex Parser
~~~~~~~~~~~~~~

- Handles various notations, including spaces between parts
- Accepts both 'j' and 'i' for the imaginary part
- Parentheses are handled ("(3+4j)" is valid)

Enum Parser
~~~~~~~~~~~

- Case-sensitive by default
- Works with both name and value lookup
- Handles whitespace automatically
- Special handling for empty values if the enum contains an empty string value

In the next section, we'll explore validators for checking that values meet specific criteria.
