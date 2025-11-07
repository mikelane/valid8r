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
- Make ANY code changes without an associated GitHub issue/ticket

**ALWAYS:**
- Start with product-technical-lead for new features
- Write BDD tests before unit tests
- Write unit tests before implementation
- See tests FAIL (RED) before writing code
- Make tests PASS (GREEN) with minimal code
- Refactor while keeping tests GREEN
- Work against a GitHub issue/ticket (existing or newly created)
- Keep the issue/ticket updated with progress throughout development

## **MANDATORY: GitHub Issue/Ticket Requirement**

**ALL work must be tracked in a GitHub issue. NO EXCEPTIONS.**

### Rules for All Agents

1. **Before making ANY changes** (code, docs, config, tests):
   - Verify an open GitHub issue exists for the work
   - If no issue exists, ask the user if you should create one
   - Link all commits and PRs to the issue number (e.g., `feat: add parser (#123)`)

2. **Throughout development**:
   - Update the issue with progress comments at key milestones:
     - When starting work: "Starting implementation"
     - After major steps: "BDD tests complete (RED)", "TDD cycle complete (GREEN)"
     - When blocked: "Blocked by X, investigating Y"
     - When complete: "Implementation complete, PR #XXX ready for review"
   - Reference the issue in ALL commit messages using `#issue-number`
   - Keep the issue status current (labels, assignees, milestones)

3. **When completing work**:
   - Reference the issue in the PR description (e.g., "Closes #123")
   - Add a final comment summarizing what was delivered
   - Do NOT close issues manually - let PRs close them automatically

### Creating Issues

When creating a new issue, include:
- **Title**: Clear, concise description of the work
- **Body**:
  - Summary of what needs to be done
  - Acceptance criteria (Gherkin scenarios if applicable)
  - Technical considerations
  - Related issues (blocks/blocked by)
- **Labels**: Appropriate labels (enhancement, bug, integration, etc.)
- **Milestone**: If part of a larger initiative

### Examples

**Good commit message:**
```
feat: add environment variable integration (#147)
```

**Good PR description:**
```
Closes #147

Implements environment variable integration with schema validation.
All BDD scenarios passing, comprehensive tests included.
```

**Good issue update:**
```
Starting BDD test implementation. Created feature file with 7 scenarios
covering all acceptance criteria from the issue description.
```

**Bad commit message:**
```
add env vars  # Missing issue reference
```

**Bad workflow:**
Making changes without creating/referencing any issue

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
4. **Communication Parsers**: `parse_phone` (North American Number Plan - NANP)
5. **Advanced Parsers**: `parse_enum`, `parse_uuid` (with version validation)
6. **Validated Parsers**: `parse_int_with_validation`, `parse_list_with_validation`, `parse_dict_with_validation`
7. **Parser Factories**: `create_parser`, `make_parser`, `validated_parser`

**Structured Result Types**:
- `UrlParts`: Decomposed URL components (scheme, username, password, host, port, path, query, fragment)
- `EmailAddress`: Email components (local, domain with normalized case)
- `PhoneNumber`: Phone components (country_code, area_code, exchange, subscriber, extension, region)

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

## Security Considerations

### DoS Protection Through Input Length Validation

**Critical Pattern**: Always validate input length BEFORE expensive operations (regex, parsing, computation).

**Example - Phone Parser DoS Protection (v0.9.1)**:
```python
def parse_phone(text: str | None, *, region: str = 'US', strict: bool = False) -> Maybe[PhoneNumber]:
    # Handle None or empty input
    if text is None or not isinstance(text, str):
        return Maybe.failure('Phone number cannot be empty')

    s = text.strip()
    if s == '':
        return Maybe.failure('Phone number cannot be empty')

    # CRITICAL: Early length guard (DoS mitigation)
    # Reject oversized inputs BEFORE regex operations
    if len(text) > 100:
        return Maybe.failure('Invalid format: phone number is too long')

    # Now safe to perform expensive regex operations
    # ...
```

**Performance Impact**:
- Without guard: 1MB input takes ~48ms to reject (after regex operations)
- With guard: 1MB input takes <1ms to reject (immediate rejection)

**Testing DoS Protection**:
```python
def it_rejects_excessively_long_input(self) -> None:
    """Reject extremely long input to prevent DoS attacks."""
    import time
    malicious_input = '4' * 1000

    start = time.perf_counter()
    result = parse_phone(malicious_input)
    elapsed_ms = (time.perf_counter() - start) * 1000

    # Verify both correctness AND performance
    assert result.is_failure()
    assert 'too long' in result.error_or('').lower()
    assert elapsed_ms < 10, f'Rejection took {elapsed_ms:.2f}ms, should be < 10ms'
```

**General Guidelines**:
1. Add length checks immediately after null/empty validation
2. Test both correctness (error message) AND performance (< 10ms)
3. Use reasonable limits (e.g., 100 chars for phone, 1000 for URLs)
4. Document the limit and rationale in code comments

### OWASP Top 10 Awareness

When implementing parsers, consider:
- **Injection**: Sanitize inputs that will be used in SQL, OS commands, etc.
- **Broken Access Control**: Validate authorization before parsing sensitive data
- **Cryptographic Failures**: Use secure defaults (e.g., case-insensitive email domains)
- **Security Misconfiguration**: Fail securely (return Failure, never raise exceptions to users)

