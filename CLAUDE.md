# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Valid8r is a clean, flexible input validation library for Python applications that uses a Maybe monad pattern for error handling. The library provides:
- Type-safe parsing functions that return `Maybe[T]` (Success/Failure)
- Chainable validators using monadic composition
- Interactive input prompting with built-in validation
- Testing utilities for validating Maybe results

**Key Philosophy**: Prefer functional composition over imperative validation. Parse and validate in a single pipeline using `bind` and `map`.

## **MANDATORY SDLC Workflow: BDD + TDD**

**THIS PROJECT FOLLOWS STRICT BDD AND TDD PRACTICES. NO EXCEPTIONS.**

All new features MUST follow this exact workflow using the specialized agents defined in `~/.claude/agents/`:

### Phase 1: Requirements & BDD Specifications (product-technical-lead)
1. **Clarify requirements** through conversational discovery
2. **Create Gherkin .feature files** in `tests/bdd/features/`
3. **Write comprehensive scenarios** using Given-When-Then format
4. **Commit .feature files** to the repository
5. **Create GitHub issues** with proper labels and acceptance criteria
6. **Pass to QA** for Gherkin validation

### Phase 2: BDD Test Implementation (qa-security-engineer)
1. **Review Gherkin for quality** - push back on anti-patterns
2. **Ensure declarative scenarios** (WHAT not HOW)
3. **Write Cucumber/Behave tests** in `tests/bdd/steps/` (in Python, separate from production code)
4. **Verify tests FAIL** (RED) - no implementation exists yet
5. **Commit BDD tests** with label: `bdd-ready` → `ready-for-dev`
6. **Pass to Development** for TDD implementation

### Phase 3: TDD Implementation (senior-developer)
1. **Read failing BDD tests** - understand acceptance criteria
2. **Write unit test FIRST** (in `tests/unit/`) - see it FAIL (RED)
3. **Write minimal code** to make test PASS (GREEN)
4. **Refactor** while keeping tests GREEN
5. **Repeat** until all BDD tests pass
6. **NEVER modify Gherkin or Cucumber tests** during implementation
7. **Commit frequently** using conventional commits
8. **Open Pull Request** when all tests pass

### Phase 4: Code Review (code-reviewer)
- Auto-assigned via CODEOWNERS
- Review for design, maintainability, SOLID principles
- Approve or request changes

### Phase 5: QA Validation (qa-security-engineer)
- Run full test suite, security audit, performance testing
- Validate acceptance criteria from Gherkin scenarios
- Approve or request fixes

### Phase 6: Merge & Deploy
- All approvals received → merge to main
- CI/CD pipeline runs automatically

### Critical Rules

**NEVER:**
- Write production code before tests (violates TDD)
- Write tests after production code (violates TDD)
- Skip the Gherkin phase for new features
- Modify Gherkin/Cucumber tests during implementation
- Commit code with failing tests

**ALWAYS:**
- Start with product-technical-lead for new features
- Write BDD tests before unit tests
- Write unit tests before implementation
- See tests FAIL (RED) before writing code
- Make tests PASS (GREEN) with minimal code
- Refactor while keeping tests GREEN

## Common Development Commands

