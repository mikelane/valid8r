Security Overview
=================

Valid8r is designed for **parsing and validating trusted user input** in web applications. This page provides an overview of security considerations when using Valid8r in production.

Quick Links
-----------

- :doc:`production-deployment` - Framework-specific deployment guides (Flask, Django, FastAPI)
- :doc:`secure-parser-development` - Writing secure custom parsers (DoS prevention)
- :doc:`policy` - Vulnerability reporting and security policy

Security Boundaries
-------------------

**What Valid8r Provides:**

✅ Type-safe parsing with explicit error handling

✅ Built-in DoS protection via early length validation

✅ Structured validation for emails, URLs, phone numbers, UUIDs, IP addresses

✅ Functional error handling with Maybe monad (no exceptions for validation)

**What Valid8r Does NOT Protect Against:**

❌ **SQL injection** - Use parameterized queries with your database ORM

❌ **XSS attacks** - Use output encoding in your template engine

❌ **CSRF attacks** - Use CSRF tokens and SameSite cookies

❌ **DDoS attacks** - Use rate limiting, WAF, or cloud provider protection

❌ **Authentication/Authorization** - Use proper auth framework (OAuth2, JWT, etc.)

Defense in Depth Strategy
--------------------------

Never rely on Valid8r alone. Use multiple defensive layers:

.. code-block:: text

   ┌─────────────────────────────────────────┐
   │  Layer 1: WAF / Load Balancer          │  ← DDoS protection, IP filtering
   ├─────────────────────────────────────────┤
   │  Layer 2: Framework Middleware          │  ← Request size limits, rate limiting
   ├─────────────────────────────────────────┤
   │  Layer 3: Application Validation        │  ← Business logic, field-level checks
   ├─────────────────────────────────────────┤
   │  Layer 4: Valid8r Parsers               │  ← Type safety, format validation
   ├─────────────────────────────────────────┤
   │  Layer 5: Database Constraints          │  ← Final data integrity checks
   └─────────────────────────────────────────┘

Parser Input Limits
-------------------

All Valid8r parsers include built-in DoS protection with early length validation:

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

.. warning::

   Parser limits are **defense-in-depth**, not your primary defense. Always enforce application-level size limits BEFORE parsing.

Example: Secure Validation Pattern
-----------------------------------

Here's a secure validation pattern using defense in depth:

.. code-block:: python

   from flask import Flask, request, jsonify
   from valid8r import parsers
   from valid8r.core.maybe import Success, Failure

   app = Flask(__name__)
   app.config['MAX_CONTENT_LENGTH'] = 10 * 1024  # Layer 1: Framework limit

   @app.route('/api/validate', methods=['POST'])
   def validate_input():
       data = request.get_json()

       # Layer 2: Application-level pre-validation
       email_input = data.get('email', '')
       if len(email_input) > 254:
           return jsonify({"error": "Email too long"}), 400

       # Layer 3: Valid8r parsing (with built-in DoS protection)
       match parsers.parse_email(email_input):
           case Success(email):
               return jsonify({"email": email.local + "@" + email.domain})
           case Failure(_):
               # Don't expose internal error details
               return jsonify({"error": "Invalid email"}), 400

DoS Protection
--------------

All parsers validate input length **before** expensive operations (regex, external libraries):

**Without length guard (vulnerable):**

- 1MB malicious input: ~48ms to reject (after regex operations)
- Attack vector: Resource exhaustion

**With length guard (protected):**

- 1MB malicious input: <1ms to reject (before regex operations)
- 48x faster rejection, preventing resource exhaustion

See :doc:`secure-parser-development` for implementation guidelines.

Recent Security Fixes
---------------------

v0.9.1 - Phone Parser DoS Protection (November 2025)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Issue**: Phone parser performed regex operations before validating input length, allowing DoS attacks with extremely large inputs.

**Impact**: Medium severity - could cause resource exhaustion with 1MB+ inputs

**Fix**: Added early length validation before regex operations

- Rejects oversized inputs in <1ms (48x faster)
- Limit: 100 characters (reasonable for any phone number format)

**Testing**: Added performance-validated test ensuring <10ms rejection time

See :doc:`policy` for the complete security policy and vulnerability reporting process.

Production Deployment
---------------------

For framework-specific deployment guides, rate limiting strategies, and monitoring recommendations, see:

- :doc:`production-deployment` - Complete production deployment guide
- :doc:`secure-parser-development` - Guidelines for writing secure custom parsers

Reporting Security Issues
--------------------------

If you discover a security vulnerability in Valid8r:

1. **Do NOT open a public GitHub issue**
2. Email **mikelane@gmail.com** with details
3. You will receive a response within 48 hours
4. We aim to release fixes within 7 days for critical issues

See :doc:`policy` for the complete reporting process.

Additional Resources
--------------------

- `OWASP Input Validation Cheat Sheet <https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html>`_
- `GitHub Security Advisories <https://github.com/mikelane/valid8r/security/advisories>`_
- `Dependabot Alerts <https://github.com/mikelane/valid8r/security/dependabot>`_
