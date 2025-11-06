FastAPI + Pydantic Integration
================================

This example demonstrates how to use Valid8r with FastAPI and Pydantic for robust API validation. Valid8r's Maybe monad pattern integrates seamlessly with Pydantic's validation system, and Python's pattern matching makes error handling elegant and readable.

Installation
------------

To run this example, install the required dependencies:

.. code-block:: bash

   pip install valid8r fastapi uvicorn

Overview
--------

Valid8r works naturally with FastAPI and Pydantic by:

1. Using Valid8r parsers in Pydantic ``@field_validator`` decorators
2. Leveraging Python's ``match/case`` for elegant Success/Failure handling
3. Providing custom validation functions with dependency injection style
4. Enabling batch validation with detailed results
5. Supporting chained validators using ``bind()``

Example 1: Pattern Matching with Field Validators
--------------------------------------------------

Use Python's ``match/case`` to handle validation results elegantly:

.. code-block:: python

   from fastapi import FastAPI
   from pydantic import BaseModel, field_validator
   from valid8r import parsers, validators
   from valid8r.core.maybe import Success, Failure

   app = FastAPI()

   class UserCreate(BaseModel):
       email: str
       age: int
       website: str | None = None

       @field_validator('email')
       @classmethod
       def validate_email(cls, v: str) -> str:
           """Validate email using Valid8r's parse_email with pattern matching."""
           result = parsers.parse_email(v)

           match result:
               case Success(email):
                   # Email is valid, return the original string
                   return v
               case Failure(error):
                   raise ValueError(error)

       @field_validator('age')
       @classmethod
       def validate_age(cls, v: int) -> int:
           """Validate age is between 18 and 120 using pattern matching."""
           result = validators.between(18, 120)(v)

           match result:
               case Success(age):
                   return age
               case Failure(error):
                   raise ValueError(error)

       @field_validator('website')
       @classmethod
       def validate_website(cls, v: str | None) -> str | None:
           """Validate website URL with pattern matching and guards."""
           if v is None:
               return v

           result = parsers.parse_url(v)

           match result:
               case Success(url) if url.scheme in ('http', 'https'):
                   # Valid URL with acceptable scheme
                   return v
               case Success(url):
                   # Valid URL but wrong scheme
                   raise ValueError(
                       f'Website must use http or https, got {url.scheme}'
                   )
               case Failure(error):
                   raise ValueError(error)

   @app.post('/users', status_code=201)
   async def create_user(user: UserCreate) -> dict:
       """Create a new user with validated input."""
       return {
           'message': 'User created successfully',
           'user': {
               'email': user.email,
               'age': user.age,
               'website': user.website,
           },
       }

Example 2: Advanced Pattern Matching
-------------------------------------

Use pattern guards and complex matching for sophisticated validation:

.. code-block:: python

   from fastapi import HTTPException, Body
   from typing import Annotated

   def validate_and_classify_ip(ip_str: str) -> dict:
       """Validate IP and classify as private or public using pattern matching."""
       result = parsers.parse_ipv4(ip_str)

       match result:
           case Success(ip) if ip.is_private:
               return {
                   'ip': str(ip),
                   'type': 'private',
                   'routable': False
               }
           case Success(ip) if ip.is_loopback:
               return {
                   'ip': str(ip),
                   'type': 'loopback',
                   'routable': False
               }
           case Success(ip):
               return {
                   'ip': str(ip),
                   'type': 'public',
                   'routable': True
               }
           case Failure(error):
               raise HTTPException(status_code=400, detail=error)

   @app.post('/classify-ip')
   async def classify_ip(
       ip_address: Annotated[str, Body(embed=True)]
   ) -> dict:
       """Classify an IP address with validation."""
       return validate_and_classify_ip(ip_address)

Example 3: Batch Validation with Pattern Matching
--------------------------------------------------

Process multiple inputs using pattern matching for clear result handling:

.. code-block:: python

   from valid8r.core.maybe import Success, Failure

   class BatchEmailValidation(BaseModel):
       """Model for batch email validation."""
       emails: list[str]

   @app.post('/validate-emails')
   async def validate_emails(batch: BatchEmailValidation) -> dict:
       """Validate multiple emails using pattern matching."""
       results = []

       for email_str in batch.emails:
           result = parsers.parse_email(email_str)

           # Use pattern matching to build result dict
           match result:
               case Success(email):
                   results.append({
                       'email': email_str,
                       'valid': True,
                       'local': email.local,
                       'domain': email.domain,
                   })
               case Failure(error):
                   results.append({
                       'email': email_str,
                       'valid': False,
                       'error': error
                   })

       valid_count = sum(1 for r in results if r['valid'])
       return {
           'total': len(batch.emails),
           'valid': valid_count,
           'invalid': len(batch.emails) - valid_count,
           'results': results,
       }

Example 4: Multi-Field Pattern Matching
----------------------------------------

Match on multiple validation results simultaneously:

