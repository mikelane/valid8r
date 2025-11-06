# Security Policy

## Supported Versions

We release security updates for the following versions of Valid8r:

| Version | Supported          |
| ------- | ------------------ |
| 0.9.x   | :white_check_mark: |
| 0.8.x   | :white_check_mark: |
| 0.7.x   | :white_check_mark: |
| < 0.7.0 | :x:                |

## Reporting a Vulnerability

We take security issues seriously. If you discover a security vulnerability in Valid8r, please follow these steps:

### 1. Do Not Open a Public Issue

Please do not report security vulnerabilities through public GitHub issues, discussions, or pull requests.

### 2. Report Privately

Send an email to **mikelane@gmail.com** with the following information:

- **Description**: A clear description of the vulnerability
- **Impact**: Potential impact and attack scenarios
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Affected Versions**: Which versions are affected
- **Proposed Fix**: If you have suggestions for fixing the issue

### 3. Use This Email Template

```
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
```

### 4. What to Expect

- **Initial Response**: You will receive an acknowledgment within 48 hours
- **Status Updates**: We will keep you informed of our progress
- **Fix Timeline**: We aim to release security fixes within 7 days for critical issues
- **Credit**: We will credit you in the security advisory (unless you prefer to remain anonymous)
- **Disclosure**: We follow coordinated disclosure and will work with you on the disclosure timeline

## Security Update Process

When a security vulnerability is confirmed:

1. **Patch Development**: We develop and test a fix
2. **Version Bump**: We prepare a new release with the security fix
3. **Security Advisory**: We publish a GitHub Security Advisory
4. **Release**: We release the patched version to PyPI
5. **Notification**: We notify users through:
   - GitHub Security Advisories
   - Release notes
   - CHANGELOG.md

## Security Best Practices

When using Valid8r:

### Input Validation

- **Always validate untrusted input**: Use Valid8r parsers for all external data
- **Fail securely**: Handle `Failure` results appropriately
- **Don't leak information**: Avoid exposing detailed error messages to end users

### Dependencies

- **Keep Updated**: Regularly update Valid8r and its dependencies
- **Monitor Advisories**: Watch for security advisories on GitHub
- **Use Dependabot**: Enable Dependabot alerts in your repository

### Example Secure Usage

```python
from valid8r import parsers, validators
from valid8r.core.maybe import Success, Failure

# Good: Parse and validate untrusted input
user_age = input("Enter your age: ")
match parsers.parse_int(user_age):
    case Success(age) if age >= 0 and age <= 120:
        print(f"Valid age: {age}")
    case Success(age):
        print("Age out of valid range")  # Don't expose the actual value
    case Failure(_):
        print("Invalid input")  # Don't expose error details

# Good: Validate email addresses
email = input("Enter email: ")
match parsers.parse_email(email):
    case Success(email_obj):
        # Proceed with validated email
        send_confirmation(email_obj)
    case Failure(_):
        print("Invalid email format")
```

## Security Boundaries

### Input Validation Philosophy

Valid8r is designed as a **parsing and validation library**, not a security boundary:

- **✅ Trusted input**: Best suited for user-generated content in web forms, API requests
- **⚠️ Untrusted input**: Should be pre-validated at application level (size limits, rate limiting)
- **❌ Hostile input**: Requires additional defenses (WAF, DDoS protection, sandboxing)

### Parser Input Limits

All parsers include built-in length validation to prevent DoS attacks:

| Parser | Max Input | Rationale |
|--------|-----------|-----------|
| `parse_phone()` | 100 chars | Longest international format + extension |
| `parse_email()` | 254 chars | RFC 5321 maximum email address length |
| `parse_url()` | 2048 chars | Common browser URL limit |
| `parse_uuid()` | 36 chars | Standard UUID format (with hyphens) |
| `parse_ip()` | 45 chars | IPv6 maximum length |
| `parse_ipv4()` | 15 chars | xxx.xxx.xxx.xxx |
| `parse_ipv6()` | 45 chars | Full IPv6 notation |
| `parse_cidr()` | 50 chars | IPv6 + CIDR notation |

**⚠️ Important**: Always enforce application-level size limits BEFORE parsing. Valid8r's limits are defense-in-depth, not your primary defense.

### What Valid8r Does NOT Protect Against

Valid8r provides **input validation**, not:

- ❌ **SQL injection** - Use parameterized queries / ORMs
- ❌ **XSS** - Use output encoding / template engines
- ❌ **CSRF** - Use CSRF tokens / SameSite cookies
- ❌ **Rate limiting** - Implement at framework/WAF level
- ❌ **Authentication/Authorization** - Use proper auth framework
- ❌ **DDoS attacks** - Use CDN / cloud provider protection

## Known Security Considerations

### DoS Protection Through Input Length Validation

**All parsers include built-in length validation** to prevent Denial of Service attacks. Input length is checked BEFORE expensive operations like regex matching.

**Example: Phone Parser DoS Protection (Fixed in v0.9.1)**

