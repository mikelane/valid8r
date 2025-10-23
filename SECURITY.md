# Security Policy

## Supported Versions

We release security updates for the following versions of Valid8r:

| Version | Supported          |
| ------- | ------------------ |
| 0.3.x   | :white_check_mark: |
| 0.2.x   | :x:                |
| < 0.2.0 | :x:                |

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

### Regular Expressions

Some parsers use regular expressions for validation. While we carefully design these to avoid ReDoS (Regular Expression Denial of Service) attacks, extremely large inputs may still cause performance issues.

**Mitigation**: Implement input length limits before parsing:

```python
MAX_INPUT_LENGTH = 1000

def safe_parse_email(text: str) -> Maybe[EmailAddress]:
    if len(text) > MAX_INPUT_LENGTH:
        return Failure("Input too long")
    return parsers.parse_email(text)
```

### Error Messages

Parser error messages are designed to be user-friendly but may contain details about why validation failed. In security-sensitive contexts, consider sanitizing error messages before displaying to end users.

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