.. code-block:: python

   class ServerConfig(BaseModel):
       """Server configuration with rich validation."""
       host: str
       port: int
       max_connections: int

       @field_validator('host')
       @classmethod
       def validate_host(cls, v: str) -> str:
           """Validate host using fallback pattern matching."""
           ipv4_result = parsers.parse_ipv4(v)
           ipv6_result = parsers.parse_ipv6(v)

           # Try IPv4 first, then IPv6, then treat as hostname
           match (ipv4_result, ipv6_result):
               case (Success(_), _):
                   # Valid IPv4
                   return v
               case (_, Success(_)):
                   # Valid IPv6
                   return v
               case (Failure(_), Failure(_)):
                   # Not a valid IP, validate as hostname
                   if not v or '/' in v or '@' in v:
                       raise ValueError('Invalid hostname')
                   return v

       @field_validator('port')
       @classmethod
       def validate_port(cls, v: int) -> int:
           """Validate port is in valid range."""
           result = validators.between(1, 65535)(v)

           match result:
               case Success(port):
                   return port
               case Failure(error):
                   raise ValueError(error)

       @field_validator('max_connections')
       @classmethod
       def validate_max_connections(cls, v: int) -> int:
           """Validate max connections is positive."""
           result = validators.minimum(1)(v)

           match result:
               case Success(connections):
                   return connections
               case Failure(error):
                   raise ValueError(error)

   @app.post('/configure')
   async def configure_server(config: ServerConfig) -> dict:
       """Configure server with validated settings."""
       return {
           'message': 'Server configured successfully',
           'config': {
               'host': config.host,
               'port': config.port,
               'max_connections': config.max_connections,
           },
       }

Example 5: Chained Validation with Pattern Matching
----------------------------------------------------

Chain validators and use pattern matching for complex validation flows:

.. code-block:: python

   class ProductCreate(BaseModel):
       """Product creation with chained validation."""
       name: str
       price: float
       quantity: int

       @field_validator('name')
       @classmethod
       def validate_name(cls, v: str) -> str:
           """Chain length and content validation."""
           # Chain multiple validators
           result = (
               validators.length(3, 100)(v)
               .bind(lambda s: validators.predicate(
                   lambda x: not x.isspace(),
                   'Name cannot be only whitespace'
               )(s))
           )

           match result:
               case Success(name):
                   return name
               case Failure(error) if 'length' in error.lower():
                   raise ValueError(f'Name length error: {error}')
               case Failure(error):
                   raise ValueError(f'Name validation error: {error}')

       @field_validator('price')
       @classmethod
       def validate_price(cls, v: float) -> float:
           """Validate price with detailed error messages."""
           result = validators.predicate(
               lambda x: x > 0,
               'Price must be positive'
           )(v)

           match result:
               case Success(price) if price > 1000000:
                   raise ValueError('Price seems unreasonably high')
               case Success(price):
                   return price
               case Failure(error):
                   raise ValueError(error)

       @field_validator('quantity')
       @classmethod
       def validate_quantity(cls, v: int) -> int:
           """Validate quantity with pattern guards."""
           result = validators.between(1, 10000)(v)

           match result:
               case Success(qty) if qty < 10:
                   # Low stock warning (still valid)
                   return qty
               case Success(qty):
                   return qty
               case Failure(error):
                   raise ValueError(error)

   @app.post('/products')
   async def create_product(product: ProductCreate) -> dict:
       """Create a product with chained validation."""
       return {
           'message': 'Product created successfully',
           'product': {
               'name': product.name,
               'price': product.price,
               'quantity': product.quantity
           },
       }

Example 6: Custom Validation with Rich Error Context
-----------------------------------------------------

Use pattern matching to provide context-rich error messages:

.. code-block:: python

   from typing import Literal

   def validate_user_input(
       email: str,
       age_str: str,
       role: Literal['admin', 'user', 'guest']
   ) -> dict | None:
       """Validate user input with comprehensive pattern matching."""
       email_result = parsers.parse_email(email)
       age_result = parsers.parse_int(age_str).bind(
           validators.between(18, 120)
       )

       # Match on both results simultaneously
       match (email_result, age_result):
           case (Success(email), Success(age)) if role == 'admin' and age < 21:
               return {
                   'status': 'error',
                   'message': 'Admins must be at least 21 years old'
               }
           case (Success(email), Success(age)):
               return {
                   'status': 'success',
                   'user': {
                       'email': f'{email.local}@{email.domain}',
                       'age': age,
                       'role': role
                   }
               }
           case (Failure(error), Success(_)):
               return {
                   'status': 'error',
                   'field': 'email',
                   'message': error
               }
           case (Success(_), Failure(error)):
               return {
                   'status': 'error',
                   'field': 'age',
                   'message': error
               }
           case (Failure(email_error), Failure(age_error)):
               return {
                   'status': 'error',
                   'message': 'Multiple validation errors',
                   'errors': {
                       'email': email_error,
                       'age': age_error
                   }
               }

   @app.post('/validate-user')
   async def validate_user(
       email: str = Body(...),
       age: str = Body(...),
       role: Literal['admin', 'user', 'guest'] = Body(...)
   ) -> dict:
       """Validate user with rich error context."""
       result = validate_user_input(email, age, role)

       if result and result.get('status') == 'error':
           raise HTTPException(status_code=400, detail=result)

       return result

