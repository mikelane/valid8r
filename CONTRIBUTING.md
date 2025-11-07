# Contributing to Valid8r

Thank you for considering contributing to Valid8r! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Fork-Based Contributions Required](#fork-based-contributions-required)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Security Guidelines](#security-guidelines)
- [Testing](#testing)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Documentation](#documentation)
- [Community](#community)

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to mikelane@gmail.com.

## Fork-Based Contributions Required

**Important**: This repository requires all contributions to be made via forks, not direct branches.

- **External contributors**: Must fork the repository and submit PRs from their fork
- **Collaborators with write access**: Should also use forks for contributions
- **Why**: This ensures a consistent workflow, improves security, and keeps the main repository clean

The `main` branch is protected and requires pull requests for all changes. Direct pushes to `main` are not allowed.

## Getting Started

### Prerequisites

- Python 3.11 or higher (3.11-3.14 supported)
- [uv](https://docs.astral.sh/uv/) for dependency management (10-100x faster than Poetry)
- [pyenv](https://github.com/pyenv/pyenv) (recommended for managing Python versions)
- Git

### Fork and Clone

**All contributions must come from a fork** - you cannot create branches directly in the main repository.

1. **Fork the repository** on GitHub by clicking the "Fork" button at https://github.com/mikelane/valid8r

2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/valid8r.git
   cd valid8r
   ```

3. **Add the upstream repository** to keep your fork in sync:
   ```bash
   git remote add upstream https://github.com/mikelane/valid8r.git
   ```

4. **Verify your remotes**:
   ```bash
   git remote -v
   # You should see:
   # origin    https://github.com/YOUR-USERNAME/valid8r.git (fetch)
   # origin    https://github.com/YOUR-USERNAME/valid8r.git (push)
   # upstream  https://github.com/mikelane/valid8r.git (fetch)
   # upstream  https://github.com/mikelane/valid8r.git (push)
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

### 1. Keep Your Fork Up to Date

Before creating a new feature branch, sync your fork with the upstream repository:

```bash
# Fetch upstream changes
git fetch upstream

# Update your local main branch
git checkout main
git merge upstream/main

# Push updates to your fork
git push origin main
```

### 2. Create a Feature Branch (In Your Fork)

**Important**: Create branches in your fork, not in the upstream repository.

```bash
# Ensure you're on an updated main branch
git checkout main
git pull upstream main

# Create and switch to a new feature branch
git checkout -b feat/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 3. Make Your Changes

Write clean, well-tested code following our style guidelines.

### 4. Run Tests Locally

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

### 5. Commit Your Changes

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```bash
git add .
git commit -m "feat: add new email validation parser"
```

See [Commit Messages](#commit-messages) section for details.

### 6. Push to Your Fork and Create Pull Request

**Push to your fork** (origin), not upstream:

```bash
# Push your feature branch to YOUR fork
git push origin feat/your-feature-name
```

Then create a Pull Request on GitHub:
1. Go to https://github.com/mikelane/valid8r
2. Click "Pull requests" → "New pull request"
3. Click "compare across forks"
4. Select your fork and branch as the source
5. Fill out the PR template completely

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

## Security Guidelines

### Writing Secure Parsers

When adding or modifying parsers, follow these security requirements:

#### 1. Input Length Validation FIRST

Always validate input length BEFORE expensive operations (regex, parsing, computation):

```python
def parse_foo(text: str) -> Maybe[Foo]:
    """Parse foo with DoS protection."""
    if not text or not isinstance(text, str):
        return Maybe.failure('Input required')

    s = text.strip()
    if s == '':
        return Maybe.failure('Input cannot be empty')

    # CRITICAL: Early length guard (DoS mitigation)
    if len(text) > MAX_LENGTH:
        return Maybe.failure('Input too long')

    # Now safe to perform expensive operations (regex, etc.)
    # ...
```

**Rationale**: Prevents DoS attacks where attackers send extremely large inputs to consume server resources.

**Example**: Without length guard, parsing 1MB input takes ~48ms. With length guard, rejection takes <1ms.

#### 2. Analyze Regex for ReDoS Vulnerabilities

Regular expressions can be vulnerable to catastrophic backtracking:

**❌ Avoid nested quantifiers:**
```python
# BAD: Nested quantifiers cause exponential time complexity
pattern = r'(a+)+'
pattern = r'(a*)*'
pattern = r'(a|ab)+'
```

**✅ Use atomic patterns:**
```python
# GOOD: Linear time complexity
pattern = r'a+'
pattern = r'(?:a|ab)+'  # Non-capturing group
```

**Tools to use:**
- Run `regexploit` on all regex patterns
- Test with pathological inputs (repeated characters)
- Consider using `regex` module with timeout

#### 3. Add DoS Regression Tests

Every parser must have a DoS prevention test:

```python
def it_rejects_excessively_long_input(self) -> None:
    """Reject extremely long input to prevent DoS attacks."""
    import time

    malicious_input = 'x' * 1_000_000  # 1MB input
    start = time.perf_counter()
    result = parse_foo(malicious_input)
    elapsed_ms = (time.perf_counter() - start) * 1000

    # Verify both correctness AND performance
    assert result.is_failure()
    assert 'too long' in result.error_or('').lower()
    assert elapsed_ms < 10, f'Rejection took {elapsed_ms:.2f}ms, should be < 10ms'
```

#### 4. Document Security Limits

Include security information in docstrings:

```python
def parse_foo(text: str) -> Maybe[Foo]:
    """Parse foo with security protection.

    Args:
        text: Input string to parse

    Returns:
        Success containing Foo if valid, Failure with error message otherwise

    Security:
        - Maximum input length: 100 characters
        - Time complexity: O(n)
        - ReDoS-safe regex patterns

    Examples:
        >>> result = parse_foo("valid-input")
        >>> assert result.is_success()
    """
```

### Security Testing

All parsers must pass security tests before merging:

```bash
# Run DoS prevention tests
uv run pytest tests/security/ -v

# Run security-marked tests
uv run pytest -m security
```

### Reporting Security Issues

**DO NOT** open public issues for security vulnerabilities.

See [SECURITY.md](SECURITY.md) for vulnerability reporting process.

### Security Code Review Checklist

Before submitting a PR that adds/modifies parsers:

- [ ] Input length validated BEFORE expensive operations
- [ ] All regex patterns analyzed for ReDoS vulnerabilities
- [ ] DoS regression test added with performance assertion
- [ ] Maximum input length documented in docstring
- [ ] Security tests pass locally (`uv run pytest tests/security/`)
- [ ] No sensitive data (API keys, emails, etc.) in code/tests

See [Secure Parser Development Guide](docs/security/secure-parser-development.md) for comprehensive guidelines.

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

Once your PR is merged to `main`, the automated release process begins:

1. **Semantic Analysis**: The semantic-release workflow analyzes all commits since the last release
2. **Version Calculation**: Determines version bump based on commit types:
   - `feat:` commits → MINOR version bump (0.X.0)
   - `fix:`, `perf:` commits → PATCH version bump (0.0.X)
   - `feat!:` or `BREAKING CHANGE:` → MAJOR version bump (X.0.0)
   - `docs:`, `chore:`, `ci:`, `refactor:`, `test:` → No version bump
3. **If version bump is needed**:
   - Version in `pyproject.toml` is updated
   - `CHANGELOG.md` is auto-generated from commit messages
   - Git tag is created (e.g., `v0.9.1`)
   - Package is built with `uv build`
   - Published to PyPI via trusted publishing
4. **If no version bump is needed**:
   - Workflow succeeds with no changes
   - No tag, no publish

**Monitoring Your Release**:
```bash
# Watch workflow execution
gh run list --workflow=semantic-release.yml --limit 5

# Check if version was bumped
gh release list

# Verify PyPI publication
pip index versions valid8r
```

**Typical Timeline**:
- Merge to main: Immediate
- Semantic-release workflow starts: ~10 seconds
- Build and publish: ~60-90 seconds
- Available on PyPI: ~2-3 minutes total

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
