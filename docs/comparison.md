# Library Comparison Guide

Valid8r is a Python validation library with a unique focus on **CLI applications**, **network data parsing**, and **functional programming patterns**. This guide helps you choose the right validation library for your use case.

## Quick Reference: When to Choose Each Library

| Use Case | Choose This Library |
|----------|-------------------|
| Building a FastAPI REST API | **Pydantic** - Best-in-class FastAPI integration, auto-generated OpenAPI docs |
| Performance-critical data validation (millions of records) | **Pydantic** - Rust-powered core, 5-50x faster than alternatives |
| Flask API with explicit serialization | **marshmallow** - Excellent Flask ecosystem, separate serialize/deserialize |
| Lightweight validation with zero dependencies | **cerberus** - No dependencies, simple dict validation |
| **CLI applications with user prompts** | **valid8r** - Interactive input, automatic retry, rich error messages |
| **Parsing network data (URLs, emails, IPs, phones)** | **valid8r** - Returns structured dataclasses (UrlParts, EmailAddress, etc.) |
| **Functional programming patterns (Maybe monad)** | **valid8r** - Railway-oriented programming, no exceptions |
| Environment variable configuration | **valid8r** - Built-in env schema with validation |
| TypeScript-style validation | **Pydantic** - Similar ergonomics, type annotations |
| Legacy Python codebases (Flask, SQLAlchemy) | **marshmallow** - Proven track record, stable API |

## Feature Comparison Matrix

| Feature | valid8r | Pydantic | marshmallow | cerberus |
|---------|---------|----------|-------------|----------|
| **Performance** | Moderate | ⭐ Excellent (Rust core) | Moderate | Good |
| **Dependencies** | Minimal (pydantic) | pydantic-core (Rust) | None (core) | None |
| **Python Versions** | 3.11+ | 3.8+ | 3.8+ | 3.7+ |
| **Error Handling** | Maybe monad | Exceptions | Exceptions | Non-blocking |
| **Structured Network Results** | ⭐ Yes (dataclasses) | No | No | No |
| **CLI Integration** | ⭐ Built-in prompts | No | No | No |
| **FastAPI Integration** | Via Pydantic | ⭐ Native | Via plugin | No |
| **JSON Schema** | No | ⭐ Yes | Yes | No |
| **Interactive Validation** | ⭐ Yes (retry logic) | No | No | No |
| **Functional Composition** | ⭐ Yes (&, \|, ~) | Limited | No | No |
| **Type Annotations** | Full | ⭐ Full | Partial | Schema-based |
| **Learning Curve** | Moderate | Moderate | Low | Low |
| **Ecosystem Size** | Small | ⭐ Very Large | Large | Medium |

## Detailed Comparisons

### valid8r vs Pydantic

**Choose Pydantic if:**
- Building FastAPI or Django Ninja APIs
- Need automatic OpenAPI/JSON Schema generation
- Processing high-volume data (millions of records)
- Want the largest ecosystem and community
- Need seamless ORM integration (SQLModel, etc.)

**Choose valid8r if:**
- Building CLI applications with interactive prompts
- Parsing network data (URLs, emails, IPs) into structured types
- Prefer functional programming (Maybe monad, no exceptions)
- Need built-in input retry logic with validation
- Want lightweight environment variable configuration

**Example Comparison:**

**Pydantic Approach:**
```python
from pydantic import BaseModel, EmailStr, HttpUrl, field_validator

class User(BaseModel):
    email: EmailStr
    website: HttpUrl
    age: int

    @field_validator('age')
    @classmethod
    def validate_age(cls, v):
        if not 0 <= v <= 120:
            raise ValueError('Age must be between 0 and 120')
        return v

# Usage - raises exceptions on failure
try:
    user = User(email="user@example.com", website="https://example.com", age=25)
    print(user.email)  # Returns string: "user@example.com"
except ValidationError as e:
    print(e.errors())
```

