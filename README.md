# Valid8r

[![PyPI version](https://img.shields.io/pypi/v/valid8r.svg)](https://pypi.org/project/valid8r/)
[![Python versions](https://img.shields.io/pypi/pyversions/valid8r.svg)](https://pypi.org/project/valid8r/)
[![License](https://img.shields.io/github/license/mikelane/valid8r.svg)](https://github.com/mikelane/valid8r/blob/main/LICENSE)
[![CI](https://github.com/mikelane/valid8r/actions/workflows/ci.yml/badge.svg)](https://github.com/mikelane/valid8r/actions/workflows/ci.yml)
[![Release](https://github.com/mikelane/valid8r/actions/workflows/release.yml/badge.svg)](https://github.com/mikelane/valid8r/actions/workflows/release.yml)
[![codecov](https://codecov.io/gh/mikelane/valid8r/branch/main/graph/badge.svg)](https://codecov.io/gh/mikelane/valid8r)
[![Documentation](https://img.shields.io/readthedocs/valid8r.svg)](https://valid8r.readthedocs.io/)

**Clean, composable input validation for Python using functional programming patterns.**

Valid8r makes input validation elegant and type-safe by using the Maybe monad for error handling. No more try-except blocks or boolean validation chains—just clean, composable parsers that tell you exactly what went wrong.

```python
from valid8r import parsers, validators, prompt

# Parse and validate user input with rich error messages
age = prompt.ask(
    "Enter your age: ",
    parser=parsers.parse_int,
    validator=validators.minimum(0) & validators.maximum(120)
)

print(f"Your age is {age}")
```

## Why Valid8r?

**Type-Safe Parsing**: Every parser returns `Maybe[T]` (Success or Failure), making error handling explicit and composable.

**Rich Structured Results**: Network parsers return dataclasses with parsed components—no more manual URL/email splitting.

**Chainable Validators**: Combine validators using `&` (and), `|` (or), and `~` (not) operators for complex validation logic.

**Security-First Design**: All parsers include DoS protection via input length validation and automated ReDoS detection prevents vulnerable regex patterns.

**Framework Integrations**: Built-in support for Pydantic (always included) and optional Click integration for CLI apps.

**Interactive Prompts**: Built-in user input prompting with automatic retry and validation.

**High Performance**: Valid8r is [4-300x faster than Pydantic](docs/performance.md) for basic parsing, making it ideal for high-throughput APIs and batch processing.

## Performance

Valid8r is designed for high-performance validation with minimal overhead:

| Scenario | valid8r | Pydantic | Speedup |
|----------|---------|----------|---------|
| Integer parsing | 375ns | 102µs | **273x faster** |
| Nested objects | 37µs | 568µs | **15x faster** |
| List (100 items) | 30µs | 126µs | **4x faster** |

**When to use valid8r**:
- High-throughput APIs (>5K requests/sec)
- Batch processing pipelines
- CLI tools requiring structured parsing
- Performance-critical code paths

**When to use Pydantic**:
- FastAPI applications (tight integration)
- Complex data models with auto-schema generation
- Developer experience > raw performance

**Full benchmarks and methodology**: [docs/performance.md](docs/performance.md)

## Quick Start

### Installation

**Basic installation** (includes Pydantic integration):
```bash
pip install valid8r
```

**With optional framework integrations**:
```bash
# Click integration for CLI applications
pip install 'valid8r[click]'

# All optional integrations
pip install 'valid8r[click]'
```

**Requirements**: Python 3.11 or higher

| Feature | Installation | Import |
|---------|--------------|--------|
| Core parsers & validators | `pip install valid8r` | `from valid8r import parsers, validators` |
| Pydantic integration | _included by default_ | `from valid8r.integrations import validator_from_parser` |
| Click integration (CLI) | `pip install 'valid8r[click]'` | `from valid8r.integrations import ParamTypeAdapter` |

### Basic Parsing

```python
from valid8r import parsers
from valid8r.core.maybe import Success, Failure

# Parse integers with automatic error handling
match parsers.parse_int("42"):
    case Success(value):
        print(f"Parsed: {value}")  # Parsed: 42
    case Failure(error):
        print(f"Error: {error}")

# Parse dates (ISO 8601 format)
result = parsers.parse_date("2025-01-15")
assert result.is_success()

# Parse UUIDs with version validation
result = parsers.parse_uuid("550e8400-e29b-41d4-a716-446655440000", version=4)
assert result.is_success()
```

### Temporal Parsing

```python
from valid8r import parsers
from datetime import UTC

# Parse timezone-aware datetime (ISO 8601)
result = parsers.parse_datetime("2024-01-15T10:30:00Z")
match result:
    case Success(dt):
        print(f"DateTime: {dt}")  # 2024-01-15 10:30:00+00:00
        print(f"Timezone: {dt.tzinfo}")  # UTC
    case Failure(error):
        print(f"Error: {error}")

# Parse with timezone offset
result = parsers.parse_datetime("2024-01-15T10:30:00+05:30")
assert result.is_success()

# Parse duration/timedelta in multiple formats
result = parsers.parse_timedelta("1h 30m")  # Simple format
assert result.value_or(None).total_seconds() == 5400

result = parsers.parse_timedelta("PT1H30M")  # ISO 8601 duration
assert result.value_or(None).total_seconds() == 5400
```

### Validation with Combinators

```python
from valid8r import validators

# Combine validators using operators
age_validator = validators.minimum(0) & validators.maximum(120)
result = age_validator(42)
assert result.is_success()

# String validation
password_validator = (
    validators.length(8, 128) &
    validators.matches_regex(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]')
)

# Set validation
tags_validator = validators.subset_of({'python', 'rust', 'go', 'typescript'})
```

### Structured Network Parsing

```python
from valid8r import parsers

# Parse URLs into structured components
match parsers.parse_url("https://user:pass@example.com:8443/path?query=1#fragment"):
    case Success(url):
        print(f"Scheme: {url.scheme}")      # https
        print(f"Host: {url.host}")          # example.com
        print(f"Port: {url.port}")          # 8443
        print(f"Path: {url.path}")          # /path
        print(f"Query: {url.query}")        # {'query': '1'}
        print(f"Fragment: {url.fragment}")  # fragment

# Parse emails with normalized domains
match parsers.parse_email("User@Example.COM"):
    case Success(email):
        print(f"Local: {email.local}")    # User
        print(f"Domain: {email.domain}")  # example.com (normalized)

# Parse phone numbers (NANP format)
match parsers.parse_phone("+1 (415) 555-2671"):
    case Success(phone):
        print(f"E.164: {phone.e164}")      # +14155552671
        print(f"National: {phone.national}")  # (415) 555-2671
```

### Collection Parsing

```python
from valid8r import parsers

# Parse lists with element validation
result = parsers.parse_list("1,2,3,4,5", element_parser=parsers.parse_int)
assert result.value_or([]) == [1, 2, 3, 4, 5]

# Parse dictionaries with key/value parsers
result = parsers.parse_dict(
    "name=Alice,age=30",
    key_parser=lambda x: Success(x),
    value_parser=lambda x: parsers.parse_int(x) if x.isdigit() else Success(x)
)
```

### Type-Based Parser Generation

Automatically generate parsers from Python type annotations:

```python
from typing import Annotated, Literal, Optional
from valid8r.core.type_adapters import from_type
from valid8r import validators

# Generate parser from type annotation
parser = from_type(int)
result = parser('42')
assert result.value_or(None) == 42

# Optional types handle None automatically
parser = from_type(Optional[int])
assert parser('').value_or('not none') is None  # Empty string becomes None
assert parser('42').value_or(None) == 42

# Collections with element validation
parser = from_type(list[int])
result = parser('[1, 2, 3, 4, 5]')
assert result.value_or([]) == [1, 2, 3, 4, 5]

# Nested structures
parser = from_type(dict[str, list[int]])
result = parser('{"scores": [95, 87, 92]}')
assert result.value_or({}) == {'scores': [95, 87, 92]}

# Combine types with validators using Annotated
Age = Annotated[int, validators.minimum(0), validators.maximum(120)]
parser = from_type(Age)
assert parser('25').value_or(None) == 25
assert parser('150').is_failure()  # Exceeds maximum

# Literal types for restricted values
parser = from_type(Literal['red', 'green', 'blue'])
assert parser('red').value_or(None) == 'red'
assert parser('yellow').is_failure()  # Not in literal set
```

**Security**: All collection parsers include automatic DoS protection—inputs exceeding 100KB are rejected in <10ms before expensive JSON parsing.

### Filesystem Parsing and Validation

```python
from valid8r import parsers, validators
from valid8r.core.maybe import Success, Failure

# Parse and validate file paths
match parsers.parse_path("/etc/hosts").bind(validators.exists()).bind(validators.is_file()):
    case Success(path):
        print(f"Valid file: {path}")
    case Failure(err):
        print(f"Error: {err}")

# Validate uploaded files
def validate_upload(file_path: str):
    return (
        parsers.parse_path(file_path)
        .bind(validators.exists())
        .bind(validators.is_file())
        .bind(validators.has_extension(['.pdf', '.docx']))
        .bind(validators.max_size(10 * 1024 * 1024))  # 10MB limit
    )

# Path expansion and resolution
match parsers.parse_path("~/Documents", expand_user=True):
    case Success(path):
        print(f"Expanded: {path}")  # /Users/username/Documents

match parsers.parse_path("./data/file.txt", resolve=True):
    case Success(path):
        print(f"Absolute: {path}")  # /full/path/to/data/file.txt
```

### Interactive Prompting

```python
from valid8r import prompt, parsers, validators

# Prompt with validation and automatic retry
email = prompt.ask(
    "Email address: ",
    parser=parsers.parse_email,
    retry=2  # Retry twice on invalid input
)

# Combine parsing and validation
port = prompt.ask(
    "Server port: ",
    parser=parsers.parse_int,
    validator=validators.between(1024, 65535),
    retry=3
)
```

### Structured Error Handling

Valid8r provides machine-readable error codes and structured error information for programmatic error handling and API responses:

```python
from valid8r import parsers
from valid8r.core.maybe import Success, Failure
from valid8r.core.errors import ErrorCode

# Programmatic error handling using error codes
def process_email(email_str: str):
    result = parsers.parse_email(email_str)

    match result:
        case Success(email):
            return f"Valid: {email.local}@{email.domain}"
        case Failure():
            # Access structured error for programmatic handling
            detail = result.error_detail()

            # Switch on error codes for different handling
            match detail.code:
                case ErrorCode.INVALID_EMAIL:
                    return "Please enter a valid email address"
                case ErrorCode.EMPTY_STRING:
                    return "Email is required"
                case ErrorCode.INPUT_TOO_LONG:
                    return "Email is too long"
                case _:
                    return f"Error: {detail.message}"

# Convert errors to JSON for API responses
result = parsers.parse_int("not-a-number")
match result:
    case Failure():
        error_dict = result.error_detail().to_dict()
        # {
        #   'code': 'INVALID_TYPE',
        #   'message': 'Input must be a valid integer',
        #   'path': '',
        #   'context': {}
        # }
```

**Features:**

- Error codes for programmatic handling (e.g., `ErrorCode.INVALID_EMAIL`, `ErrorCode.OUT_OF_RANGE`)
- JSON serialization for API responses via `to_dict()`
- Field paths for multi-field validation (e.g., `.user.email`)
- Debugging context with validation parameters
- 100% backward compatible with string errors

See the [Error Handling Guide](https://valid8r.readthedocs.io/en/latest/user_guide/error_handling.html) for comprehensive examples and best practices.


### Async Validation

Validate data using async validators for I/O-bound operations like database checks, API calls, and external service validation:

```python
import asyncio
from valid8r.core import parsers, schema, validators
from valid8r.core.maybe import Success, Failure

# Define async validator
async def check_email_unique(email: str) -> Maybe[str]:
    """Check if email is unique in database."""
    # Simulate database query
    await asyncio.sleep(0.1)
    existing_emails = {'admin@example.com', 'user@example.com'}

    if email in existing_emails:
        return Maybe.failure('Email already registered')
    return Maybe.success(email)

# Create schema with async validators
user_schema = schema.Schema(fields={
    'email': schema.Field(
        parser=parsers.parse_email,
        validators=[
            validators.min_length(1),  # Sync validator (fail-fast)
            check_email_unique,  # Async validator (database check)
        ],
        required=True
    ),
    'username': schema.Field(
        parser=parsers.parse_str,
        validators=[
            validators.matches_pattern(r'^[a-z0-9_]+$'),
            check_username_available,  # Another async validator
        ],
        required=True
    ),
})

# Validate asynchronously with timeout
async def main():
    result = await user_schema.validate_async(
        {'email': 'new@example.com', 'username': 'newuser'},
        timeout=5.0
    )

    match result:
        case Success(data):
            print(f"Valid: {data}")
        case Failure(errors):
            for error in errors:
                print(f"{error.path}: {error.message}")

asyncio.run(main())
```

**Key Features:**

- Concurrent execution of async validators across fields for better performance
- Mixed sync and async validators (sync runs first for fail-fast behavior)
- Configurable timeout support to prevent hanging on slow operations
- Full error accumulation across all fields
- Works seamlessly with existing sync validators

**Common Use Cases:**

- Database uniqueness checks (email, username)
- External API validation (API keys, payment methods)
- Geolocation constraints (IP address country verification)
- Remote file access validation
- Any I/O-bound validation operation

See the [Async Validation Guide](https://valid8r.readthedocs.io/en/latest/user_guide/async_validation.html) for comprehensive examples including database integration, API validation, and performance optimization patterns.
### Environment Variables

Load typed, validated configuration from environment variables following 12-factor app principles:

```python
from valid8r.integrations.env import EnvSchema, EnvField, load_env_config
from valid8r import parsers, validators
from valid8r.core.maybe import Success, Failure

# Define configuration schema
schema = EnvSchema(fields={
    'port': EnvField(
        parser=lambda x: parsers.parse_int(x).bind(validators.between(1024, 65535)),
        default=8080
    ),
    'debug': EnvField(parser=parsers.parse_bool, default=False),
    'database_url': EnvField(parser=parsers.parse_str, required=True),
    'admin_email': EnvField(parser=parsers.parse_email, required=True),
})

# Load and validate configuration
result = load_env_config(schema, prefix='APP_')

match result:
    case Success(config):
        # All values are typed and validated
        port = config['port']              # int (validated 1024-65535)
        debug = config['debug']            # bool (not str!)
        db = config['database_url']        # str (required, guaranteed present)
        email = config['admin_email']      # EmailAddress (validated format)
    case Failure(error):
        print(f"Configuration error: {error}")
```

**Features:**

- Type-safe parsing (no more string-to-int conversions)
- Declarative validation with composable parsers
- Required vs optional fields with sensible defaults
- Nested schemas for hierarchical configuration
- Clear error messages for missing or invalid values

See [Environment Variables Guide](https://valid8r.readthedocs.io/en/latest/examples/environment_variables.html) for complete examples including FastAPI, Docker, and Kubernetes deployment patterns.

### Framework Integrations

#### Pydantic Integration (Always Included)

Convert valid8r parsers into Pydantic field validators:

```python
from pydantic import BaseModel, field_validator
from valid8r import parsers, validators
from valid8r.integrations import validator_from_parser

class User(BaseModel):
    age: int

    @field_validator('age', mode='before')
    @classmethod
    def validate_age(cls, v):
        # Parse string to int, then validate 0-120 range
        age_parser = lambda x: parsers.parse_int(x).bind(
            validators.between(0, 120)
        )
        return validator_from_parser(age_parser)(v)

user = User(age="25")  # Accepts string, validates, returns int
```

Works seamlessly with nested models, lists, and complex Pydantic schemas. See [Pydantic Integration Examples](https://valid8r.readthedocs.io/en/latest/examples/pydantic_integration.html).

#### Click Integration (Optional)

Install: `pip install 'valid8r[click]'`

Integrate valid8r parsers into Click CLI applications:

```python
import click
from valid8r import parsers
from valid8r.integrations import ParamTypeAdapter

@click.command()
@click.option('--email', type=ParamTypeAdapter(parsers.parse_email))
def send_mail(email):
    """Send an email with validated address."""
    click.echo(f"Sending to {email.local}@{email.domain}")

# Automatically validates email format and provides rich error messages
```

See [Click Integration Examples](https://valid8r.readthedocs.io/en/latest/examples/click_integration.html).

## Features

### Parsers

**Basic Types**:
- `parse_int`, `parse_float`, `parse_bool`, `parse_decimal`, `parse_complex`
- `parse_date` (ISO 8601), `parse_uuid` (with version validation)

**Collections**:
- `parse_list`, `parse_dict`, `parse_set` (with element parsers)

**Network & Communication**:
- `parse_ipv4`, `parse_ipv6`, `parse_ip`, `parse_cidr`
- `parse_url` → `UrlParts` (structured URL components)
- `parse_email` → `EmailAddress` (normalized domain)
- `parse_phone` → `PhoneNumber` (NANP validation with E.164 formatting)

**Filesystem**:
- `parse_path` → `pathlib.Path` (with expansion and resolution options)

**Advanced**:
- `parse_enum` (type-safe enum parsing)
- `create_parser`, `make_parser`, `validated_parser` (custom parser factories)

### Validators

**Numeric**: `minimum`, `maximum`, `between`

**String**: `non_empty_string`, `matches_regex`, `length`

**Collection**: `in_set`, `unique_items`, `subset_of`, `superset_of`, `is_sorted`

**Filesystem**: `exists`, `is_file`, `is_dir`, `is_readable`, `is_writable`, `is_executable`, `max_size`, `min_size`, `has_extension`

**Custom**: `predicate` (create validators from any function)

**Combinators**: Combine validators using `&` (and), `|` (or), `~` (not)

### Testing Utilities

```python
from valid8r.testing import (
    assert_maybe_success,
    assert_maybe_failure,
    MockInputContext,
)

# Test validation logic
result = validators.minimum(0)(42)
assert assert_maybe_success(result, 42)

result = validators.minimum(0)(-5)
assert assert_maybe_failure(result, "at least 0")

# Mock user input for testing prompts
with MockInputContext(["invalid", "valid@example.com"]):
    result = prompt.ask("Email: ", parser=parsers.parse_email, retry=1)
    assert result.is_success()
```

## Documentation

**Full documentation**: [valid8r.readthedocs.io](https://valid8r.readthedocs.io/)

- [Library Comparison Guide](docs/comparison.md) - When to choose valid8r vs Pydantic/marshmallow/cerberus
- [API Reference](https://valid8r.readthedocs.io/en/latest/api.html)
- [Parser Guide](https://valid8r.readthedocs.io/en/latest/parsers.html)
- [Validator Guide](https://valid8r.readthedocs.io/en/latest/validators.html)
- [Testing Guide](https://valid8r.readthedocs.io/en/latest/testing.html)

## Security

### Reporting Vulnerabilities

**Please do not report security vulnerabilities through public GitHub issues.**

Report security issues privately to **mikelane@gmail.com** or via [GitHub Security Advisories](https://github.com/mikelane/valid8r/security/advisories/new).

See [SECURITY.md](SECURITY.md) for our complete security policy, supported versions, and response timeline.

### Production Deployment

Valid8r is designed for parsing **trusted user input** in web applications. For production deployments:

1. **Enforce input size limits** at the framework level (recommended: 10KB max request size)
2. **Implement rate limiting** for validation endpoints (recommended: 10 requests/minute)
3. **Use defense in depth**: Framework → Application → Parser validation
4. **Monitor and log** validation failures for security analysis

**Example - Flask Defense in Depth:**

```python
from flask import Flask, request
from valid8r import parsers

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024  # Layer 1: Framework limit

@app.route('/submit', methods=['POST'])
def submit():
    phone = request.form.get('phone', '')

    # Layer 2: Application validation
    if len(phone) > 100:
        return "Phone too long", 400

    # Layer 3: Parser validation
    result = parsers.parse_phone(phone)
    if result.is_failure():
        return "Invalid phone format", 400

    return process_phone(result.value_or(None))
```

See [Production Deployment Guide](docs/security/production-deployment.md) for framework-specific examples (Flask, Django, FastAPI).

### Security Boundaries

Valid8r provides **input validation**, not protection against:

- ❌ SQL injection - Use parameterized queries / ORMs
- ❌ XSS attacks - Use output encoding / template engines
- ❌ CSRF attacks - Use CSRF tokens / SameSite cookies
- ❌ DDoS attacks - Use rate limiting / CDN / WAF

**Parser Input Limits:**

| Parser | Max Input | Notes |
|--------|-----------|-------|
| `parse_email()` | 254 chars | RFC 5321 maximum |
| `parse_phone()` | 100 chars | International + extension |
| `parse_url()` | 2048 chars | Browser URL limit |
| `parse_uuid()` | 36 chars | Standard UUID format |
| `parse_ip()` | 45 chars | IPv6 maximum |

All parsers include built-in DoS protection with early length validation before expensive operations.

See [SECURITY.md](SECURITY.md) for complete security documentation.

## Community

Join the Valid8r community on GitHub Discussions:

- **Questions?** Start a discussion in [Q&A](https://github.com/mikelane/valid8r/discussions/categories/q-a)
- **Feature ideas?** Share them in [Ideas](https://github.com/mikelane/valid8r/discussions/categories/ideas)
- **Built something cool?** Show it off in [Show and Tell](https://github.com/mikelane/valid8r/discussions/categories/show-and-tell)
- **Announcements**: Watch [Announcements](https://github.com/mikelane/valid8r/discussions/categories/announcements) for updates

**When to use Discussions vs Issues:**
- Use **Discussions** for questions, ideas, and general conversation
- Use **Issues** for bug reports and feature requests with technical specifications

See the [Welcome Discussion](https://github.com/mikelane/valid8r/discussions/175) for community guidelines.

## Contributing

We welcome contributions! **All contributions must be made via forks** - please do not create branches directly in the main repository.

See [CONTRIBUTING.md](CONTRIBUTING.md) for complete guidelines.

**Quick links**:
- [Fork-Based Workflow Requirement](CONTRIBUTING.md#fork-based-contributions-required)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Development Setup](CONTRIBUTING.md#development-setup)
- [Commit Message Format](CONTRIBUTING.md#commit-messages)
- [Pull Request Process](CONTRIBUTING.md#pull-request-process)

### Development Quick Start

```bash
# 1. Fork the repository on GitHub
#    Visit: https://github.com/mikelane/valid8r

# 2. Clone YOUR fork (not the upstream repo)
git clone https://github.com/YOUR-USERNAME/valid8r
cd valid8r

# 3. Add upstream remote
git remote add upstream https://github.com/mikelane/valid8r.git

# 4. Install uv (fast dependency manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 5. Install dependencies
uv sync

# 6. Run tests
uv run tox

# 7. Run linters
uv run ruff check .
uv run ruff format .
uv run mypy valid8r

# 8. Create a feature branch and make your changes
git checkout -b feat/your-feature

# 9. Push to YOUR fork and create a PR
git push origin feat/your-feature
```

## Project Status

Valid8r is in active development (v0.7.x). The API is stabilizing but may change before v1.0.0.

- ✅ Core parsers and validators
- ✅ Maybe monad error handling
- ✅ Interactive prompting
- ✅ Network parsers (URL, Email, IP, Phone)
- ✅ Collection parsers
- ✅ Comprehensive testing utilities
- 🚧 Additional validators (in progress)
- 🚧 Custom error types (planned)

See [ROADMAP.md](ROADMAP.md) for planned features.

## License

MIT License - see [LICENSE](LICENSE) for details.

Copyright (c) 2025 Mike Lane

---

**Made with ❤️ for the Python community**
