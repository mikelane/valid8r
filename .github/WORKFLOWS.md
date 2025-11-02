# GitHub Actions Workflows Documentation

This document describes the GitHub Actions CI/CD workflows configured for the valid8r package.

## Workflows Overview

### 1. CI Workflow (`ci.yml`)

**Triggers**:
- Pull requests to `main`
- Pushes to `main`
- Manual dispatch

**Jobs**:
- **Lint**: Runs ruff (check + format) and isort
- **Type Check**: Runs mypy type checking
- **Test**: Runs unit tests on Python 3.11, 3.12, 3.13 with coverage
- **BDD Test**: Runs behave BDD tests
- **Docs**: Builds Sphinx documentation
- **Smoke Test**: Runs smoke_test.py
- **All Checks**: Gate job that ensures all checks pass

**Purpose**: Ensures code quality on every PR and push to main.

### 2. Version and Release Workflow (`version-and-release.yml`)

**Triggers**:
- Pushes to `main` (automatic version bump based on conventional commits)
- Manual dispatch (with optional manual version bump override)

**Jobs**:
- Analyzes commit messages using conventional commits format
- Determines version bump type (major, minor, patch)
- Updates version in `pyproject.toml` using Poetry
- Creates git tag (e.g., `v0.2.0`)
- Generates categorized changelog from commits
- Creates GitHub Release with release notes

**Version Bump Rules**:
- **Major** (1.0.0 → 2.0.0):
  - Commits with `BREAKING CHANGE:` in body
  - Commits with `!` after type: `feat!:`, `fix!:`
- **Minor** (0.1.0 → 0.2.0):
  - Commits starting with `feat:`
- **Patch** (0.1.0 → 0.1.1):
  - Commits starting with `fix:`, `chore:`, `docs:`, `style:`, `refactor:`, `perf:`, `test:`
- **No bump**: Commits without conventional format

### 3. Publish to PyPI Workflow (`publish-pypi.yml`)

**Triggers**:
- GitHub Release published (automatic after version-and-release.yml)
- Manual dispatch (with option to publish to Test PyPI)

**Jobs**:
- **Check Version**: Verifies version doesn't already exist on PyPI
- **Build**: Creates wheel and source distribution using Poetry
- **Test Built Package**: Installs and smoke tests the wheel on Python 3.11, 3.12, 3.13
- **Publish to PyPI**: Publishes to PyPI (if not already published)
- **Publish to Test PyPI**: Alternative publish target (manual only)
- **Notify**: Confirmation message

**Safety Features**:
- Skips publishing if version already exists on PyPI
- Tests built package before publishing
- Uses trusted publisher (OIDC) or API token authentication
- `skip-existing` prevents duplicate uploads

## Setup Instructions

### Required GitHub Secrets

Configure these secrets in your repository settings (`Settings` → `Secrets and variables` → `Actions`):

#### For PyPI Publishing (Required)

**Option 1: API Token (Recommended for initial setup)**

