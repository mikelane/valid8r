# Secure Parser Development Guidelines

This document provides guidelines for developing secure parsers in valid8r to prevent Denial of Service (DoS) vulnerabilities and other security issues.

## Table of Contents

1. [Overview](#overview)
2. [DoS Prevention](#dos-prevention)
3. [Input Validation Order](#input-validation-order)
4. [Testing Requirements](#testing-requirements)
5. [Error Messages](#error-messages)
6. [Common Patterns](#common-patterns)
7. [References](#references)

## Overview

All parsers in valid8r must follow security-first design principles to prevent resource exhaustion attacks. The primary threat model is:

- **Attacker Goal**: Exhaust server resources (CPU, memory) by sending malicious inputs
- **Attack Vector**: Extremely long strings that trigger expensive operations
- **Impact**: Service degradation or complete denial of service

## DoS Prevention

### Principle: Early Length Guards

**ALWAYS validate input length BEFORE expensive operations:**

```python
def parse_example(text: str) -> Maybe[Example]:
    """Parse example with DoS protection."""
    # 1. Type check
    if not isinstance(text, str):
        return Maybe.failure('Input must be a string')

    # 2. Empty check
    s = text.strip()
    if s == '':
        return Maybe.failure('Input must not be empty')

    # 3. CRITICAL: Early length guard (DoS mitigation)
    # Check BEFORE any expensive operations (regex, external libraries, etc.)
    if len(text) > MAX_LENGTH:
        return Maybe.failure(f'Input is too long (maximum {MAX_LENGTH} characters)')

    # 4. Now safe to perform expensive operations
    # - Regex matching
    # - External library calls
    # - Complex parsing logic
    ...
```

### Maximum Input Lengths

Use RFC standards and industry best practices to determine limits:

| Parser | Max Length | Rationale |
|--------|------------|-----------|
| `parse_email()` | 254 chars | RFC 5321 maximum email address length |
| `parse_url()` | 2048 chars | Browser URL length limit |
| `parse_uuid()` | 45 chars | Standard UUID format (36) + safety margin |
| `parse_ip()` | 45 chars | IPv6 max length |
| `parse_cidr()` | 50 chars | IPv6 + CIDR notation |
| `parse_phone()` | 100 chars | NANP format + extensions + safety margin |
| `parse_slug()` | 255 chars | Database VARCHAR(255) limits |
| `parse_json()` | 1,000,000 chars | 1MB (reasonable API payload) |
| `parse_jwt()` | 10,000 chars | 10KB (typical JWT size) |
| `parse_base64()` | 10,000,000 chars | 10MB (reasonable file size) |

### Performance Threshold

**All parsers must reject malicious input in < 10ms** (< 1ms for simple parsers).

This ensures that even under attack, the server can handle thousands of malicious requests per second without significant resource impact.

## Input Validation Order

Follow this exact order for all parsers:

1. **Type Check**: Verify input is the expected type (usually `str`)
2. **Empty Check**: Reject empty/None inputs
3. **Length Guard**: Check length BEFORE expensive operations (DoS protection)
4. **Library Check**: Verify optional dependencies are available
5. **Expensive Operations**: Regex, external libraries, complex parsing

**Example**:

```python
def parse_secure(text: str) -> Maybe[Result]:
    # 1. Type check
    if not isinstance(text, str):
        return Maybe.failure('Input must be a string')

    # 2. Empty check
    s = text.strip()
    if s == '':
        return Maybe.failure('Input must not be empty')

    # 3. Length guard (CRITICAL - DoS protection)
    if len(text) > MAX_LENGTH:
        return Maybe.failure(f'Input is too long (maximum {MAX_LENGTH} characters)')

    # 4. Library check (if needed)
    if not HAS_LIBRARY:
        return Maybe.failure('Required library not installed')

    # 5. Expensive operations (NOW SAFE)
    try:
        result = expensive_operation(s)
        return Maybe.success(result)
    except LibraryError as e:
        return Maybe.failure(str(e))
```

## Testing Requirements

### Correctness Tests

Every parser must have tests verifying:

1. **Valid inputs** (success cases)
2. **Invalid inputs** (failure cases with correct error messages)
3. **Edge cases** (boundary conditions, empty, whitespace)

### Security Tests

Every parser must have DoS protection tests:

```python
def it_rejects_excessively_long_input(self) -> None:
    """Reject extremely long input to prevent DoS attacks."""
    import time

    # Create malicious input exceeding maximum length
    malicious_input = 'a' * (MAX_LENGTH + 100)

    # Measure rejection time
    start = time.perf_counter()
    result = parse_function(malicious_input)
    elapsed_ms = (time.perf_counter() - start) * 1000

    # Verify correctness
    assert result.is_failure()
    assert 'too long' in result.error_or('').lower()

    # Verify performance (DoS protection)
    assert elapsed_ms < 10, f'Rejection took {elapsed_ms:.2f}ms, should be < 10ms'
```

### Coverage Requirements

- **Line coverage**: 100%
- **Branch coverage**: 100%
- **Mutation coverage**: Strongly recommended

## Error Messages

### User-Facing Messages

Error messages must be:

1. **Clear and actionable**: Tell the user what went wrong and how to fix it
2. **Deterministic**: Same input always produces same error
3. **Length-limited**: Avoid revealing the entire malicious input in error messages
4. **Security-conscious**: Don't leak implementation details

**Good**:
```python
return Maybe.failure('Email address is too long (maximum 254 characters)')
return Maybe.failure('Phone number must have 10 digits, got 8')
return Maybe.failure('Invalid format: phone number contains invalid characters')
```

**Bad**:
```python
return Maybe.failure(f'Input too long: {text}')  # Leaks malicious input
return Maybe.failure('regex match failed')  # Implementation detail
return Maybe.failure('Error')  # Not actionable
```

### Docstring Documentation

Every parser must document:

1. **Rules**: What constitutes valid/invalid input
2. **Maximum length**: Document the limit in the docstring
3. **Failure messages**: List all possible error messages
4. **Examples**: Provide usage examples in doctests

```python
def parse_example(text: str) -> Maybe[Example]:
    """Parse example with security constraints.

    Rules:
    - Maximum length: 254 characters
    - Must contain '@' symbol
    - Cannot start with whitespace

    Failure messages:
    - Input must be a string
    - Input must not be empty
    - Input is too long (maximum 254 characters)
    - Invalid format: missing '@' symbol

    Args:
        text: Input string to parse

    Returns:
        Maybe[Example]: Success with parsed value or Failure with error

    Examples:
        >>> parse_example('valid@input').is_success()
        True
        >>> parse_example('a' * 300).is_failure()
        True
    """
```

## Common Patterns

### Pattern 1: External Library Validation

When using external libraries for validation (e.g., `email-validator`):

```python
def parse_with_library(text: str) -> Maybe[Result]:
    # ALWAYS check length BEFORE calling library
    if len(text) > MAX_LENGTH:
        return Maybe.failure(f'Input is too long (maximum {MAX_LENGTH} characters)')

    try:
        result = external_library.validate(text)
        return Maybe.success(result)
    except LibraryError as e:
        return Maybe.failure(str(e))
```

### Pattern 2: Regex Operations

When using regex for validation/parsing:

```python
# Compile patterns at module level for performance
_PATTERN = re.compile(r'^[a-z0-9-]+$')

def parse_with_regex(text: str) -> Maybe[Result]:
    # ALWAYS check length BEFORE regex operations
    if len(text) > MAX_LENGTH:
        return Maybe.failure(f'Input is too long (maximum {MAX_LENGTH} characters)')

    # Now safe to use regex
    if not _PATTERN.match(text):
        return Maybe.failure('Invalid format')

    return Maybe.success(text)
```

### Pattern 3: Multi-Stage Parsing

When parsing involves multiple stages:

```python
def parse_complex(text: str) -> Maybe[Result]:
    # Check length ONCE at the beginning
    if len(text) > MAX_LENGTH:
        return Maybe.failure(f'Input is too long (maximum {MAX_LENGTH} characters)')

    # All subsequent operations are safe
    stage1 = _parse_stage1(text)  # No need to recheck length
    if stage1.is_failure():
        return stage1

    stage2 = _parse_stage2(stage1.value_or(''))
    return stage2
```

## References

### Security Standards

- **OWASP Top 10 2021**: A04 - Insecure Design
- **CWE-400**: Uncontrolled Resource Consumption
- **RFC 5321**: SMTP (email address length limits)

### Project References

- **Issue #132**: Comprehensive security audit of all parsers
- **Issue #131**: Phone parser DoS vulnerability (fixed in v0.9.1)
- **PR #XXX**: Email parser DoS fix (this PR)

### Testing

- **Tests**: `/tests/security/test_dos_prevention.py`
- **Assessment Script**: `/dos_assessment.py`
- **Audit Report**: `/SECURITY_AUDIT_REPORT.md`

## Checklist for New Parsers

When creating a new parser, verify:

- [ ] Type check is first validation
- [ ] Empty/None input is rejected
- [ ] **Length guard is present BEFORE expensive operations**
- [ ] Maximum length is documented in docstring
- [ ] Error messages are clear and actionable
- [ ] DoS protection test exists (< 10ms rejection)
- [ ] Test coverage is 100% (line + branch)
- [ ] Performance is measured and verified

## Maintenance

This document should be updated when:

- New parsers are added to the library
- New security threats are identified
- Performance thresholds change
- RFC standards are updated
- Best practices evolve

**Last Updated**: 2025-11-05 (Issue #132 DoS audit)
