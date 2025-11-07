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

**Framework Integrations**: Built-in support for Pydantic (always included) and optional Click integration for CLI apps.

**Interactive Prompts**: Built-in user input prompting with automatic retry and validation.

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

**Advanced**:
- `parse_enum` (type-safe enum parsing)
- `create_parser`, `make_parser`, `validated_parser` (custom parser factories)

### Validators

**Numeric**: `minimum`, `maximum`, `between`

**String**: `non_empty_string`, `matches_regex`, `length`

**Collection**: `in_set`, `unique_items`, `subset_of`, `superset_of`, `is_sorted`

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

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Quick links**:
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Development Setup](CONTRIBUTING.md#development-setup)
- [Commit Message Format](CONTRIBUTING.md#commit-messages)
- [Pull Request Process](CONTRIBUTING.md#pull-request-process)

### Development Quick Start

```bash
# Install uv (fast dependency manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install dependencies
git clone https://github.com/mikelane/valid8r
cd valid8r
uv sync

# Run tests
uv run tox

# Run linters
uv run ruff check .
uv run ruff format .
uv run mypy valid8r
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
