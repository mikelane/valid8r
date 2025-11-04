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