**valid8r Approach:**
```python
from valid8r import parsers, validators, prompt
from valid8r.core.maybe import Success, Failure

# Interactive CLI with automatic retry
email_result = prompt.ask(
    "Email: ",
    parser=parsers.parse_email,
    retry=2
)

match email_result:
    case Success(email):
        # Returns structured EmailAddress(local='user', domain='example.com')
        print(f"{email.local}@{email.domain}")
        print(f"Domain is normalized: {email.domain}")  # Lowercase
    case Failure(error):
        print(f"Error: {error}")

# URL parsing returns structured components
url_result = parsers.parse_url("https://user:pass@example.com:8443/path?q=1#frag")
match url_result:
    case Success(url):
        # UrlParts dataclass with all components parsed
        print(url.scheme)    # 'https'
        print(url.host)      # 'example.com'
        print(url.port)      # 8443
        print(url.path)      # '/path'
        print(url.query)     # {'q': '1'}
        print(url.fragment)  # 'frag'
```

**Key Differences:**

1. **Error Handling Philosophy:**
   - Pydantic: Exceptions (try/except required)
   - valid8r: Maybe monad (pattern matching or `.is_success()`)

2. **Network Parsing:**
   - Pydantic: Returns strings (`EmailStr` is still a string)
   - valid8r: Returns structured dataclasses (EmailAddress, UrlParts, PhoneNumber)

3. **Interactive Input:**
   - Pydantic: Not designed for user prompts
   - valid8r: Built-in `prompt.ask()` with retry logic

4. **Performance:**
   - Pydantic: 5-50x faster (Rust core)
   - valid8r: Adequate for CLI/web apps, not optimized for bulk processing

**When to Use Both:**

You can use Pydantic for FastAPI models and valid8r for CLI commands:

```python
from fastapi import FastAPI
from pydantic import BaseModel
from valid8r import parsers
from valid8r.integrations import validator_from_parser

app = FastAPI()

class UserCreate(BaseModel):
    email: str

    @field_validator('email', mode='before')
    @classmethod
    def validate_email(cls, v):
        # Use valid8r's email parser in Pydantic model
        return validator_from_parser(parsers.parse_email)(v)
```

---

### valid8r vs marshmallow

**Choose marshmallow if:**
- Building Flask APIs
- Need explicit control over serialization/deserialization
- Working with SQLAlchemy models
- Want zero dependencies
- Prefer schema-based validation over type annotations

**Choose valid8r if:**
- Building CLI applications
- Need structured network parsing (URLs, emails, IPs)
- Prefer functional composition over schema definitions
- Want Maybe monad error handling
- Need interactive input prompting

**Example Comparison:**

**marshmallow Approach:**
```python
from marshmallow import Schema, fields, validate, ValidationError

class UserSchema(Schema):
    email = fields.Email(required=True)
    age = fields.Integer(required=True, validate=validate.Range(min=0, max=120))
    website = fields.URL(required=True)

schema = UserSchema()

# Explicit deserialization
try:
    result = schema.load({'email': 'user@example.com', 'age': 25, 'website': 'https://example.com'})
    print(result['email'])  # Returns dict: {'email': '...', 'age': 25, ...}
except ValidationError as e:
    print(e.messages)

# Explicit serialization
output = schema.dump(result)
```

**valid8r Approach:**
```python
from valid8r import parsers, validators
from valid8r.core.maybe import Success, Failure

# Functional composition with Maybe monad
age_parser = lambda x: parsers.parse_int(x).bind(validators.between(0, 120))

email_result = parsers.parse_email("user@example.com")
age_result = age_parser("25")
url_result = parsers.parse_url("https://example.com")

# Pattern matching for error handling
match (email_result, age_result, url_result):
    case (Success(email), Success(age), Success(url)):
        print(f"Email: {email.local}@{email.domain}")
        print(f"Age: {age}")
        print(f"URL: {url.scheme}://{url.host}")
    case _:
        # Handle any failures
        for result in [email_result, age_result, url_result]:
            if result.is_failure():
                print(result.error_or("Unknown error"))
```

**Key Differences:**

1. **API Style:**
   - marshmallow: Schema classes, explicit load/dump
   - valid8r: Functional composition, Maybe monad

2. **Serialization:**
   - marshmallow: Bidirectional (serialize/deserialize)
   - valid8r: Focused on parsing/validation (deserialization only)

3. **Type Safety:**
   - marshmallow: Runtime schema validation
   - valid8r: Type hints + runtime validation

4. **Error Handling:**
   - marshmallow: ValidationError exceptions
   - valid8r: Maybe monad (no exceptions)

**Migration Guide: marshmallow → valid8r**

