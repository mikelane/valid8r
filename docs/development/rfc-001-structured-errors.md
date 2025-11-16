# RFC-001: Structured Error Model

**Status**: Draft
**Created**: 2025-11-15
**Author**: Claude Code (community RFC)
**Related Issue**: #24

## Summary

Design a structured error model that can carry error codes, messages, field paths, and context while maintaining backward compatibility with the current `Maybe[T]` type.

## Motivation

### Current State

Valid8r currently uses a simple `Maybe[T]` monad with two variants:
- `Success(value: T)` - Contains a successfully parsed/validated value
- `Failure(error: str)` - Contains a simple error message string

**Limitations**:
1. **No error codes**: Cannot programmatically distinguish error types
2. **No field paths**: Multi-field validation cannot indicate which field failed
3. **No context**: Cannot attach additional debugging information
4. **No error accumulation**: Fails on first error (fail-fast only)
5. **Limited machine readability**: String parsing required for error categorization

### Use Cases Requiring Structured Errors

**1. Schema API (Issue #15)**
```python
schema = Schema({
    'age': parse_int & minimum(0),
    'email': parse_email,
    'tags': parse_list(parse_str) & unique_items()
})

result = schema.validate({'age': '-1', 'email': 'invalid', 'tags': ['a', 'a']})
# Need: Multiple errors with paths: '.age', '.email', '.tags'
```

**2. API Error Responses**
```python
# Frontend needs structured error format:
{
    "errors": [
        {"code": "INVALID_EMAIL", "field": "email", "message": "..."},
        {"code": "OUT_OF_RANGE", "field": "age", "message": "..."}
    ]
}
```

**3. Dataclass Validation (Issue #16)**
```python
@validated_dataclass
class User:
    name: str = field(validators=[length(1, 100)])
    age: int = field(validators=[minimum(0), maximum(120)])

# Need field-level error reporting
```

**4. Internationalization (i18n)**
```python
# Error codes enable translation
if error.code == 'MINIMUM_VALUE':
    return translate(error.code, locale, **error.context)
```

## Proposal

### 1. Structured Error Type

```python
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class ValidationError:
    """Structured validation error with code, message, path, and context."""

    code: str
    """Machine-readable error code (e.g., 'INVALID_EMAIL', 'OUT_OF_RANGE')"""

    message: str
    """Human-readable error message"""

    path: str = ''
    """JSON path to the field that failed (e.g., '.user.email', '.items[0].name')"""

    context: dict[str, Any] | None = None
    """Additional context (e.g., {'min': 0, 'max': 100, 'value': 150})"""

    def __str__(self) -> str:
        """Human-readable representation."""
        prefix = f'{self.path}: ' if self.path else ''
        return f'{prefix}{self.message}'

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'code': self.code,
            'message': self.message,
            'path': self.path,
            'context': self.context or {},
        }
```

### 2. Enhanced Maybe Type

**Option A: Extend Failure to accept ValidationError**

```python
from typing import Generic, TypeVar

T = TypeVar('T')

class Maybe(Generic[T]):
    """Existing Maybe monad with enhanced Failure support."""

    @staticmethod
    def success(value: T) -> 'Success[T]':
        return Success(value)

    @staticmethod
    def failure(error: str | ValidationError) -> 'Failure[T]':
        """Create failure from string or ValidationError."""
        return Failure(error)

class Failure(Maybe[T]):
    def __init__(self, error: str | ValidationError):
        if isinstance(error, str):
            # Backward compatibility: wrap string in ValidationError
            self._error = ValidationError(
                code='VALIDATION_ERROR',
                message=error,
                path='',
                context=None
            )
        else:
            self._error = error

    @property
    def error(self) -> ValidationError:
        """Get structured error."""
        return self._error

    def error_or(self, default: str) -> str:
        """Backward compatible: return error message string."""
        return self._error.message
```

**Benefits**:
- ✅ Backward compatible (string errors still work)
- ✅ Gradual migration (parsers can return strings initially)
- ✅ Existing code continues to work (`error_or()` returns string)

**Drawbacks**:
- ⚠️ Type signature unchanged (can't distinguish in type system)
- ⚠️ Accessing structured data requires knowing it's a ValidationError

**Option B: New Result[T, E] type**

```python
from typing import Generic, TypeVar

T = TypeVar('T')
E = TypeVar('E')

class Result(Generic[T, E]):
    """Result type with custom error type."""

    @staticmethod
    def ok(value: T) -> 'Ok[T, E]':
        return Ok(value)

    @staticmethod
    def err(error: E) -> 'Err[T, E]':
        return Err(error)

# Usage:
Result[int, ValidationError]  # Explicit error type
Result[int, list[ValidationError]]  # Multiple errors
```

**Benefits**:
- ✅ Type-safe error handling
- ✅ Explicit about error type
- ✅ Supports error accumulation naturally

**Drawbacks**:
- ❌ Breaking change (new API)
- ❌ Migration burden for existing users
- ❌ Two error handling patterns in codebase

### 3. Error Codes Registry

**Standard Error Codes**:

```python
class ErrorCode:
    """Standard validation error codes."""

    # Parsing errors
    INVALID_TYPE = 'INVALID_TYPE'
    INVALID_FORMAT = 'INVALID_FORMAT'
    PARSE_ERROR = 'PARSE_ERROR'

    # Numeric validators
    OUT_OF_RANGE = 'OUT_OF_RANGE'
    BELOW_MINIMUM = 'BELOW_MINIMUM'
    ABOVE_MAXIMUM = 'ABOVE_MAXIMUM'

    # String validators
    TOO_SHORT = 'TOO_SHORT'
    TOO_LONG = 'TOO_LONG'
    PATTERN_MISMATCH = 'PATTERN_MISMATCH'
    EMPTY_STRING = 'EMPTY_STRING'

    # Collection validators
    NOT_IN_SET = 'NOT_IN_SET'
    DUPLICATE_ITEMS = 'DUPLICATE_ITEMS'
    INVALID_SUBSET = 'INVALID_SUBSET'

    # Network validators
    INVALID_EMAIL = 'INVALID_EMAIL'
    INVALID_URL = 'INVALID_URL'
    INVALID_IP = 'INVALID_IP'
    INVALID_PHONE = 'INVALID_PHONE'

    # Filesystem validators
    PATH_NOT_FOUND = 'PATH_NOT_FOUND'
    NOT_A_FILE = 'NOT_A_FILE'
    NOT_A_DIRECTORY = 'NOT_A_DIRECTORY'
    FILE_TOO_LARGE = 'FILE_TOO_LARGE'

    # DoS protection
    INPUT_TOO_LONG = 'INPUT_TOO_LONG'

    # Custom
    CUSTOM_ERROR = 'CUSTOM_ERROR'
```

### 4. Migration Strategy

**Phase 1: Add ValidationError class (Non-breaking)**
- Introduce `ValidationError` dataclass
- Keep existing `Maybe[T]` API unchanged
- Internal use only

**Phase 2: Update Failure to accept ValidationError (Non-breaking)** ✅ **COMPLETED**
- ✅ `Failure` constructor accepts `str | ValidationError`
- ✅ Strings auto-wrapped in `ValidationError`
- ✅ `error_or()` continues to return strings
- ✅ Added `error_detail()` method to access `ValidationError`
- ✅ Added `validation_error` property (backward compatibility)
- ✅ Comprehensive docstrings with examples
- ✅ Full test coverage including edge cases

**Phase 3: Migrate parsers/validators (Gradual)**
- Update validators to return `ValidationError` objects
- Preserve backward compatibility (both work)
- Deprecation warnings for string-only errors (opt-in via flag)

**Phase 4: Schema API & error accumulation (New feature)**
- Build Schema API using `list[ValidationError]`
- New `validate_all()` mode for collecting all errors
- Separate API from existing `Maybe`-based parsers

**Phase 5: Stabilize & document (v1.0)**
- All parsers/validators return `ValidationError`
- Comprehensive migration guide
- `Maybe[T]` remains primary API (backward compatible)

### 5. Example Usage

**Before (current)**:
```python
result = parse_int('not a number')
match result:
    case Failure(err):
        print(err)  # "Input must be a valid integer"
```

**After (enhanced - Phase 2 COMPLETED)**:
```python
result = parse_int('not a number')
match result:
    case Failure(err):
        # Backward compatible
        print(err.error_or(''))  # "Input must be a valid integer"

        # New structured access (RFC-001 Phase 2)
        detail = err.error_detail()
        print(detail.code)  # "INVALID_TYPE"
        print(detail.message)  # "Input must be a valid integer"
        print(detail.context)  # {'input': 'not a number', 'expected': 'int'}

        # Alternative: validation_error property (also available)
        error = err.validation_error
        print(error.code)  # "INVALID_TYPE"
```

**Schema API (new feature)**:
```python
from valid8r.schema import Schema

schema = Schema({
    'age': parse_int & minimum(0),
    'email': parse_email,
})

result = schema.validate({'age': '-1', 'email': 'bad'})
match result:
    case Err(errors):  # list[ValidationError]
        for error in errors:
            print(f'{error.path}: {error.message}')
        # Output:
        # .age: Must be at least 0
        # .email: Invalid email address format
```

## Alternatives Considered

### Alternative 1: Keep strings, add error dict

**Idea**: Keep `Failure(error: str)`, add optional `Failure(error: str, details: dict)`

**Rejected because**:
- Awkward API (two parameters for one concept)
- Doesn't solve path/code issues cleanly
- Still requires migration for accumulation

### Alternative 2: Exceptions-based errors

**Idea**: Use Python exceptions for validation errors

**Rejected because**:
- Breaks functional programming model
- Exceptions are for exceptional cases, not expected validation failures
- Monadic composition (bind/map) wouldn't work
- Against project philosophy (explicit error handling)

### Alternative 3: External error registry

**Idea**: Errors return codes, messages live in separate registry

**Rejected because**:
- Complicates API (lookup required)
- Harder to customize error messages
- Context would still need to be attached somewhere

## Open Questions

1. **Should we introduce `Result[T, E]` or enhance `Maybe[T]`?**
   - **Recommendation**: Start with enhanced `Maybe[T]` for backward compatibility
   - Consider `Result[T, E]` for Schema API specifically

2. **How to handle error accumulation?**
   - **Recommendation**: New API surface (Schema.validate_all())
   - Returns `Result[T, list[ValidationError]]` instead of `Maybe[T]`

3. **Should error codes be an enum or strings?**
   - **Recommendation**: Strings (extensible, user-defined codes possible)
   - Provide `ErrorCode` constants for standard codes

4. **How to maintain backward compatibility for `error_or()`?**
   - **Recommendation**: `error_or()` always returns the message string
   - Add `error_detail()` method to access full `ValidationError`

5. **Should paths use JSON path or dot notation?**
   - **Recommendation**: Dot notation (simpler, matches Python)
   - Examples: `.user.email`, `.items[0].name`

## Implementation Plan

### Milestone 1: Foundation (1-2 weeks)
- [ ] Create `ValidationError` dataclass
- [ ] Create `ErrorCode` constants
- [ ] Update `Failure` to accept `ValidationError`
- [ ] Add backward compatibility tests
- [ ] Document migration strategy

### Milestone 2: Core Migration (2-3 weeks)
- [ ] Migrate all parsers to return `ValidationError`
- [ ] Migrate all validators to return `ValidationError`
- [ ] Update all tests
- [ ] Performance benchmarks (ensure no regression)

### Milestone 3: Schema API (3-4 weeks)
- [ ] Design Schema API
- [ ] Implement error accumulation
- [ ] Field path tracking
- [ ] Comprehensive tests
- [ ] Documentation

### Milestone 4: Polish & Release (1 week)
- [ ] Migration guide
- [ ] Example code updates
- [ ] Blog post/announcement
- [ ] v1.0.0-beta release

**Total Timeline**: 7-10 weeks

## Success Criteria

1. ✅ Existing code continues to work without changes
2. ✅ `error_or()` behavior unchanged
3. ✅ New code can access structured errors
4. ✅ Schema API can collect multiple errors
5. ✅ Error codes enable programmatic handling
6. ✅ Field paths enable UI error display
7. ✅ Context enables helpful error messages
8. ✅ Performance impact < 5%

## References

- Issue #15: Schema API with error accumulation
- Issue #16: Dataclass integration
- Pydantic ValidationError: https://docs.pydantic.dev/latest/errors/errors/
- Rust Result type: https://doc.rust-lang.org/std/result/
- Railway Oriented Programming: https://fsharpforfunandprofit.com/rop/

## Feedback

Please provide feedback on this RFC via:
- GitHub Discussions: https://github.com/mikelane/valid8r/discussions
- Comment on Issue #24: https://github.com/mikelane/valid8r/issues/24

Key questions for community:
1. Enhance `Maybe[T]` or introduce `Result[T, E]`?
2. Error codes as enums or strings?
3. Any use cases we're missing?
4. Migration concerns?