See `SECURITY.md` for reporting vulnerabilities and security best practices.

## Performance Considerations

- Parsers should be fast (avoid regex when simple string operations suffice)
- **Always validate input length BEFORE expensive operations** (see Security Considerations)
- Validate at boundaries; keep core logic working on trusted data
- Mark slow tests with `@pytest.mark.slow`
- Use `@pytest.mark.integration` for external integrations

## Release Process

### Fully Automated Releases

Valid8r uses [python-semantic-release v10](https://python-semantic-release.readthedocs.io/)
for fully automated versioning and releases. The workflow is:

1. **Commit to main** using [Conventional Commits](https://www.conventionalcommits.org/)
2. **Semantic-release analyzes** commits and determines version bump
3. **Version bumped** based on commit types:
   - `feat:` → MINOR (0.X.0)
   - `fix:`, `perf:` → PATCH (0.0.X)
   - `feat!:` or `BREAKING CHANGE:` → MAJOR (X.0.0)
4. **Changelog auto-generated** from commit history
5. **Git tag created** (e.g., `v0.10.0`)
6. **Built and tested** (wheel + sdist smoke tests)
7. **Published to PyPI** via Trusted Publishing (no API tokens)
8. **GitHub release created** with changelog

**Workflow**: `.github/workflows/release.yml`

### Conventional Commit Format

```bash
<type>(<scope>): <subject>

<body>

<footer>
```

**Common Types**:
- `feat`: New feature (MINOR bump)
- `fix`: Bug fix (PATCH bump)
- `perf`: Performance improvement (PATCH bump)
- `docs`: Documentation only (no bump)
- `refactor`: Code refactoring (no bump)
- `test`: Test changes (no bump)
- `ci`: CI/CD changes (no bump)
- `chore`: Maintenance tasks (no bump)

**Examples**:
```bash
# Feature (0.8.0 → 0.9.0)
feat: add parse_uuid function with version validation

# Bug fix (0.8.0 → 0.8.1)
fix: correct email domain normalization case handling

# Performance (0.8.0 → 0.8.1)
perf: add input length guard to phone parser for DoS protection

# Breaking change (0.8.0 → 1.0.0)
feat!: change Maybe.bind signature to accept keyword arguments

BREAKING CHANGE: Maybe.bind now requires parser functions to accept
keyword arguments instead of positional arguments.

# No version bump
docs: update README with phone parser examples
```

### Security Features

- **PyPI Trusted Publishing**: No API tokens, OIDC authentication
- **SHA-pinned Actions**: All GitHub Actions pinned to commit SHAs
- **Isolated Testing**: Built packages tested in isolation before publish
- **Automated Validation**: Multi-version testing, type checking, linting

### Manual Override (Emergency Only)

```bash
# Trigger release workflow manually
gh workflow run release.yml
```

### Release Checklist

Before merging to `main`:
- [ ] All tests pass (`uv run tox`)
- [ ] Commits follow Conventional Commits format
- [ ] PR description includes summary of changes
- [ ] Breaking changes are clearly documented
- [ ] CHANGELOG.md will be auto-updated (no manual edits needed)

### Monitoring Releases

```bash
# Check latest release
gh release list

# View workflow runs
gh run list --workflow=release.yml

# Check PyPI versions
pip index versions valid8r
```

### Branch Protection and PAT Configuration

The `main` branch is protected by repository rulesets. The semantic-release workflow uses a Personal Access Token (PAT) stored in `SEMANTIC_RELEASE_TOKEN` secret to bypass branch protection when creating version bump commits and tags.

**Configuration**:
- Repository ruleset: Requires review for all PRs
- Bypass actor: Repository administrators (using Classic PAT with `repo` scope)
- Secret: `SEMANTIC_RELEASE_TOKEN` (Classic PAT, not fine-grained)
- do not push to github without running the full pre-commit suite of linting and tests.

### GitHub Auto-Close Issues Workflow

**Problem**: GitHub's native auto-close feature doesn't work with squash merges when the closing keyword ("Closes #XXX", "Fixes #XXX", "Resolves #XXX") is only in the PR description body, not the PR title.

**Solution**: Custom GitHub Action (`.github/workflows/auto-close-issues.yml`) that:
1. Triggers when a PR is merged to `main`
2. Parses the PR description for closing keywords
3. Automatically closes referenced issues via GitHub API
4. Adds a comment linking the PR that closed the issue

**Supported Keywords** (case-insensitive):
- `Closes #123`, `Close #123`, `Closed #123`
- `Fixes #123`, `Fix #123`, `Fixed #123`
- `Resolves #123`, `Resolve #123`, `Resolved #123`

**PR Best Practices**:
```markdown
## Summary
Brief description of changes

## Implementation
Technical details

## Related Issues
Closes #142
Fixes #145
```

**Benefits**:
- Eliminates manual issue closing after PR merge
- Prevents PM agents from suggesting already-completed work
- Provides traceability with automatic comments
- Works seamlessly with existing squash merge workflow

**Workflow Run**: Adds ~5-10 seconds to PR merge process (negligible cost)