Prior to v0.9.1, the phone parser performed regex operations before validating input length:
- ❌ 1MB malicious input: ~48ms to reject (after regex)
- ✅ v0.9.1+: 1MB input: <1ms to reject (before regex)

**Implementation Pattern**:
```python
def parse_phone(text: str | None, *, region: str = 'US', strict: bool = False) -> Maybe[PhoneNumber]:
    # Handle None or empty
    if text is None or not isinstance(text, str):
        return Maybe.failure('Phone number cannot be empty')

    s = text.strip()
    if s == '':
        return Maybe.failure('Phone number cannot be empty')

    # CRITICAL: Early length guard (DoS mitigation)
    if len(text) > 100:
        return Maybe.failure('Invalid format: phone number is too long')

    # Now safe to perform regex operations
    # ...
```

**Why This Matters**:
- Prevents resource exhaustion from oversized inputs
- Rejects malicious inputs in microseconds instead of milliseconds
- Applies to all parsers that use regex (email, URL, IP, phone, etc.)

**Additional Application-Level Protection**:

While Valid8r includes built-in length validation, you can add additional limits for your specific use case:

```python
from valid8r import parsers
from valid8r.core.maybe import Maybe, Failure

MAX_EMAIL_LENGTH = 254  # RFC 5321 maximum

def safe_parse_email(text: str) -> Maybe[EmailAddress]:
    """Parse email with stricter length limit for your application."""
    if len(text) > MAX_EMAIL_LENGTH:
        return Failure("Email address exceeds maximum length")
    return parsers.parse_email(text)
```

### Error Messages

Parser error messages are designed to be user-friendly but may contain details about why validation failed. In security-sensitive contexts, consider sanitizing error messages before displaying to end users.

## Recent Security Fixes

### v0.9.1 - Phone Parser DoS Protection (November 2025)

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

**Related**: Issue #131, PR #138

## Production Deployment Guidelines

### Defense in Depth Pattern

Always use multiple layers of validation:

```python
from flask import Flask, request
from valid8r import parsers

app = Flask(__name__)

@app.route('/submit', methods=['POST'])
def submit():
    # Layer 1: Framework-level size limit (FIRST DEFENSE)
    if len(request.data) > 10_000:  # 10KB max request
        return "Request too large", 413

    # Layer 2: Application-level validation (SECOND DEFENSE)
    phone = request.form.get('phone', '')
    if len(phone) > 100:
        return "Phone number too long", 400

    # Layer 3: Parser validation (THIRD DEFENSE)
    result = parsers.parse_phone(phone)
    if result.is_failure():
        # Don't expose internal error details to users
        return "Invalid phone number format", 400

    # Now safe to use validated phone number
    return process_phone(result.value_or(None))
```

### Rate Limiting

Protect validation endpoints from abuse:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route('/validate')
@limiter.limit("10 per minute")  # Strict limit for validation
def validate_input():
    # Validation logic
    pass
```

### Error Handling

Don't expose internal validation details:

```python
from valid8r import parsers
from valid8r.core.maybe import Success, Failure

result = parsers.parse_email(user_input)

match result:
    case Success(email):
        # Log successful validation (info level)
        logger.info(f"Valid email processed: {email.domain}")
        return email
    case Failure(error):
        # Log failure (warning level) but DON'T expose to user
        logger.warning(f"Email validation failed: {error}")
        # Generic user-facing message
        return "Invalid email address format"
```

### Batch Processing

Use timeouts and size limits for batch operations:

```python
from celery import Celery
from valid8r import parsers

app = Celery('tasks')

@app.task(time_limit=5)  # 5 second timeout per task
def validate_batch(phone_numbers):
    # Limit batch size
    if len(phone_numbers) > 1000:
        raise ValueError("Batch too large")

    results = []
    for phone in phone_numbers:
        # Pre-validation before parsing
        if len(phone) > 100:
            results.append({"error": "too long"})
            continue

        result = parsers.parse_phone(phone)
        results.append({
            "success": result.is_success(),
            "error": None if result.is_success() else "invalid format"
        })

    return results
```

### Framework-Specific Configuration

**Flask**:
```python
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024  # 10KB
```

**Django**:
```python
DATA_UPLOAD_MAX_MEMORY_SIZE = 10240  # 10KB
```

**FastAPI**:
```python
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["example.com"]
)
```

### Security Testing

Include security tests in your CI/CD:

```bash
# Run DoS prevention tests
uv run pytest tests/security/test_dos_prevention.py -v

# Run all security-marked tests
uv run pytest -m security
```

## Scope

This security policy covers:

- ✅ Valid8r library code (parsers, validators, Maybe monad)
- ✅ Input validation vulnerabilities
- ✅ Dependency vulnerabilities
- ❌ Vulnerabilities in user application code
- ❌ Misuse of the library by developers

## Security Resources

- [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
- [GitHub Security Advisories](https://github.com/mikelane/valid8r/security/advisories)
- [Dependabot Alerts](https://github.com/mikelane/valid8r/security/dependabot)

## Contact

For security issues: **mikelane@gmail.com**

For general questions: Open a GitHub Discussion or Issue

---

Thank you for helping keep Valid8r and its users safe!