```python
# Before (marshmallow)
from marshmallow import Schema, fields, validate

class ConfigSchema(Schema):
    port = fields.Integer(validate=validate.Range(min=1024, max=65535))
    debug = fields.Boolean()
    email = fields.Email(required=True)

schema = ConfigSchema()
config = schema.load(data)

# After (valid8r)
from valid8r.integrations.env import EnvSchema, EnvField
from valid8r import parsers, validators

schema = EnvSchema(fields={
    'port': EnvField(
        parser=lambda x: parsers.parse_int(x).bind(validators.between(1024, 65535)),
        default=8080
    ),
    'debug': EnvField(parser=parsers.parse_bool, default=False),
    'email': EnvField(parser=parsers.parse_email, required=True),
})

result = load_env_config(schema, prefix='APP_')
match result:
    case Success(config):
        # Typed configuration
        port = config['port']  # int, validated
```

---

### valid8r vs cerberus

**Choose cerberus if:**
- Need zero dependencies
- Validating simple dictionaries/JSON
- Want lightweight validation
- Building Eve framework applications
- Prefer non-blocking validation (collect all errors)

**Choose valid8r if:**
- Building CLI applications with user interaction
- Need structured network parsing
- Want functional composition
- Prefer type annotations over schema dicts
- Need Maybe monad error handling

**Example Comparison:**

**cerberus Approach:**
```python
from cerberus import Validator

schema = {
    'email': {'type': 'string', 'regex': r'^[^@]+@[^@]+\.[^@]+$'},
    'age': {'type': 'integer', 'min': 0, 'max': 120},
    'website': {'type': 'string', 'regex': r'^https?://'}
}

validator = Validator(schema)

data = {'email': 'user@example.com', 'age': 25, 'website': 'https://example.com'}

if validator.validate(data):
    print("Valid!")
    print(data['email'])  # Returns raw string
else:
    print(validator.errors)  # {'age': ['min value is 0']}
```

**valid8r Approach:**
```python
from valid8r import parsers, validators
from valid8r.core.maybe import Success, Failure

# Type-safe parsing with structured results
email = parsers.parse_email("user@example.com")
age = parsers.parse_int("25").bind(validators.between(0, 120))
url = parsers.parse_url("https://example.com")

match (email, age, url):
    case (Success(e), Success(a), Success(u)):
        # Structured data types
        print(f"Email domain: {e.domain}")  # EmailAddress dataclass
        print(f"Age: {a}")  # int
        print(f"URL scheme: {u.scheme}")  # UrlParts dataclass
```

**Key Differences:**

1. **Dependencies:**
   - cerberus: Zero dependencies
   - valid8r: Requires pydantic (always included)

2. **Validation Style:**
   - cerberus: Dict-based schemas, non-blocking validation
   - valid8r: Functional composition, fails fast

3. **Type Safety:**
   - cerberus: No type hints (runtime schema)
   - valid8r: Full type annotations

4. **Network Parsing:**
   - cerberus: Regex validation only
   - valid8r: Structured parsing (EmailAddress, UrlParts, etc.)

**Migration Guide: cerberus → valid8r**

```python
# Before (cerberus)
from cerberus import Validator

schema = {
    'name': {'type': 'string', 'minlength': 3, 'maxlength': 128},
    'age': {'type': 'integer', 'min': 0, 'max': 120},
    'tags': {'type': 'list', 'schema': {'type': 'string'}}
}

v = Validator(schema)
if v.validate(data):
    process(data)

# After (valid8r)
from valid8r import parsers, validators

name = parsers.parse_str(data['name']).bind(validators.length(3, 128))
age = parsers.parse_int(data['age']).bind(validators.between(0, 120))
tags = parsers.parse_list(data['tags'], element_parser=parsers.parse_str)

results = [name, age, tags]
if all(r.is_success() for r in results):
    process({
        'name': name.value_or(''),
        'age': age.value_or(0),
        'tags': tags.value_or([])
    })
```

---

## Performance Benchmarks

**Disclaimer:** Benchmarks are approximate and vary by use case. Always profile your specific workload.

### Basic Type Validation (1 million iterations)

| Library | Time (seconds) | Relative Speed |
|---------|---------------|----------------|
| Pydantic v2 | 0.5s | 1x (baseline) |
| valid8r | 2.8s | 5.6x slower |
| marshmallow | 8.5s | 17x slower |
| cerberus | 3.2s | 6.4x slower |

**Interpretation:**
- Pydantic is fastest for bulk validation due to Rust core
- valid8r is adequate for CLI/web apps (not bulk processing)
- All libraries are fast enough for typical user input validation