1. Go to [PyPI Account Settings](https://pypi.org/manage/account/)
2. Scroll to "API tokens" and click "Add API token"
3. Name: `github-actions-valid8r`
4. Scope: "Entire account" (or specific to `valid8r` project once it exists)
5. Copy the token (starts with `pypi-`)
6. In GitHub: `Settings` → `Secrets` → `New repository secret`
   - Name: `PYPI_API_TOKEN`
   - Value: `pypi-...` (paste the token)

**Option 2: Trusted Publisher (Recommended for production)**

1. Go to [PyPI Publishing Settings](https://pypi.org/manage/account/publishing/)
2. Add a new pending publisher:
   - PyPI Project Name: `valid8r`
   - Owner: `mikelane` (your GitHub username/org)
   - Repository: `valid8r`
   - Workflow name: `publish-pypi.yml`
   - Environment name: `pypi`
3. Once configured, remove `password:` line from workflow and add `permissions: id-token: write`

#### For Test PyPI (Optional)

1. Go to [Test PyPI Account Settings](https://test.pypi.org/manage/account/)
2. Create API token same as above
3. In GitHub: Add secret `TEST_PYPI_API_TOKEN`

#### For Codecov (Optional)

1. Go to [Codecov](https://codecov.io/) and link your repository
2. Copy the upload token
3. In GitHub: Add secret `CODECOV_TOKEN`

### Repository Settings

Configure GitHub repository settings:

1. **Branch Protection for `main`**:
   - `Settings` → `Branches` → `Add rule` for `main`
   - ✅ Require pull request before merging
   - ✅ Require status checks to pass before merging
     - Select: `Lint and Format Check`, `Type Check (mypy)`, `Test (Python 3.11)`, `BDD Tests`, `All Checks Passed`
   - ✅ Require conversation resolution before merging
   - ✅ Do not allow bypassing the above settings

2. **Actions Permissions**:
   - `Settings` → `Actions` → `General`
   - Workflow permissions: "Read and write permissions"
   - ✅ Allow GitHub Actions to create and approve pull requests

3. **Environments** (for PyPI publishing):
   - `Settings` → `Environments` → `New environment`
   - Name: `pypi`
   - (Optional) Add required reviewers for production deployments
   - Add environment secret: `PYPI_API_TOKEN`

## Usage Guide for Developers

### Conventional Commits Format

All commits should follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

#### Commit Types

| Type | Version Bump | Description | Example |
|------|-------------|-------------|---------|
| `feat` | **minor** | New feature | `feat: add parse_uuid function` |
| `fix` | **patch** | Bug fix | `fix: handle empty string in parse_int` |
| `docs` | **patch** | Documentation only | `docs: update README with examples` |
| `style` | **patch** | Formatting, no code change | `style: fix indentation in parsers.py` |
| `refactor` | **patch** | Code refactoring | `refactor: simplify Maybe.bind implementation` |
| `perf` | **patch** | Performance improvement | `perf: optimize parse_list for large inputs` |
| `test` | **patch** | Add/update tests | `test: add edge cases for parse_email` |
| `chore` | **patch** | Build/tooling changes | `chore: update dependencies` |
| `ci` | **none** | CI/CD changes | `ci: add Python 3.13 to test matrix` |

#### Breaking Changes (Major Version Bump)

**Option 1: `!` after type**:
```
feat!: change parse_int to return Result instead of Maybe

This is a breaking change that affects all users of parse_int.
```

**Option 2: `BREAKING CHANGE:` in footer**:
```
feat: redesign validation API

BREAKING CHANGE: validators now return Maybe[T] instead of bool
```

### Example Commit Messages

**Feature (minor bump)**:
```bash
git commit -m "feat(parsers): add parse_phone_number with international support

- Supports E.164 format
- Returns PhoneNumber structured type
- Includes country code validation"
```

**Bug Fix (patch bump)**:
```bash
git commit -m "fix(validators): maximum validator now handles float comparison correctly

Previously, maximum(10.5) would incorrectly reject 10.5 due to
floating point comparison issue."
```

**Breaking Change (major bump)**:
```bash
git commit -m "feat!: migrate to Result monad from Maybe monad

BREAKING CHANGE: All parsers now return Result[T, Error] instead of
Maybe[T]. Success and Failure are renamed to Ok and Err.

Migration guide:
- Replace Success(val) with Ok(val)
- Replace Failure(msg) with Err(Error(msg))
- Update all .value_or() calls to handle new Error type"
```

**Documentation (patch bump)**:
```bash
git commit -m "docs: add comprehensive tutorial for custom validators"
```

**Chore (patch bump)**:
```bash
git commit -m "chore(deps): update pydantic to 2.10.0"
```

**Non-versioning commit**:
```bash
git commit -m "ci: add caching to GitHub Actions workflows"
```

### Development Workflow

#### 1. Create a Feature Branch

```bash
git checkout -b feat/phone-number-parser
```

#### 2. Make Changes and Commit

```bash
# Make your changes
vim valid8r/core/parsers.py

# Add tests
vim tests/unit/test_parsers.py

# Run tests locally
uv run pytest

# Commit with conventional format
git add .
git commit -m "feat(parsers): add parse_phone_number

- Validates phone numbers using libphonenumber
- Returns PhoneNumber structured type
- Supports international formats"
```

#### 3. Push and Create PR

```bash
git push origin feat/phone-number-parser

# Create PR using GitHub CLI
gh pr create --title "feat(parsers): add parse_phone_number" --body "Adds phone number parsing with international support"
```

#### 4. CI Checks Run Automatically

The CI workflow will:
- Run linters (ruff, isort)
- Run type checking (mypy)
- Run tests on Python 3.11, 3.12, 3.13
- Run BDD tests
- Build documentation
- Run smoke tests

All checks must pass before merging.

#### 5. Merge to Main

```bash
# Squash and merge (or merge) via GitHub UI
# Ensure the final commit message follows conventional commits format
```

#### 6. Automatic Version Bump and Release

After merge to `main`:
1. `version-and-release.yml` analyzes commits since last tag
2. Determines version bump (e.g., `feat:` → minor bump)
3. Updates `pyproject.toml` version (e.g., `0.1.0` → `0.2.0`)
4. Creates git tag `v0.2.0`
5. Generates changelog from categorized commits
6. Creates GitHub Release with notes

#### 7. Automatic PyPI Publication

After GitHub Release is created:
1. `publish-pypi.yml` checks if version exists on PyPI
2. Builds wheel and source distribution
3. Tests the built package
4. Publishes to PyPI
5. Verifies publication

### Manual Version Override

If you need to manually trigger a version bump:

```bash
# Via GitHub UI: Actions → Version and Release → Run workflow
# Select version bump type: major, minor, or patch

# Or via GitHub CLI
gh workflow run version-and-release.yml -f version_bump=minor
```

### Publishing to Test PyPI

To test the publishing process without affecting production PyPI:

```bash
# Via GitHub UI: Actions → Publish to PyPI → Run workflow
# Check "Publish to Test PyPI instead of PyPI"

# Or via GitHub CLI
gh workflow run publish-pypi.yml -f test_pypi=true
```

Then install from Test PyPI:
```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ valid8r
```

## Workflow Triggers Summary

| Workflow | Automatic Triggers | Manual Trigger | When |
|----------|-------------------|----------------|------|
| CI | PR to main, Push to main | Yes | Every code change |
| Version & Release | Push to main | Yes (with override) | After merge to main |
| Publish to PyPI | Release published | Yes (with test mode) | After GitHub Release |

## Versioning Strategy

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version (X.0.0): Incompatible API changes
- **MINOR** version (0.X.0): New functionality, backward compatible
- **PATCH** version (0.0.X): Bug fixes, backward compatible

### Pre-1.0.0 Exception

While in `0.x.x` versions (pre-stable):
- Breaking changes may be introduced in minor versions
- Use `0.x.0` for significant features
- Use `0.x.y` for patches and small features

Once the API is stable, release `1.0.0` and follow strict semver.

## Troubleshooting

### Version Not Bumping

**Problem**: Commits pushed to main but no version bump occurs.

**Cause**: Commits don't follow conventional commits format.

**Solution**: Ensure commit messages start with `feat:`, `fix:`, etc.

```bash
# Check recent commits
git log --oneline -5

# If needed, create a manual bump
gh workflow run version-and-release.yml -f version_bump=patch
```

### PyPI Upload Failed: Version Already Exists

**Problem**: Workflow fails with "File already exists" error.

**Cause**: Version already published to PyPI (duplicate).

**Solution**: This is expected behavior. The workflow skips publishing if the version exists. To publish a new version, merge more commits to trigger a version bump.

### CI Checks Failing

**Problem**: Unable to merge PR due to failing checks.

**Solution**:
1. Check workflow run logs in GitHub Actions tab
2. Run same checks locally:
   ```bash
   uv run ruff check .
   uv run ruff format --check .
   uv run mypy valid8r
   uv run pytest
   uv run behave tests/bdd/features
   ```
3. Fix issues and push again

### Permission Denied on Git Push (workflow)

**Problem**: Workflow fails to push version bump commit.

**Cause**: Insufficient permissions for GITHUB_TOKEN.

**Solution**:
1. Go to `Settings` → `Actions` → `General`
2. Set "Workflow permissions" to "Read and write permissions"
3. ✅ "Allow GitHub Actions to create and approve pull requests"

## Best Practices

### Commit Messages
- Use imperative mood: "add feature" not "added feature"
- Keep first line under 72 characters
- Reference issues: `fix(parser): handle null input (#123)`
- Group related changes in one commit

### Pull Requests
- Keep PRs focused and small
- Use conventional commits format for PR title
- PR title becomes the squash commit message
- Link related issues in PR description

### Releases
- Let the workflow handle versioning automatically
- Review generated release notes before announcing
- Update documentation for breaking changes
- Consider deprecation warnings before breaking changes

### Testing Before Release
1. Create a feature branch
2. Open PR to see CI results
3. Merge to main (triggers version bump)
4. Wait for GitHub Release
5. Verify PyPI publication
6. Test installation: `pip install valid8r`

## CI/CD Architecture Diagram

```
┌─────────────────┐
│  Pull Request   │
└────────┬────────┘
         │
         ▼
    ┌────────┐
    │   CI   │ ◄── Lint, Type Check, Test (3.11, 3.12, 3.13), BDD, Docs
    └────┬───┘
         │ (All checks pass)
         ▼
    ┌─────────┐
    │  Merge  │
    │ to main │
    └────┬────┘
         │
         ▼
┌──────────────────┐
│ Version & Release│ ◄── Analyze commits, bump version, create tag & release
└────────┬─────────┘
         │
         ▼
  ┌──────────────┐
  │GitHub Release│
  └──────┬───────┘
         │
         ▼
┌─────────────────┐
│ Publish to PyPI │ ◄── Build, test package, publish if new version
└─────────────────┘
```

## Support and Issues

If you encounter issues with the CI/CD workflows:

1. Check workflow run logs in the "Actions" tab
2. Review this documentation
3. Open an issue with:
   - Workflow name
   - Run ID or link to failed run
   - Error message
   - Expected vs actual behavior

## Additional Resources

- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Poetry Publishing](https://python-poetry.org/docs/libraries/#publishing-to-pypi)
- [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
