# Contributing to Valid8r

Thank you for considering contributing to Valid8r! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Testing](#testing)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Documentation](#documentation)
- [Community](#community)

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to mikelane@gmail.com.

## Getting Started

### Prerequisites

- Python 3.11 or higher (3.11-3.14 supported)
- [uv](https://docs.astral.sh/uv/) for dependency management (10-100x faster than Poetry)
- [pyenv](https://github.com/pyenv/pyenv) (recommended for managing Python versions)
- Git

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/valid8r.git
   cd valid8r
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/mikelane/valid8r.git
   ```

## Development Setup

### 1. Install Python Versions

If using pyenv, install the required Python versions:

```bash
pyenv install 3.14.0
pyenv install 3.13.9
pyenv install 3.12.12
pyenv install 3.11.14
pyenv local 3.14.0 3.13.9 3.12.12 3.11.14
```

### 2. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Verify installation:**
```bash
uv --version
# Should show: uv 0.9.x or later
```

### 3. Install Dependencies

```bash
uv sync
```

This installs all dependencies including dev, test, lint, and docs groups.

**Note**: If you previously used Poetry, see [docs/migration-poetry-to-uv.md](../docs/migration-poetry-to-uv.md) for migration instructions.

### 4. Set Up Pre-commit Hooks

```bash
uv run pre-commit install
```

Pre-commit hooks automatically:
- Trim trailing whitespace
- Fix end of files
- Check YAML and TOML syntax
- Run ruff (linting and formatting)
- Run mypy (type checking)

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feat/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes

Write clean, well-tested code following our style guidelines.

### 3. Run Tests Locally

```bash
# Run all tests with coverage
uv run tox

# Run only unit tests
uv run pytest tests/unit

# Run BDD tests
uv run tox -e bdd

# Run linting
uv run tox -e lint
```

### 4. Commit Your Changes

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```bash
git add .
git commit -m "feat: add new email validation parser"
```

See [Commit Messages](#commit-messages) section for details.

### 5. Push and Create Pull Request

```bash
git push origin feat/your-feature-name
```

Then create a Pull Request on GitHub.

## Code Style

### Python Style Guidelines

- **Line length**: 120 characters
- **Quotes**: Single quotes for strings, double quotes for docstrings
- **Type hints**: All functions must be fully type-annotated
- **Imports**: Sorted using isort (automatic via pre-commit)

### Formatting Tools

```bash
# Format code with ruff
uv run ruff format .

# Check and fix linting issues
uv run ruff check . --fix

# Check type hints
uv run mypy valid8r
```

### Code Patterns

- **Functional composition** over imperative validation
- **Maybe monad pattern** for error handling (Success/Failure)
- **SOLID principles** in design
- **No external dependencies** in core library (except uuid-utils)

### Architecture Principles

- Parse and validate in a single pipeline using `bind` and `map`
- Keep core logic free of I/O and side effects
- Use dependency injection for testing
- Mirror test structure to source structure

## Testing

### Test Requirements

- **Every new feature** must have tests
- **Every bug fix** must have a test that would have caught the bug
- Maintain or improve **code coverage** (currently 100%)

### Test Structure

```
tests/
├── unit/           # Unit tests mirroring source structure
├── bdd/            # BDD/Cucumber tests
│   ├── features/   # Gherkin feature files
│   └── steps/      # Step definitions
└── integration/    # Integration tests
```

### Test Naming Conventions

- Test files: `test_*.py`
- Test classes: `Describe[ClassName]` (e.g., `DescribeParseInt`)
- Test methods: `it_[describes_behavior]` (e.g., `it_parses_positive_integers`)

### Writing Tests

```python
from valid8r import parsers
from valid8r.testing import assert_maybe_success, assert_maybe_failure

class DescribeParseEmail:
    """Tests for parse_email function."""

    def it_parses_valid_email(self):
        """It parses a valid email address."""
        result = parsers.parse_email("user@example.com")
        assert assert_maybe_success(result)
        assert result.value_or(None).domain == "example.com"

    def it_rejects_invalid_email(self):
        """It rejects an invalid email address."""
        result = parsers.parse_email("not-an-email")
        assert assert_maybe_failure(result, "valid email")
```

### Google Testing Principles

- **Test behavior, not implementation**: Assert on public API only
- **Small and hermetic**: No network calls, use tmp_path, inject time
- **Deterministic**: Seed randomness, avoid sleeps
- **DAMP not DRY**: Prefer clarity over reuse in tests
- **One concept per test**: Each test fails for one clear reason

### Parametrization

Use `@pytest.mark.parametrize` with clear IDs:

```python
@pytest.mark.parametrize(
    "raw,expected",
    [
        pytest.param("42", 42, id="positive"),
        pytest.param("0", 0, id="zero"),
        pytest.param("-1", -1, id="negative"),
    ],
)
def it_parses_integers(raw, expected):
    result = parsers.parse_int(raw)
    assert result.value_or(None) == expected
```

## Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/) which enable automatic semantic versioning and changelog generation.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature (triggers MINOR version bump)
- `fix`: Bug fix (triggers PATCH version bump)
- `docs`: Documentation only changes
- `style`: Code style changes (formatting, missing semi-colons, etc)
- `refactor`: Code refactoring (no functional changes)
- `perf`: Performance improvements (triggers PATCH version bump)
- `test`: Adding or updating tests
- `build`: Build system or external dependency changes
- `ci`: CI configuration changes
- `chore`: Other changes that don't modify src or test files

### Breaking Changes

For breaking changes, add `BREAKING CHANGE:` in the footer or use `!` after the type:

```
feat!: remove deprecated parse_phone function

BREAKING CHANGE: parse_phone has been removed in favor of parse_phone_number
```

This triggers a MAJOR version bump.

### Examples

```bash
# Feature addition (minor version bump)
feat: add parse_uuid function with version validation

# Bug fix (patch version bump)
fix: correct email domain normalization case handling

# Performance improvement (patch version bump)
perf: optimize parse_int for large numbers

# Breaking change (major version bump)
feat!: change Maybe.bind signature to accept keyword arguments

BREAKING CHANGE: Maybe.bind now requires parser functions to accept
keyword arguments instead of positional arguments.

# Documentation update (no version bump)
docs: add examples for parse_url structured results

# Multiple scopes
feat(parsers,validators): add phone number validation
```

### Quick Reference

See [.github/CONVENTIONAL_COMMITS.md](.github/CONVENTIONAL_COMMITS.md) for more examples.

## Pull Request Process

### Before Submitting

1. Ensure all tests pass: `uv run tox`
2. Update documentation if needed
3. Add changelog entry if applicable
4. Verify your commits follow the conventional commit format

### PR Template

Fill out the PR template completely, including:
- Summary of changes
- Motivation and context
- Type of change
- Test coverage
- Code quality checklist
- Documentation updates

### Review Process

1. Automated checks must pass (CI, linting, tests)
2. Code review by maintainers
3. Address feedback and update as needed
4. Approval required before merge

### After Merge

- Your PR will be automatically merged to main
- Semantic release will analyze commits
- Version will be bumped automatically based on commit types
- Release notes will be auto-generated
- Package will be published to PyPI

## Issue Reporting

### Bug Reports

Use the bug report template and include:
- Python version
- Valid8r version
- Minimal reproduction example
- Expected vs actual behavior
- Stack trace if applicable

### Feature Requests

Use the feature request template and include:
- Clear description of the feature
- Use cases and motivation
- Proposed API (if applicable)
- Alternative solutions considered

### Questions

For questions:
- Check existing documentation
- Search existing issues
- Use discussions for general questions
- File an issue for documentation improvements

## Documentation

### Docstrings

Use Google or NumPy style docstrings:

```python
def parse_email(text: str) -> Maybe[EmailAddress]:
    """Parse and normalize an email address.

    Args:
        text: The email address string to parse.

    Returns:
        Success containing EmailAddress if valid, Failure with error message otherwise.

    Examples:
        >>> result = parse_email("User@Example.COM")
        >>> assert result.is_success()
        >>> email = result.value_or(None)
        >>> assert email.domain == "example.com"  # normalized to lowercase
```

### API Documentation

- All public functions must have comprehensive docstrings
- Include type hints (handled automatically)
- Provide usage examples as doctests
- Document error cases and edge cases

### Building Docs

```bash
# Build documentation
uv run docs-build

# Serve with live reload
uv run docs-serve
```

View at http://localhost:8000

## Community

### Getting Help

- **GitHub Discussions**: For questions and general discussion
- **GitHub Issues**: For bugs and feature requests
- **Documentation**: https://valid8r.readthedocs.io/

### Stay Updated

- Watch the repository for releases
- Follow the project on GitHub
- Read the CHANGELOG.md

## Development Tips

### Useful Commands

```bash
# Run smoke test
uv run python smoke_test.py

# Check coverage
uv run pytest --cov=valid8r --cov-report=html tests/unit
# View at htmlcov/index.html

# Run specific test
uv run pytest tests/unit/test_parsers.py::DescribeParseInt::it_parses_positive_integers

# Watch mode (requires pytest-watch)
uv run ptw tests/unit
```

### Debugging

- Use `breakpoint()` for debugging (built-in Python 3.7+)
- pytest --pdb to drop into debugger on failures
- Use MockInputContext for testing prompts

### Performance Testing

```python
import timeit

setup = "from valid8r import parsers"
stmt = "parsers.parse_int('12345')"
time = timeit.timeit(stmt, setup=setup, number=100000)
print(f"Average time: {time/100000*1000000:.2f} μs")
```

## License

By contributing to Valid8r, you agree that your contributions will be licensed under the MIT License.

## Questions?

Don't hesitate to ask questions! File an issue or start a discussion on GitHub.

Thank you for contributing to Valid8r! 🎉