### When Performance Matters

**Choose Pydantic if:**
- Processing > 10,000 records per second
- Real-time data pipelines
- Latency-critical APIs

**valid8r is fine if:**
- Validating user input (< 1000 req/sec)
- CLI applications (human interaction speed)
- Background jobs with moderate throughput

---

## Migration Guides

### From Pydantic to valid8r

**When to migrate:**
- Moving from FastAPI to CLI application
- Need structured network parsing
- Prefer functional programming patterns

**Migration steps:**

```python
# Before (Pydantic)
from pydantic import BaseModel, EmailStr, field_validator

class Config(BaseModel):
    email: EmailStr
    port: int

    @field_validator('port')
    @classmethod
    def validate_port(cls, v):
        if not 1024 <= v <= 65535:
            raise ValueError('Port must be 1024-65535')
        return v

try:
    config = Config(email="admin@example.com", port=8080)
except ValidationError as e:
    print(e.errors())

# After (valid8r)
from valid8r import parsers, validators
from valid8r.integrations.env import EnvSchema, EnvField, load_env_config

schema = EnvSchema(fields={
    'email': EnvField(parser=parsers.parse_email, required=True),
    'port': EnvField(
        parser=lambda x: parsers.parse_int(x).bind(validators.between(1024, 65535)),
        required=True
    ),
})

result = load_env_config(schema, prefix='APP_')
match result:
    case Success(config):
        email = config['email']  # EmailAddress dataclass
        port = config['port']    # int
    case Failure(error):
        print(error)
```

**Key changes:**
1. Replace `BaseModel` with `EnvSchema` for config
2. Replace `@field_validator` with `lambda x: parser(x).bind(validator(...))`
3. Replace `try/except` with `match` pattern matching
4. Use `.local`/`.domain` for EmailAddress instead of string

---

### From marshmallow to valid8r

**When to migrate:**
- Moving from Flask to Click CLI
- Need structured network parsing
- Want functional composition

**Migration steps:**

```python
# Before (marshmallow)
from marshmallow import Schema, fields, validate, ValidationError

class UserSchema(Schema):
    email = fields.Email(required=True)
    age = fields.Integer(validate=validate.Range(min=0, max=120))

schema = UserSchema()
try:
    result = schema.load({'email': 'user@example.com', 'age': 25})
except ValidationError as e:
    print(e.messages)

# After (valid8r)
from valid8r import parsers, validators
from valid8r.core.maybe import Success, Failure

email = parsers.parse_email("user@example.com")
age = parsers.parse_int("25").bind(validators.between(0, 120))

match (email, age):
    case (Success(e), Success(a)):
        print(f"Email: {e.local}@{e.domain}")
        print(f"Age: {a}")
    case _:
        errors = [r.error_or("") for r in [email, age] if r.is_failure()]
        print(errors)
```

**Key changes:**
1. Replace `Schema` classes with functional composition
2. Replace `fields.X()` with `parsers.parse_X()`
3. Replace `validate=validate.Range()` with `.bind(validators.between())`
4. Replace `try/except` with `match` pattern matching
5. Use structured types (EmailAddress) instead of strings

---

### From cerberus to valid8r

**When to migrate:**
- Need type annotations
- Want structured network parsing
- Prefer functional style

**Migration steps:**

```python
# Before (cerberus)
from cerberus import Validator

schema = {
    'email': {'type': 'string', 'regex': r'^[^@]+@[^@]+\.[^@]+$'},
    'age': {'type': 'integer', 'min': 0, 'max': 120}
}

v = Validator(schema)
if v.validate(data):
    print(data['email'])
else:
    print(v.errors)

# After (valid8r)
from valid8r import parsers, validators

email = parsers.parse_email(data['email'])
age = parsers.parse_int(data['age']).bind(validators.between(0, 120))

if email.is_success() and age.is_success():
    print(f"Email: {email.value_or('')}")
    print(f"Age: {age.value_or(0)}")
else:
    print([r.error_or("") for r in [email, age] if r.is_failure()])
```

**Key changes:**
1. Replace dict schemas with function calls
2. Replace `{'type': 'integer'}` with `parsers.parse_int()`
3. Replace `{'min': X, 'max': Y}` with `.bind(validators.between(X, Y))`
4. Replace `v.validate()` with `.is_success()`
5. Use structured types instead of validated dicts