Example 7: Production-Ready FastAPI Integration
------------------------------------------------

For production deployments, add defense-in-depth validation with rate limiting, host validation, and multiple security layers:

.. code-block:: python

   from fastapi import FastAPI, HTTPException, Request
   from fastapi.middleware.trustedhost import TrustedHostMiddleware
   from slowapi import Limiter, _rate_limit_exceeded_handler
   from slowapi.util import get_remote_address
   from slowapi.errors import RateLimitExceeded
   from valid8r import parsers
   from valid8r.core.maybe import Success, Failure
   from pydantic import BaseModel, field_validator

   app = FastAPI()

   # Layer 1: Rate limiting
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

   # Layer 2: Trusted host middleware
   app.add_middleware(TrustedHostMiddleware, allowed_hosts=["example.com"])

   class UserInput(BaseModel):
       email: str
       phone: str

       # Layer 3: Pydantic field validation (pre-Valid8r)
       @field_validator('email')
       @classmethod
       def validate_email_length(cls, v: str) -> str:
           if len(v) > 254:
               raise ValueError('Email too long')
           return v

       @field_validator('phone')
       @classmethod
       def validate_phone_length(cls, v: str) -> str:
           if len(v) > 100:
               raise ValueError('Phone number too long')
           return v

   @app.post("/users/")
   @limiter.limit("10/minute")  # Rate limit per IP
   def create_user(request: Request, user: UserInput):
       """Create user with defense-in-depth validation."""
       # Layer 4: Valid8r parsing (with built-in DoS protection)
       email_result = parsers.parse_email(user.email)
       phone_result = parsers.parse_phone(user.phone)

       match (email_result, phone_result):
           case (Success(email), Success(phone)):
               return {
                   "email": f"{email.local}@{email.domain}",
                   "phone": phone.national
               }
           case (Failure(_), _):
               raise HTTPException(status_code=400, detail="Invalid email")
           case (_, Failure(_)):
               raise HTTPException(status_code=400, detail="Invalid phone")

.. note::
   This example demonstrates **defense in depth**: rate limiting (Layer 1), host validation (Layer 2),
   Pydantic pre-validation (Layer 3), and Valid8r parsing (Layer 4). See :doc:`/security/production-deployment`
   for complete FastAPI security patterns.

Installation for Production Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To run the production example, install additional dependencies:

.. code-block:: bash

   pip install valid8r fastapi uvicorn slowapi

Running the Example
--------------------

Save the code above to a file (e.g., ``app.py``) and run:

.. code-block:: bash

   uvicorn app:app --reload

Visit http://localhost:8000/docs for interactive API documentation powered by FastAPI's automatic OpenAPI generation.

Example Requests
----------------

**Create User:**

.. code-block:: bash

   curl -X POST "http://localhost:8000/users" \\
     -H "Content-Type: application/json" \\
     -d '{
       "email": "user@example.com",
       "age": 25,
       "website": "https://example.com"
     }'

**Classify IP Address:**

.. code-block:: bash

   curl -X POST "http://localhost:8000/classify-ip" \\
     -H "Content-Type: application/json" \\
     -d '{"ip_address": "192.168.1.1"}'

**Batch Email Validation:**

.. code-block:: bash

   curl -X POST "http://localhost:8000/validate-emails" \\
     -H "Content-Type: application/json" \\
     -d '{
       "emails": [
         "valid@example.com",
         "invalid-email",
         "another@test.org"
       ]
     }'

Key Takeaways
-------------

* **Pattern Matching Power**: Python's ``match/case`` makes Maybe monad handling elegant and readable
* **Pattern Guards**: Use ``if`` conditions in match cases for sophisticated validation logic
* **Multiple Results**: Match on tuples of results to handle complex multi-field validation
* **Clear Error Handling**: Pattern matching makes success and failure paths explicit
* **Seamless Integration**: Valid8r's Maybe monad fits naturally with Pydantic's validation
* **Type Safety**: Full type hints throughout for excellent IDE support
* **Functional Approach**: Use Success/Failure types instead of exceptions for elegant error handling

Why Pattern Matching?
----------------------

Pattern matching with ``match/case`` provides several advantages over traditional ``if/else`` or method checks:

1. **Exhaustive Handling**: The compiler ensures you handle all cases
2. **Guards for Complex Logic**: Use ``if`` conditions within cases for sophisticated matching
3. **Destructuring**: Extract values directly in the pattern (``case Success(value)``)
4. **Readability**: Code reads like a decision tree, making logic flow obvious
5. **Composability**: Easily match on multiple results simultaneously

This makes Valid8r's Maybe monad even more powerful when combined with Python 3.10+ pattern matching features.
