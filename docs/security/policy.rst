Security Policy
===============

This page contains the Valid8r security policy for reporting vulnerabilities and understanding our security update process.

.. note::

   For the complete security policy, see the `SECURITY.md file <https://github.com/mikelane/valid8r/blob/main/SECURITY.md>`_ in the repository.

Supported Versions
------------------

We release security updates for the following versions of Valid8r:

+----------+--------------------+
| Version  | Supported          |
+==========+====================+
| 0.9.x    | ✅ Yes             |
+----------+--------------------+
| 0.8.x    | ✅ Yes             |
+----------+--------------------+
| 0.7.x    | ✅ Yes             |
+----------+--------------------+
| < 0.7.0  | ❌ No              |
+----------+--------------------+

Reporting a Vulnerability
-------------------------

We take security issues seriously. If you discover a security vulnerability in Valid8r, please follow these steps:

1. Do Not Open a Public Issue
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Please **do not** report security vulnerabilities through public GitHub issues, discussions, or pull requests.

2. Report Privately
~~~~~~~~~~~~~~~~~~~

Send an email to **mikelane@gmail.com** with the following information:

- **Description**: A clear description of the vulnerability
- **Impact**: Potential impact and attack scenarios
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Affected Versions**: Which versions are affected
- **Proposed Fix**: If you have suggestions for fixing the issue

Email Template
~~~~~~~~~~~~~~

.. code-block:: text

   Subject: [SECURITY] Description of the vulnerability

   **Description:**
   A clear and concise description of the vulnerability.

   **Impact:**
   What could an attacker do with this vulnerability?

   **Steps to Reproduce:**
   1. Step one
   2. Step two
   3. ...

   **Affected Versions:**
   - Version X.X.X
   - Version Y.Y.Y

   **Proposed Fix:**
   (Optional) Your suggestions for fixing the issue.

   **Additional Context:**
   Any additional information, configurations, or screenshots.

3. What to Expect
~~~~~~~~~~~~~~~~~

- **Initial Response**: You will receive an acknowledgment within **48 hours**
- **Status Updates**: We will keep you informed of our progress
- **Fix Timeline**: We aim to release security fixes within **7 days** for critical issues
- **Credit**: We will credit you in the security advisory (unless you prefer to remain anonymous)
- **Disclosure**: We follow coordinated disclosure and will work with you on the disclosure timeline

Security Update Process
-----------------------

When a security vulnerability is confirmed:

1. **Patch Development**: We develop and test a fix
2. **Version Bump**: We prepare a new release with the security fix
3. **Security Advisory**: We publish a GitHub Security Advisory
4. **Release**: We release the patched version to PyPI
5. **Notification**: We notify users through:

   - GitHub Security Advisories
   - Release notes
   - CHANGELOG.md

Security Best Practices
-----------------------

When using Valid8r in production:

Input Validation
~~~~~~~~~~~~~~~~

- **Always validate untrusted input**: Use Valid8r parsers for all external data
- **Fail securely**: Handle ``Failure`` results appropriately
- **Don't leak information**: Avoid exposing detailed error messages to end users

Example:

.. code-block:: python

   from valid8r import parsers
   from valid8r.core.maybe import Success, Failure

   # Good: Parse and validate untrusted input
   user_age = input("Enter your age: ")
   match parsers.parse_int(user_age):
       case Success(age) if 0 <= age <= 120:
           print(f"Valid age: {age}")
       case Success(_):
           print("Age out of valid range")  # Don't expose the actual value
       case Failure(_):
           print("Invalid input")  # Don't expose error details

Dependencies
~~~~~~~~~~~~

- **Keep Updated**: Regularly update Valid8r and its dependencies
- **Monitor Advisories**: Watch for security advisories on GitHub
- **Use Dependabot**: Enable Dependabot alerts in your repository

Framework Configuration
~~~~~~~~~~~~~~~~~~~~~~~

Always configure request size limits at the framework level:

**Flask**:

.. code-block:: python

   app.config['MAX_CONTENT_LENGTH'] = 10 * 1024  # 10KB

**Django**:

.. code-block:: python

   DATA_UPLOAD_MAX_MEMORY_SIZE = 10240  # 10KB

**FastAPI**:

.. code-block:: python

   from fastapi.middleware.trustedhost import TrustedHostMiddleware

   app.add_middleware(
       TrustedHostMiddleware,
       allowed_hosts=["example.com"]
   )

See :doc:`production-deployment` for complete framework-specific guides.

Recent Security Fixes
---------------------

v0.9.1 - Phone Parser DoS Protection (November 2025)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Issue**: Phone parser performed regex operations before validating input length, allowing DoS attacks with extremely large inputs.

**Impact**: Medium severity - could cause resource exhaustion with 1MB+ inputs

- Processing time: ~48ms for 1MB malicious input
- Attack vector: Requires ability to send oversized POST data
- Real-world risk: Low (most frameworks limit request size)

**Fix**: Added early length validation before regex operations

- Rejects oversized inputs in <1ms (48x faster)
- Limit: 100 characters (reasonable for any phone number format)
- Error message: "Invalid format: phone number is too long"

**Testing**: Added performance-validated test ensuring <10ms rejection time

**Lesson**: Always validate input length BEFORE expensive operations. This pattern now applies to all new parsers.

**Related**: `Issue #131 <https://github.com/mikelane/valid8r/issues/131>`_, `PR #138 <https://github.com/mikelane/valid8r/pull/138>`_

Scope
-----

This security policy covers:

- ✅ Valid8r library code (parsers, validators, Maybe monad)
- ✅ Input validation vulnerabilities
- ✅ Dependency vulnerabilities
- ❌ Vulnerabilities in user application code
- ❌ Misuse of the library by developers

Security Resources
------------------

- `OWASP Input Validation Cheat Sheet <https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html>`_
- `GitHub Security Advisories <https://github.com/mikelane/valid8r/security/advisories>`_
- `Dependabot Alerts <https://github.com/mikelane/valid8r/security/dependabot>`_
- :doc:`production-deployment` - Production deployment security guide
- :doc:`secure-parser-development` - Secure parser development guidelines

Contact
-------

- **Security issues**: mikelane@gmail.com
- **General questions**: `Open a GitHub Discussion or Issue <https://github.com/mikelane/valid8r/issues>`_

Thank you for helping keep Valid8r and its users safe!
