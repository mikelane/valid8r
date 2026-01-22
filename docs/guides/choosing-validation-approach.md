# Choosing a Validation Approach

Valid8r provides three distinct validation approaches, each optimized for different use cases. This guide helps you select the right approach for your needs.

## Decision Flowchart

```
                    What are you validating?
                            |
            +---------------+---------------+
            |               |               |
       Single value    Multiple fields   Type annotation
       from string?    in a dict/form?   driven?
            |               |               |
            v               v               v
     Parser Chaining   Schema Validation  from_type()
```

### Quick Decision Tree

1. **Single value from user input?** → Use [Parser Chaining](#parser-chaining)
2. **Multiple fields that all need validation?** → Use [Schema Validation](#schema-validation)
3. **Want type annotations to drive validation?** → Use [from_type()](#from_type-type-based-parsing)
4. **Need ALL errors across multiple fields?** → Use [Schema Validation](#schema-validation)
5. **Building a CLI with interactive prompts?** → Use [Parser Chaining](#parser-chaining) with `prompt.ask()`
6. **Validating API request body?** → Use [Schema Validation](#schema-validation)
7. **Working with dataclass-like structures?** → Use [from_type()](#from_type-type-based-parsing) with `Annotated`

---

## Parser Chaining

**Best for:** Single values, CLI input, early-exit validation pipelines

Parser chaining uses the Maybe monad's `.bind()` method to create validation pipelines that stop at the first failure.

### When to Use

- Validating individual user inputs (CLI arguments, form fields)
- Need fast-fail behavior (stop at first error)
- Building interactive prompts with retry logic
- Simple validation with 1-3 chained steps

### Example

```python
from valid8r import parsers, validators
from valid8r.core.maybe import Success, Failure

# Chain parsing and validation
result = parsers.parse_int("42").bind(
    validators.minimum(0)
).bind(
    validators.maximum(100)
)

match result:
    case Success(value):
        print(f"Valid: {value}")
    case Failure(error):
        print(f"Error: {error}")
```

### Characteristics

| Aspect | Behavior |
|--------|----------|
| Error handling | Stops at first failure (fail-fast) |
| Error count | Returns single error message |
| Input type | String → parsed type |
| Composition | Via `.bind()` and `.map()` |
| Complexity | Low |

---

## Schema Validation

**Best for:** Multi-field forms, API request bodies, configuration objects

Schema validation validates entire dict-like objects against a defined structure, collecting ALL validation errors across all fields.

### When to Use

- Validating API request/response bodies
- Form submissions with multiple fields
- Configuration file validation
- Need ALL errors at once (not just the first)
- Complex nested object structures
- Want field path tracking (e.g., `.user.address.street`)

### Example

```python
from valid8r.core import parsers, schema, validators
from valid8r.core.maybe import Success, Failure

user_schema = schema.Schema(
    fields={
        'name': schema.Field(
            parser=parsers.parse_str,
            validator=validators.non_empty_string(),
            required=True,
        ),
        'age': schema.Field(
            parser=parsers.parse_int,
            validator=validators.between(0, 120),
            required=True,
        ),
        'email': schema.Field(
            parser=parsers.parse_email,
            required=True,
        ),
    }
)

result = user_schema.validate({
    'name': '',
    'age': 'invalid',
    'email': 'bad-email',
})

match result:
    case Success(data):
        print(f"Valid: {data}")
    case Failure(errors):
        for err in errors:
            print(f"{err.path}: {err.message}")
        # Output:
        # .name: String must not be empty
        # .age: Invalid integer format
        # .email: Invalid email address
```

### Characteristics

| Aspect | Behavior |
|--------|----------|
| Error handling | Collects ALL errors across fields |
| Error count | Returns list of ValidationError objects |
| Input type | Dict → validated dict with parsed types |
| Composition | Nested schemas via `schema.validate` as parser |
| Complexity | Medium |

---

## from_type() (Type-Based Parsing)

**Best for:** Type annotation enthusiasts, Python 3.10+ projects, reducing boilerplate

The `from_type()` function automatically generates parsers from Python type annotations.

### When to Use

- Strong preference for type-driven development
- Using `typing.Annotated` for validation metadata
- Want parsers generated from existing type hints
- Building libraries that work with generic types
- Need Union types or Literal validation

### Example

```python
from typing import Annotated, Optional
from valid8r.core.type_adapters import from_type
from valid8r import validators

# Simple type
int_parser = from_type(int)
result = int_parser('42')  # Success(42)

# With validation via Annotated
Age = Annotated[int, validators.minimum(0), validators.maximum(120)]
age_parser = from_type(Age)
result = age_parser('25')  # Success(25)
result = age_parser('150')  # Failure('Value must be at most 120')

# Complex nested type
from typing import Literal

Status = Literal['active', 'inactive', 'pending']
parser = from_type(dict[str, list[Status]])
result = parser('{"users": ["active", "pending"]}')
# Success({'users': ['active', 'pending']})
```

### Characteristics

| Aspect | Behavior |
|--------|----------|
| Error handling | Stops at first failure |
| Error count | Returns single error message |
| Input type | String (often JSON) → typed value |
| Composition | Via type annotations (`Annotated`, `Union`, `Optional`) |
| Complexity | Low-Medium |

---

## Comparison Table

| Feature | Parser Chaining | Schema Validation | from_type() |
|---------|----------------|-------------------|-------------|
| **Input format** | Single string | Dict/object | String (JSON for collections) |
| **Error collection** | First error only | All errors | First error only |
| **Field paths** | N/A | Yes (`.field.nested`) | N/A |
| **Nested structures** | Manual chaining | Nested schemas | Type annotations |
| **Type inference** | Explicit parsers | Explicit parsers | From type hints |
| **Validators** | Via `.bind()` | Via `Field.validator` | Via `Annotated` |
| **Learning curve** | Low | Medium | Low-Medium |
| **Best for** | CLI, single values | APIs, forms | Type-driven code |
| **Python version** | 3.11+ | 3.11+ | 3.11+ (best with 3.12+) |

---

## When to Use Each Approach

### Use Parser Chaining When:

- Building CLI applications with `prompt.ask()`
- Validating one value at a time
- Want simple, readable validation pipelines
- Performance matters (no dict overhead)
- Need custom error handling per step

```python
# Perfect for CLI prompts
from valid8r import parsers, validators, prompt

age = prompt.ask(
    "Enter your age: ",
    parser=parsers.parse_int,
    validator=validators.between(0, 120),
    retry=True
)
```

### Use Schema Validation When:

- Validating API request bodies
- Need to show ALL validation errors to users
- Have complex nested data structures
- Want field path tracking for error reporting
- Building form validation
- Need strict mode to reject extra fields

```python
# Perfect for API validation
result = user_schema.validate(request.json)

match result:
    case Failure(errors):
        return Response({
            'errors': [
                {'field': err.path, 'message': err.message}
                for err in errors
            ]
        }, status=400)
```

### Use from_type() When:

- Already have type annotations you want to leverage
- Prefer declarative, type-driven code
- Using `Annotated` for validation metadata
- Need Union or Literal type validation
- Building generic, reusable components

```python
# Perfect for type-driven validation
from typing import Annotated, Literal

Status = Literal['draft', 'published', 'archived']
Priority = Annotated[int, validators.between(1, 5)]

Task = dict[str, Union[Status, Priority]]
parser = from_type(Task)
```

---

## Migration Guide

### From Parser Chaining to Schema

When you need error accumulation across multiple fields:

**Before (Parser Chaining):**
```python
# Validates one at a time, stops at first error
name = parsers.parse_str(data['name']).bind(validators.non_empty_string())
age = parsers.parse_int(data['age']).bind(validators.minimum(0))
email = parsers.parse_email(data['email'])

# Manual error collection
errors = []
if name.is_failure():
    errors.append(('name', name.error_or('')))
if age.is_failure():
    errors.append(('age', age.error_or('')))
# ... tedious
```

**After (Schema Validation):**
```python
# Collects all errors automatically
user_schema = schema.Schema(
    fields={
        'name': schema.Field(
            parser=parsers.parse_str,
            validator=validators.non_empty_string(),
            required=True,
        ),
        'age': schema.Field(
            parser=parsers.parse_int,
            validator=validators.minimum(0),
            required=True,
        ),
        'email': schema.Field(parser=parsers.parse_email, required=True),
    }
)

result = user_schema.validate(data)
# All errors in result.error_or([])
```

### From Schema to from_type()

When you want type annotations to drive validation:

**Before (Schema):**
```python
config_schema = schema.Schema(
    fields={
        'port': schema.Field(
            parser=parsers.parse_int,
            validator=validators.between(1024, 65535),
            required=True,
        ),
        'debug': schema.Field(parser=parsers.parse_bool, required=False),
    }
)
```

**After (from_type):**
```python
from typing import Annotated, TypedDict

Port = Annotated[int, validators.between(1024, 65535)]

# Note: TypedDict not directly supported, but you can use dict
parser = from_type(dict[str, Union[Port, bool]])
# Or define individual field parsers from types
port_parser = from_type(Port)
debug_parser = from_type(bool)
```

### From from_type() to Parser Chaining

When you need more control over the validation pipeline:

**Before (from_type):**
```python
parser = from_type(Annotated[int, validators.minimum(0)])
result = parser(user_input)
```

**After (Parser Chaining):**
```python
# More explicit, easier to debug
result = parsers.parse_int(user_input).bind(validators.minimum(0))
```

---

## Frequently Asked Questions

### Which approach is fastest?

**Parser Chaining** is fastest for single values (no dict/schema overhead). For multi-field validation, all approaches have similar performance since parsing is typically the bottleneck.

### Can I combine approaches?

**Yes!** You can use `from_type()` to create parsers and use them in Schema fields:

```python
from valid8r.core.type_adapters import from_type

Port = Annotated[int, validators.between(1024, 65535)]

config_schema = schema.Schema(
    fields={
        'port': schema.Field(
            parser=from_type(Port),
            required=True,
        ),
    }
)
```

### How do I validate nested objects?

**Schema Validation** is best for nested objects with error accumulation:

```python
address_schema = schema.Schema(
    fields={
        'street': schema.Field(parser=parsers.parse_str, required=True),
        'city': schema.Field(parser=parsers.parse_str, required=True),
    }
)

user_schema = schema.Schema(
    fields={
        'name': schema.Field(parser=parsers.parse_str, required=True),
        'address': schema.Field(
            parser=address_schema.validate,  # Nest schemas!
            required=True,
        ),
    }
)
```

### What if I need custom error messages?

All approaches support custom error messages:

**Parser Chaining:**
```python
parsers.parse_int("abc", error_message="Please enter a number")
validators.minimum(0, "Age cannot be negative")
```

**Schema:**
```python
schema.Field(
    parser=parsers.parse_int,
    validator=validators.minimum(0, "Age cannot be negative"),
    required=True,
)
```

**from_type:**
```python
# Validators in Annotated include error messages
Annotated[int, validators.minimum(0, "Age cannot be negative")]
```

### Should I use Schema or Pydantic for APIs?

- **Pydantic** is better for FastAPI integration (native support, OpenAPI generation)
- **Schema** is better when you want Maybe monad error handling and don't need Pydantic's features

See the [Library Comparison Guide](../comparison.md) for detailed comparisons.

---

## Summary

| Scenario | Recommended Approach |
|----------|---------------------|
| CLI with interactive prompts | Parser Chaining |
| Single value validation | Parser Chaining |
| API request body | Schema Validation |
| Form with multiple fields | Schema Validation |
| Need ALL errors at once | Schema Validation |
| Type-annotation driven | from_type() |
| Annotated validators | from_type() |
| Union/Literal types | from_type() |

**When in doubt:**
- Start with **Parser Chaining** for simplicity
- Move to **Schema Validation** when you need error accumulation
- Use **from_type()** when type annotations are central to your design
