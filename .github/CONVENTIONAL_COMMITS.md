# Conventional Commits Quick Reference

This is a quick reference guide for writing conventional commits for the valid8r project.

## Basic Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Commit Types and Version Bumps

| Type | Bump | Use When | Example |
|------|------|----------|---------|
| `feat` | 🔼 **minor** | Adding new feature | `feat: add UUID v7 parsing support` |
| `fix` | 🔼 **patch** | Fixing a bug | `fix: handle empty strings in parse_int` |
| `docs` | 🔼 **patch** | Documentation changes | `docs: add examples to README` |
| `style` | 🔼 **patch** | Code formatting (no logic change) | `style: format with ruff` |
| `refactor` | 🔼 **patch** | Code refactoring | `refactor: simplify Maybe monad` |
| `perf` | 🔼 **patch** | Performance improvements | `perf: optimize list parsing` |
| `test` | 🔼 **patch** | Adding or updating tests | `test: add edge cases for validators` |
| `chore` | 🔼 **patch** | Maintenance tasks | `chore: update dependencies` |
| `ci` | ⚪ **none** | CI/CD changes | `ci: add Python 3.13 to matrix` |
| `build` | ⚪ **none** | Build system changes | `build: update uv config` |

## Breaking Changes (Major Bump)

### Method 1: Add `!` after type

```bash
feat!: redesign validation API

Changed validators to return Result instead of Maybe.
```

### Method 2: Add `BREAKING CHANGE:` footer

```bash
feat: redesign validation API

BREAKING CHANGE: Validators now return Result[T, E] instead of Maybe[T].
Update all validator calls to handle the new return type.
```

## Scopes (Optional)

Scopes indicate which part of the codebase changed:

```
feat(parsers): add parse_phone_number
fix(validators): correct float comparison in maximum
docs(readme): add installation instructions
test(integration): add API integration tests
chore(deps): bump pydantic to 2.10
```

Common scopes for valid8r:
- `parsers` - Changes to parsing functions
- `validators` - Changes to validation functions
- `prompt` - Changes to interactive prompting
- `core` - Changes to core Maybe monad
- `testing` - Changes to testing utilities
- `docs` - Documentation changes
- `deps` - Dependency updates
- `ci` - CI/CD workflow changes

## Real Examples

### Feature Addition (Minor Bump)

```bash
git commit -m "feat(parsers): add parse_ipv6 function

- Validates IPv6 addresses using ipaddress module
- Returns Success(IPv6Address) or Failure with error
- Handles compressed and expanded notation"
```

### Bug Fix (Patch Bump)

```bash
git commit -m "fix(validators): minimum validator now accepts equal values

Previously minimum(5) would reject the value 5, which was incorrect.
Now minimum(5) accepts 5 as expected."
```

### Documentation Update (Patch Bump)

```bash
git commit -m "docs: add comprehensive guide for custom parsers

Includes:
- Step-by-step tutorial
- Best practices
- Common pitfalls
- Example implementations"
```

### Refactoring (Patch Bump)

```bash
git commit -m "refactor(core): extract error handling into helper functions

No behavior change, improved code organization and testability."
```

### Performance Improvement (Patch Bump)

```bash
git commit -m "perf(parsers): use lazy evaluation in parse_list

Reduces memory usage for large lists by 40% and improves
parsing speed by 25%."
```

### Test Addition (Patch Bump)

```bash
git commit -m "test(parsers): add property-based tests for parse_int

Uses hypothesis to test parse_int with randomly generated
integers and invalid inputs."
```

### Breaking Change (Major Bump)

```bash
git commit -m "feat!: replace Maybe with Result monad

BREAKING CHANGE: All parsers now return Result[T, Error] instead
of Maybe[T].

Migration guide:
- Replace 'from valid8r.core.maybe import Success, Failure'
  with 'from valid8r.core.result import Ok, Err'
- Replace Success(value) with Ok(value)
- Replace Failure(msg) with Err(Error(msg))
- Update pattern matching to use Ok/Err

This change provides better error context and aligns with
Rust-style error handling."
```

### Dependency Update (Patch Bump)

```bash
git commit -m "chore(deps): update pydantic from 2.9.0 to 2.10.0

- Fixes security vulnerability CVE-2024-XXXX
- Improves validation performance
- No breaking changes"
```

### CI/CD Update (No Bump)

```bash
git commit -m "ci: add automatic PyPI publishing workflow

Sets up automatic versioning and publishing to PyPI when
releases are created."
```