---

## Hybrid Approaches

### Using valid8r with Pydantic (Recommended)

**Use Case:** FastAPI backend + CLI management tool

```python
# api.py - FastAPI with Pydantic
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

app = FastAPI()

class User(BaseModel):
    email: EmailStr
    age: int

@app.post("/users")
def create_user(user: User):
    return {"email": user.email, "age": user.age}

# cli.py - Click CLI with valid8r
import click
from valid8r import parsers, prompt, validators
from valid8r.integrations import ParamTypeAdapter

@click.command()
def create_user_interactive():
    """Create user via interactive CLI."""
    email = prompt.ask(
        "Email: ",
        parser=parsers.parse_email,
        retry=2
    )

    age = prompt.ask(
        "Age: ",
        parser=parsers.parse_int,
        validator=validators.between(0, 120),
        retry=2
    )

    match (email, age):
        case (Success(e), Success(a)):
            # Call API with validated data
            create_user(User(email=f"{e.local}@{e.domain}", age=a))
```

**Rationale:** Pydantic excels at API validation, valid8r excels at CLI interaction. Use both where each is strongest.

---

### Using valid8r Parsers in Pydantic Models

```python
from pydantic import BaseModel, field_validator
from valid8r import parsers, validators
from valid8r.integrations import validator_from_parser

class Config(BaseModel):
    port: int
    email: str

    @field_validator('port', mode='before')
    @classmethod
    def validate_port(cls, v):
        # Use valid8r's parser + validator in Pydantic
        parser = lambda x: parsers.parse_int(x).bind(validators.between(1024, 65535))
        return validator_from_parser(parser)(v)

    @field_validator('email', mode='before')
    @classmethod
    def validate_email(cls, v):
        # Use valid8r's structured email parsing
        return validator_from_parser(parsers.parse_email)(v)
```

---

## Frequently Asked Questions

### Why another validation library?

Valid8r fills specific gaps that existing libraries don't address:

1. **Interactive CLI validation:** No other library provides built-in prompting with retry logic
2. **Structured network parsing:** Pydantic/marshmallow/cerberus return strings; valid8r returns dataclasses (EmailAddress, UrlParts, PhoneNumber)
3. **Functional composition:** Maybe monad enables railway-oriented programming without exceptions
4. **Environment variables:** Built-in schema for typed, validated env config

Valid8r is **not trying to replace** Pydantic for APIs or marshmallow for Flask. It's designed for **CLI applications** and **network data parsing**.

---

### Is valid8r faster than Pydantic?

**No.** Pydantic is 5-50x faster due to its Rust core.

**When speed matters:** Choose Pydantic for bulk processing, real-time pipelines, or high-throughput APIs.

**When valid8r is fast enough:** CLI apps, user input validation (< 1000 req/sec), background jobs.

**Example:** Parsing 1 million phone numbers:
- Pydantic: ~0.5 seconds
- valid8r: ~2.8 seconds

For CLI apps, the difference is negligible (human interaction is the bottleneck).

---

### Can I use valid8r with FastAPI?

**Yes, but Pydantic is better suited for FastAPI.**

FastAPI is designed around Pydantic:
- Automatic OpenAPI docs from Pydantic models
- Native integration with request/response validation
- JSON Schema generation

**You can use valid8r parsers in Pydantic models** via `validator_from_parser()`:

```python
from fastapi import FastAPI
from pydantic import BaseModel, field_validator
from valid8r import parsers
from valid8r.integrations import validator_from_parser

app = FastAPI()

class User(BaseModel):
    email: str

    @field_validator('email', mode='before')
    @classmethod
    def validate_email(cls, v):
        return validator_from_parser(parsers.parse_email)(v)
```

**Recommendation:** Use Pydantic for FastAPI, use valid8r for CLI tools.

---

### What makes valid8r different?

**Three unique features:**

1. **Structured Network Parsing**
   - Other libraries: `email: str = "user@example.com"`
   - valid8r: `email: EmailAddress(local='user', domain='example.com')`

2. **CLI-First Design**
   - Built-in `prompt.ask()` with retry logic
   - Rich error messages optimized for terminal output
   - Click integration via `ParamTypeAdapter`

3. **Maybe Monad Error Handling**
   - No exceptions in validation path
   - Composable via `.bind()` and `.map()`
   - Pattern matching for error handling

