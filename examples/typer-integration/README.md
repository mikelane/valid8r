# Cloud CLI - Typer Integration Example

A complete example demonstrating all valid8r + Typer integration patterns through a fictional cloud infrastructure management CLI.

## Installation

```bash
# Install dependencies
pip install valid8r typer

# Or with uv
uv pip install valid8r typer
```

## Usage Examples

### Pattern 1: validator_callback() - Simple Validation

The `deploy` command uses `validator_callback()` for straightforward parameter validation:

```bash
# Valid deployment
python cloud_cli.py deploy my-api --region us-east-1 --port 8080 --notify admin@example.com

# Invalid region (will fail)
python cloud_cli.py deploy my-api --region invalid-region --port 8080

# Invalid port (will fail)
python cloud_cli.py deploy my-api --region us-east-1 --port 99999

# Invalid email (will fail)
python cloud_cli.py deploy my-api --region us-east-1 --port 8080 --notify not-an-email
```

**When to use validator_callback():**
- Simple, single-use validations
- When you need clear error messages with custom prefixes
- Validating options/arguments inline

### Pattern 2: ValidatedType - Reusable Custom Types

The `grant-access` and `create-project` commands use custom types that can be reused:

```bash
# Create a project
python cloud_cli.py create-project my-webapp-api --owner alice@example.com --region us-west-2

# Invalid project ID (must be lowercase, 3-40 chars)
python cloud_cli.py create-project MyProject --owner alice@example.com

# Grant access with IAM role
python cloud_cli.py grant-access my-project-123 \
    --role arn:aws:iam::123456789012:role/MyRole \
    --user alice@example.com

# Invalid ARN format (will fail)
python cloud_cli.py grant-access my-project-123 \
    --role invalid-arn \
    --user alice@example.com
```

**When to use ValidatedType:**
- Types used across multiple commands
- Complex validation logic
- When you want a named type for documentation

### Pattern 3: validated_prompt() - Interactive Mode

The `configure` command provides an interactive wizard with validated prompts:

```bash
# Interactive configuration
python cloud_cli.py configure

# Will prompt for:
# - Project ID (with format validation)
# - Region (from allowed list)
# - Email (valid email format)
# - Port (1-65535 range)
#
# Invalid inputs are rejected with retry logic
```

**When to use validated_prompt():**
- Interactive CLIs or wizards
- When you need retry logic
- Onboarding or configuration workflows

### Pattern 4: Combining Validation with Typer Features

The `scale` command combines validation with Typer's confirmation prompts:

```bash
# Scale with confirmation
python cloud_cli.py scale my-api --instances 5 --region us-east-1

# Skip confirmation
python cloud_cli.py scale my-api --instances 5 --region us-east-1 --force

# Invalid instance count (will fail)
python cloud_cli.py scale my-api --instances 150 --region us-east-1
```

## Integration Patterns

### 1. validator_callback()

Best for simple, inline validations:

```python
from valid8r.integrations.typer import validator_callback
from valid8r.core import parsers, validators

def port_parser(text: str | None):
    return parsers.parse_int(text).bind(
        validators.minimum(1) & validators.maximum(65535)
    )

port_callback = validator_callback(port_parser, error_prefix='Port')

@app.command()
def my_command(
    port: Annotated[int, typer.Option(callback=port_callback)] = 8080
) -> None:
    # port is validated and converted to int
    pass
```

### 2. ValidatedType

Best for reusable types:

```python
from valid8r.integrations.typer import ValidatedType

ProjectId = ValidatedType(
    lambda t: parsers.parse_str(t).bind(
        validators.matches(r'^[a-z][a-z0-9-]{2,39}$')
    )
)

@app.command()
def my_command(
    project: Annotated[str, typer.Argument(click_type=ProjectId)]
) -> None:
    # project is validated and must match the pattern
    pass
```

### 3. validated_prompt()

Best for interactive workflows:

```python
from valid8r.integrations.typer import validated_prompt

@app.command()
def interactive() -> None:
    email = validated_prompt(
        'Enter email',
        parser=parsers.parse_email,
        max_retries=3
    )
    # email is validated EmailAddress object
```

## Error Handling

All patterns provide clear error messages:

```bash
$ python cloud_cli.py deploy my-api --region invalid --port 8080
Error: Invalid parameter value for '--region': Region: Invalid region. Must be one of: us-east-1, us-west-2, eu-west-1, ap-southeast-1

$ python cloud_cli.py deploy my-api --region us-east-1 --port 99999
Error: Invalid parameter value for '--port': Port: Must be at most 65535

$ python cloud_cli.py deploy my-api --region us-east-1 --port 8080 --notify bad-email
Error: Invalid parameter value for '--notify': An email address must have an @-sign.
```

## Help Text

Typer automatically generates help text with validation constraints:

```bash
$ python cloud_cli.py deploy --help
Usage: cloud_cli.py deploy [OPTIONS] SERVICE

  Deploy a service to the specified region.

Arguments:
  SERVICE  Service name to deploy  [required]

Options:
  -r, --region TEXT     AWS region (us-east-1, us-west-2, etc.)  [required]
  -p, --port INTEGER    Service port (1-65535)  [default: 8080]
  --notify TEXT         Email for deployment notifications
  --help                Show this message and exit.
```

## Benefits of valid8r + Typer Integration

1. **Type Safety**: Validated values are properly typed (EmailAddress, PhoneNumber, etc.)
2. **Clear Errors**: User-friendly error messages with helpful context
3. **Reusability**: Create custom types once, use everywhere
4. **Composability**: Chain validators using monadic operations
5. **Interactive Support**: Built-in retry logic for prompts
6. **Zero Boilerplate**: No manual try/catch blocks or validation code

## Learn More

- [Typer Integration Guide](../../docs/guides/typer-integration.md) - Comprehensive documentation
- [valid8r Documentation](https://valid8r.readthedocs.io/) - Full library reference
- [Typer Documentation](https://typer.tiangolo.com/) - Typer CLI framework

## License

This example is part of the valid8r project and is released under the MIT License.