## Multi-line Commits with Body and Footer

```bash
git commit -m "feat(parsers): add parse_email with validation options

Added comprehensive email parsing with configurable validation:
- Domain validation (DNS lookup optional)
- Length limits (RFC 5321 compliance)
- Special character handling
- Unicode support

The parser returns EmailAddress structured type with
local and domain parts separated.

Closes #123
Refs #124"
```

## Tips for Good Commit Messages

1. **Use imperative mood**: "add feature" not "added feature" or "adds feature"
2. **First line under 72 chars**: Keep subject line concise
3. **Separate subject from body**: Use blank line between subject and body
4. **Explain why, not what**: Code shows what changed, commit explains why
5. **Reference issues**: Use "Closes #123" or "Fixes #456"
6. **One logical change per commit**: Split unrelated changes into separate commits

## Common Patterns

### Multiple Related Changes

```bash
feat(parsers): add comprehensive URL parsing

- Add parse_url returning UrlParts struct
- Add parse_url_simple for basic validation
- Add support for custom schemes
- Include query parameter parsing
```

### Bug Fix with Test

```bash
fix(validators): handle None values in range validator

Added None check before comparison. Previously would raise
TypeError when validating None values.

Added regression test to prevent future issues.

Fixes #234
```

### Documentation with Examples

```bash
docs(examples): add real-world validation examples

Created examples/ directory with:
- Form validation example
- API request validation
- Configuration file parsing
- Custom validator creation
```

## Anti-Patterns (Avoid These)

❌ **Vague messages**:
```bash
git commit -m "fix stuff"
git commit -m "update code"
git commit -m "changes"
```

❌ **Missing type**:
```bash
git commit -m "add phone parser"  # Should be: feat(parsers): add phone parser
```

❌ **Wrong type**:
```bash
git commit -m "feat: fix bug in validator"  # Should be: fix(validators): ...
```

❌ **Multiple unrelated changes**:
```bash
git commit -m "feat: add parser, fix validator, update docs"
# Should be 3 separate commits
```

## Verification Before Commit

Before committing, check:

1. ✅ Type is correct (feat, fix, docs, etc.)
2. ✅ Scope is appropriate (if used)
3. ✅ Description is clear and concise
4. ✅ Breaking changes marked with `!` or `BREAKING CHANGE:`
5. ✅ Tests pass locally
6. ✅ Linters pass

```bash
# Run checks before committing
uv run ruff check .
uv run mypy valid8r
uv run pytest

# Then commit
git commit -m "feat(parsers): add parse_phone_number"
```

## GitHub PR Titles

PR titles should also follow conventional commits format, as they become the commit message when squashing:

**Good PR Titles**:
- `feat(parsers): add UUID validation with version support`
- `fix(validators): handle edge case in email validation`
- `docs: improve README with getting started guide`

**Bad PR Titles**:
- `Add feature` ❌
- `Bug fix` ❌
- `Update` ❌

## Automation Details

The `version-and-release.yml` workflow analyzes commits using these rules:

1. **Major bump**: Any commit with `!` or `BREAKING CHANGE:`
2. **Minor bump**: Any `feat:` commit (if no major bump)
3. **Patch bump**: Any `fix:`, `docs:`, `style:`, `refactor:`, `perf:`, `test:`, `chore:` commit
4. **No bump**: Only `ci:` or `build:` commits

The **first matching rule wins**:
- If any commit is breaking → major bump
- Else if any commit is feat → minor bump
- Else if any commit is fix/docs/etc → patch bump
- Else → no bump

## Questions?

If unsure about commit format:

1. Check this guide
2. Look at recent commits: `git log --oneline -10`
3. Review [conventionalcommits.org](https://www.conventionalcommits.org/)
4. Ask in PR comments or issues

## Quick Decision Tree

```
Does this change the public API?
├─ Yes, breaks backward compatibility
│  └─ Use feat! or fix! with BREAKING CHANGE → Major bump
└─ No, backward compatible
   ├─ Adds new feature?
   │  └─ Use feat: → Minor bump
   ├─ Fixes bug?
   │  └─ Use fix: → Patch bump
   ├─ Updates docs?
   │  └─ Use docs: → Patch bump
   ├─ Refactors code?
   │  └─ Use refactor: → Patch bump
   ├─ Updates tests?
   │  └─ Use test: → Patch bump
   ├─ Maintenance/deps?
   │  └─ Use chore: → Patch bump
   └─ Updates CI/CD?
      └─ Use ci: → No bump
```