**Example:**
```python
from valid8r import parsers

# Returns UrlParts dataclass, not string
url = parsers.parse_url("https://user:pass@example.com:8443/path?q=1#frag")

print(url.value_or(None).scheme)    # 'https'
print(url.value_or(None).port)      # 8443
print(url.value_or(None).query)     # {'q': '1'}
```

---

### Should I migrate from Pydantic?

**Probably not, unless:**

1. You're building a CLI app (use valid8r instead)
2. You need structured network parsing (use valid8r for parsing, Pydantic for models)
3. You prefer functional programming (Maybe monad vs exceptions)

**Don't migrate if:**
- Building FastAPI/Django Ninja APIs (Pydantic is superior)
- Need JSON Schema or OpenAPI generation (Pydantic only)
- Performance is critical (Pydantic is much faster)

**Hybrid approach (recommended):**
- Use Pydantic for web APIs
- Use valid8r for CLI tools and network parsing
- Use valid8r parsers inside Pydantic validators when needed

---

### Does valid8r support async validation?

**No.** Valid8r is synchronous only.

If you need async validation, use Pydantic or write custom async wrappers around valid8r parsers.

---

### Can I create custom parsers?

**Yes.** Use `make_parser` or `create_parser`:

```python
from valid8r.core.parsers import make_parser
from valid8r.core.maybe import Maybe

@make_parser
def parse_hex_color(text: str) -> Maybe[str]:
    """Parse hex color code (e.g., #FF5733)."""
    if not text.startswith('#'):
        return Maybe.failure('Color must start with #')
    if len(text) != 7:
        return Maybe.failure('Color must be #RRGGBB format')
    try:
        int(text[1:], 16)
        return Maybe.success(text.upper())
    except ValueError:
        return Maybe.failure('Invalid hex color')

# Use like any other parser
result = parse_hex_color("#ff5733")
```

---

### Is valid8r production-ready?

**Yes, with caveats:**

- ✅ Stable API (v0.7.x)
- ✅ Comprehensive test coverage (>95%)
- ✅ Type-safe (passes strict mypy)
- ✅ Security: DoS protection, input length limits
- ⚠️ Pre-1.0 (minor API changes possible before v1.0.0)
- ⚠️ Smaller ecosystem than Pydantic/marshmallow

**Production deployments:** See [Security Guide](../security.md) for rate limiting, input size limits, and defense-in-depth strategies.

---

### What's the learning curve?

**Beginner-friendly** if you understand:
- Type hints
- Pattern matching (Python 3.10+)
- Basic functional programming (map, bind)

**Steeper** if new to:
- Maybe monad pattern
- Railway-oriented programming
- Functional composition

**Time to productivity:**
- Basic parsing: 15 minutes
- Validators and composition: 1 hour
- Advanced parsers and integrations: 2-4 hours

---

## Summary: Choosing the Right Library

| **Your Situation** | **Recommended Library** |
|-------------------|------------------------|
| Building REST API with FastAPI | **Pydantic** |
| Building Flask API with SQLAlchemy | **marshmallow** |
| Building CLI tool with user prompts | **valid8r** |
| Zero dependencies required | **cerberus** |
| Parsing URLs/emails into structured data | **valid8r** |
| Performance-critical bulk validation | **Pydantic** |
| Functional programming patterns | **valid8r** |
| Need JSON Schema / OpenAPI | **Pydantic** |
| Environment variable configuration | **valid8r** |
| Legacy Python 3.7 support | **cerberus** or **marshmallow** |

**The Bottom Line:**

- **Pydantic** is the industry standard for web APIs and data modeling
- **marshmallow** is battle-tested for Flask and SQLAlchemy
- **cerberus** is the lightweight choice for simple dict validation
- **valid8r** is purpose-built for CLI apps and network data parsing

**Valid8r's niche:** If you're building CLI applications or need structured network parsing, valid8r provides features that no other library offers. For everything else, consider the established alternatives first.

---

## Additional Resources

- [valid8r Documentation](https://valid8r.readthedocs.io/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [marshmallow Documentation](https://marshmallow.readthedocs.io/)
- [cerberus Documentation](https://docs.python-cerberus.org/)

**Community:**
- [valid8r GitHub Discussions](https://github.com/mikelane/valid8r/discussions)
- [valid8r Issue Tracker](https://github.com/mikelane/valid8r/issues)