**Note**: This project uses `uv` for dependency management. The migration from Poetry to uv was completed in November 2025 (PR #48), bringing 60% faster CI pipelines and 300x+ faster dependency resolution.

See `docs/migration-poetry-to-uv.md` for the complete migration guide, including command comparisons and troubleshooting.

**Install uv:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Setup
```bash
# Clone and install dependencies
git clone https://github.com/mikelane/valid8r
cd valid8r
uv sync

# Install specific dependency groups
uv sync --group test      # Just test dependencies
uv sync --group dev       # Just dev dependencies
uv sync --group lint      # Just linting tools
uv sync --group docs      # Just documentation tools
```

### Testing
```bash
# Run all tests (unit + BDD) with coverage
uv run tox

# Run only unit tests
uv run pytest tests/unit

# Run a single test file
uv run pytest tests/unit/test_parsers.py

# Run a single test class
uv run pytest tests/unit/test_parsers.py::DescribeParseInt

# Run a single test method
uv run pytest tests/unit/test_parsers.py::DescribeParseInt::it_parses_positive_integers

# Run BDD tests only
uv run tox -e bdd

# Run with coverage report
uv run pytest --cov=valid8r --cov-report=term tests/unit
```

### Linting and Type Checking
```bash
# Run all linters and formatters
uv run tox -e lint

# Run ruff (linter + formatter)
uv run ruff check .
uv run ruff format .

# Run mypy type checking
uv run mypy valid8r

# Run isort (import sorting)
uv run isort valid8r tests
```

### Documentation
```bash
# Build docs
uv run tox -e docs

# Or use the project script
uv run docs-build

# Serve docs with live reload
uv run docs-serve
```

### Quick Smoke Test
```bash
# Run the smoke test
uv run python smoke_test.py
```

### Dependency Management
```bash
# Add a production dependency
uv add requests

# Add a dev dependency
uv add --group dev pytest-timeout

# Add to specific dependency groups
uv add --group test pytest-mock
uv add --group docs sphinx-theme

# Update all dependencies
uv lock --upgrade

# Update a specific package
uv lock --upgrade-package requests

# Export requirements for other tools
uv export > requirements.txt
```

## Code Architecture

### Core Module Structure

```
valid8r/
├── core/
│   ├── maybe.py           # Maybe monad: Success and Failure types
│   ├── parsers.py         # String-to-type parsers returning Maybe[T]
│   ├── validators.py      # Validation functions using Maybe
│   └── combinators.py     # Combinator functions (&, |, ~)
├── prompt/
│   ├── basic.py           # Interactive input prompting
│   └── __init__.py        # Re-exports ask()
├── testing/
│   ├── mock_input.py      # MockInputContext for testing prompts
│   ├── assertions.py      # assert_maybe_success, assert_maybe_failure
│   └── generators.py      # Test data generators
└── __init__.py            # Public API exports
```

### The Maybe Monad Pattern

Valid8r uses the Maybe monad (`Success[T]` and `Failure[T]`) for all parsing and validation:

**Success/Failure Types**:
- `Success(value)`: Contains a successfully parsed/validated value
- `Failure(error)`: Contains an error message string
- Pattern matching recommended: `match result: case Success(val): ... case Failure(err): ...`

**Monadic Operations**:
- `bind(f)`: Chain operations that return Maybe (flatMap)
- `map(f)`: Transform the contained value
- `value_or(default)`: Extract value or return default
- `error_or(default)`: Extract error or return default
- `is_success()`, `is_failure()`: Check state

**Design Decision**: All parsers in `parsers.py` return `Maybe[T]` to enable composable error handling without exceptions.

### Parser Categories

1. **Basic Type Parsers**: `parse_int`, `parse_float`, `parse_bool`, `parse_date`, `parse_complex`, `parse_decimal`
2. **Collection Parsers**: `parse_list`, `parse_dict`, `parse_set` (with element parsers)
3. **Network Parsers**: `parse_ipv4`, `parse_ipv6`, `parse_ip`, `parse_cidr`, `parse_url`, `parse_email`
4. **Advanced Parsers**: `parse_enum`, `parse_uuid` (with version validation)
5. **Validated Parsers**: `parse_int_with_validation`, `parse_list_with_validation`, `parse_dict_with_validation`
6. **Parser Factories**: `create_parser`, `make_parser`, `validated_parser`

**Structured Result Types**:
- `UrlParts`: Decomposed URL components (scheme, username, password, host, port, path, query, fragment)
- `EmailAddress`: Email components (local, domain with normalized case)

### Public API Maintenance

The public API is defined in `valid8r/__init__.py` and must maintain backward compatibility:

**Top-level exports**:
- Modules: `parsers`, `validators`, `combinators`, `prompt`
- Types: `Maybe` (from `valid8r.core.maybe`)

**Critical Rule**: When adding/removing exports, update:
1. `__all__` in `valid8r/__init__.py`
2. `__all__` in `valid8r/prompt/__init__.py`
3. Public API tests (see `tests/unit/test_public_api.py`)

Deep imports like `from valid8r.core.maybe import Success` must remain supported for backward compatibility.

## Testing Conventions

### Test Structure

Tests follow strict naming conventions defined in `pyproject.toml`:
- Test directories: `tests/unit/`, `tests/bdd/`, `tests/integration/`
- Test files: `test_*.py` or `it_*.py`
- Test classes: `Describe[ClassName]` (e.g., `DescribeParseInt`)
- Test methods: `it_[describes_behavior]` (e.g., `it_parses_positive_integers`)

**Mirror source structure**: `valid8r/core/parsers.py` → `tests/unit/test_parsers.py`

### Test Style: Google Testing Principles

- **Test behavior, not implementation**: Assert on public API only
- **Small and hermetic**: No network, use `tmp_path`, inject time
- **Deterministic**: Seed randomness, avoid sleeps
- **DAMP not DRY**: Prefer clarity over reuse in tests
- **One concept per test**: Each test fails for one clear reason
- **Clear names as specification**: `it_rejects_empty_input` not `it_should_reject`

### Parametrization

Prefer `@pytest.mark.parametrize` with excellent IDs:

```python
@pytest.mark.parametrize(
    "raw,expected",
    [
        pytest.param("42", 42, id="pos-42"),
        pytest.param("0", 0, id="zero"),
        pytest.param("-1", -1, id="neg-1"),
    ],
)
def it_parses_integers(raw, expected):
    assert parsers.parse_int(raw).value_or(None) == expected
```

Use `indirect=["fixture_name"]` for non-trivial object construction.

### Testing Maybe Results

Use testing utilities from `valid8r.testing`:

```python
from valid8r.testing import assert_maybe_success, assert_maybe_failure, MockInputContext

# Assert success with expected value
result = parsers.parse_int("42")
assert assert_maybe_success(result, 42)

# Assert failure with error substring
result = parsers.parse_int("not a number")
assert assert_maybe_failure(result, "valid integer")

# Mock user input for prompts
with MockInputContext(["yes", "42"]):
    answer = prompt.ask("Continue?", parser=parsers.parse_bool)
    age = prompt.ask("Age?", parser=parsers.parse_int)
```

## Code Style

### Type Annotations
- All functions must be fully type-annotated
- Code must pass `mypy` with strict settings
- Use `from __future__ import annotations` in all files (ruff enforces this)

### Formatting
- Line length: 120 characters
- Quotes: single quotes for strings, double quotes for docstrings
- Use ruff for formatting (black-compatible with modifications)
- Import sorting via isort (integrated with ruff)

### Comments
- Keep comments minimal; explain WHY, not WHAT
- Public API gets comprehensive docstrings with doctests
- Private functions use minimal docstrings

### Error Messages
- Parser failures return deterministic, user-friendly messages
- Test error messages by matching substrings, not exact text
- Avoid technical jargon in user-facing error messages

## Architecture Patterns

### Dependency Injection for Testing
Use dependency injection to make code testable without mocks:
- Inject parsers into validation functions
- Inject validators into prompt functions
- Use fixtures to create test doubles

### Parser Composition
Combine parsers using monadic operations:

```python
# Chain parsing and validation
result = parse_int(text).bind(lambda x: validators.minimum(0)(x))

# Transform parsed values
result = parse_int(text).map(lambda x: x * 2)

# Combine validators using operators
validator = validators.minimum(0) & validators.maximum(100)
```

### Strangler Pattern for Refactoring
When refactoring legacy code:
- Add new implementation alongside old
- Use feature flags/adapters to toggle
- Migrate gradually with tests ensuring equivalence
- Delete old implementation when migration complete

## Special Considerations

### No External Dependencies (Core)
The core library has minimal external dependencies:
- `uuid-utils` (optional, falls back to stdlib)
- Standard library only for everything else

When adding functionality, prefer stdlib solutions unless there's a compelling reason for a dependency.

### Sphinx Documentation
API documentation is auto-generated using sphinx-autoapi. Docstrings must be comprehensive:
- Include type information (handled by type hints)
- Provide usage examples as doctests
- Document error cases and edge cases
- Use Google-style or NumPy-style docstring format

### BDD Tests
Gherkin feature files live in `tests/bdd/features/` with step definitions in `tests/bdd/steps/`. BDD tests complement unit tests by describing user-facing behavior.

## Performance Considerations

- Parsers should be fast (avoid regex when simple string operations suffice)
- Validate at boundaries; keep core logic working on trusted data
- Mark slow tests with `@pytest.mark.slow`
- Use `@pytest.mark.integration` for external integrations
