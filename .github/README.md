# GitHub Configuration for valid8r

This directory contains all GitHub-specific configuration for the valid8r project, including CI/CD workflows, issue templates, and documentation.

## Quick Links

- **[Workflows Documentation](WORKFLOWS.md)** - Complete guide to CI/CD workflows
- **[Setup Checklist](SETUP_CHECKLIST.md)** - Step-by-step repository setup guide
- **[Conventional Commits Guide](CONVENTIONAL_COMMITS.md)** - Quick reference for commit messages

## Directory Structure

```
.github/
├── workflows/
│   ├── ci.yml                      # Continuous Integration (tests, linting, type checking)
│   ├── version-and-release.yml     # Automatic versioning and GitHub releases
│   └── publish-pypi.yml            # PyPI package publishing
├── ISSUE_TEMPLATE/
│   └── ... (issue templates)
├── CODEOWNERS                       # Code ownership and review assignments
├── dependabot.yml                   # Dependency update automation
├── pull_request_template.md         # PR template for contributors
├── WORKFLOWS.md                     # Complete workflows documentation
├── CONVENTIONAL_COMMITS.md          # Commit message format guide
├── SETUP_CHECKLIST.md              # Initial repository setup steps
└── README.md                        # This file
```

## Workflows Overview

### 1. CI Workflow (`workflows/ci.yml`)

**Runs on**: Every pull request and push to main

**Purpose**: Ensure code quality and prevent bugs from reaching production

**Checks**:
- Linting with ruff (code quality and formatting)
- Type checking with mypy
- Unit tests on Python 3.11, 3.12, 3.13
- BDD tests with behave
- Documentation build
- Smoke tests
- Coverage reporting

**Status**: ✅ All checks must pass before merging

### 2. Version and Release Workflow (`workflows/version-and-release.yml`)

**Runs on**: Pushes to main branch

**Purpose**: Automate semantic versioning based on conventional commits

**Process**:
1. Analyzes commit messages since last release
2. Determines version bump (major, minor, or patch)
3. Updates `pyproject.toml` version
4. Creates git tag (e.g., `v0.2.0`)
5. Generates changelog from commits
6. Creates GitHub Release with notes

**Versioning Rules**:
- `feat:` commits → Minor version bump (0.1.0 → 0.2.0)
- `fix:`, `docs:`, etc. → Patch version bump (0.1.0 → 0.1.1)
- `BREAKING CHANGE:` or `feat!:` → Major version bump (0.1.0 → 1.0.0)

### 3. Publish to PyPI Workflow (`workflows/publish-pypi.yml`)

**Runs on**: GitHub release published (triggered by version-and-release workflow)

**Purpose**: Automatically publish package to PyPI

**Process**:
1. Checks if version already exists on PyPI (prevents duplicates)
2. Builds wheel and source distribution
3. Tests built package on all Python versions
4. Publishes to PyPI using API token
5. Verifies publication

**Safety**: Skips publishing if version already exists

## For Contributors

### Writing Commit Messages

All commits must follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>[optional scope]: <description>

[optional body]
```

**Common types**:
- `feat:` - New feature (minor version bump)
- `fix:` - Bug fix (patch version bump)
- `docs:` - Documentation changes (patch version bump)
- `refactor:` - Code refactoring (patch version bump)
- `test:` - Test updates (patch version bump)
- `chore:` - Maintenance tasks (patch version bump)

**Examples**:
```bash
git commit -m "feat(parsers): add UUID parsing support"
git commit -m "fix(validators): handle None in minimum validator"
git commit -m "docs: add examples to README"
```

See [CONVENTIONAL_COMMITS.md](CONVENTIONAL_COMMITS.md) for detailed guide.

### Creating Pull Requests

1. Create feature branch: `git checkout -b feat/my-feature`
2. Make changes and commit with conventional format
3. Push and create PR
4. Ensure all CI checks pass
5. Wait for review and approval
6. Squash and merge (PR title becomes commit message)

PR title should also follow conventional commits format:
```
feat(parsers): add phone number validation
fix(validators): correct email regex pattern
docs: improve getting started guide
```

### Development Workflow

```bash
# 1. Create feature branch
git checkout -b feat/add-parser

# 2. Make changes
# ... edit code ...

# 3. Run tests locally
poetry run pytest
poetry run mypy valid8r
poetry run ruff check .

# 4. Commit with conventional format
git commit -m "feat(parsers): add phone number parser"

# 5. Push and create PR
git push origin feat/add-parser
gh pr create --fill

# 6. Wait for CI checks to pass
# 7. Get review approval
# 8. Merge to main

# 9. Automatic version bump happens on main
# 10. Automatic PyPI publish happens after release
```

## For Repository Administrators

### Initial Setup

Follow the [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md) for complete setup instructions.

**Key steps**:
1. Create PyPI account and generate API token
2. Add `PYPI_API_TOKEN` to GitHub secrets
3. Configure branch protection rules
4. Enable GitHub Actions with write permissions
5. Test workflows with a test release

### Secrets Required

**Required**:
- `PYPI_API_TOKEN` - PyPI API token for publishing

**Optional**:
- `TEST_PYPI_API_TOKEN` - Test PyPI token for testing
- `CODECOV_TOKEN` - Codecov token for coverage reporting

### Branch Protection

The `main` branch should be protected with these rules:
- Require pull request reviews (1+ approvals)
- Require status checks to pass:
  - Lint and Format Check
  - Type Check (mypy)
  - Test (Python 3.11, 3.12, 3.13)
  - BDD Tests
  - All Checks Passed
- Require conversation resolution
- Require linear history
- Prevent force pushes
- Prevent deletions

### Manual Triggers

All workflows can be manually triggered:

```bash
# Manual version bump (override automatic detection)
gh workflow run version-and-release.yml -f version_bump=minor

# Manual PyPI publish
gh workflow run publish-pypi.yml

# Publish to Test PyPI
gh workflow run publish-pypi.yml -f test_pypi=true
```

## Troubleshooting

### Workflows Not Running

**Check**:
1. GitHub Actions enabled: `Settings` → `Actions` → `General`
2. Workflow files in correct location: `.github/workflows/`
3. Valid YAML syntax: Use `yamllint` or GitHub's editor

### Version Not Bumping

**Check**:
1. Commits follow conventional format
2. Commits since last tag use proper types (`feat:`, `fix:`, etc.)
3. Not only `ci:` or `build:` commits (these don't trigger bumps)

### PyPI Publishing Failed

**Check**:
1. `PYPI_API_TOKEN` secret is set correctly
2. PyPI account has 2FA enabled
3. Package name not already taken
4. Version not already published
5. Token has correct scope (account or project)

### CI Checks Failing

**Run locally**:
```bash
poetry run ruff check .
poetry run ruff format --check .
poetry run mypy valid8r
poetry run pytest
poetry run behave tests/bdd/features
```

Fix issues and push again.

## Documentation

### Complete Documentation

- **[WORKFLOWS.md](WORKFLOWS.md)**: Comprehensive guide to all workflows, including:
  - Detailed workflow descriptions
  - Trigger conditions
  - Job breakdowns
  - Conventional commits specification
  - Developer workflow guide
  - Troubleshooting guide

- **[CONVENTIONAL_COMMITS.md](CONVENTIONAL_COMMITS.md)**: Quick reference for commit message format:
  - Commit types and version bumps
  - Examples for every scenario
  - Breaking change formats
  - Anti-patterns to avoid
  - Decision tree for choosing commit type

- **[SETUP_CHECKLIST.md](SETUP_CHECKLIST.md)**: Step-by-step setup guide:
  - PyPI account creation
  - API token generation
  - GitHub secrets configuration
  - Branch protection setup
  - Initial testing procedures
  - Troubleshooting common issues

### Additional Resources

- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Poetry Publishing Guide](https://python-poetry.org/docs/libraries/#publishing-to-pypi)

## Workflow Automation Summary

```
Developer Workflow:
┌─────────────────┐
│ Create PR       │
│ (feat: ...)     │
└────────┬────────┘
         │
         ▼
    ┌────────┐
    │   CI   │ ◄── Lint, Type Check, Test, BDD
    └────┬───┘
         │
         ▼
    ┌─────────┐
    │ Merge   │
    │ to main │
    └────┬────┘
         │
         ▼
┌──────────────────┐
│ Version Bump     │ ◄── Auto-detect from commits
│ & Release        │     Update version, create tag & release
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Publish to PyPI  │ ◄── Build, test, publish
└──────────────────┘
         │
         ▼
    ┌────────┐
    │ Done!  │ Package available: pip install valid8r
    └────────┘
```

## Monitoring and Maintenance

### Regular Checks

- Review GitHub Actions logs for failed workflows
- Monitor PyPI releases: https://pypi.org/project/valid8r/
- Check coverage trends on Codecov
- Update Python versions in test matrix annually
- Rotate API tokens every 6 months

### Version History

View all releases: https://github.com/mikelane/valid8r/releases

### CI/CD Status

Check current status: https://github.com/mikelane/valid8r/actions

## Support

**Issues with workflows?**
1. Check workflow logs in Actions tab
2. Review documentation in this directory
3. Open an issue with workflow name and error details

**Questions about setup?**
1. Follow [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md)
2. Check troubleshooting sections
3. Review GitHub Actions documentation

## Contributing to Workflows

When updating workflows:

1. Test changes in a fork first
2. Use manual trigger to test (`workflow_dispatch`)
3. Document changes in commit message
4. Update documentation files as needed
5. Use `ci: update workflow...` commit type (won't trigger version bump)

Example:
```bash
git commit -m "ci: add Python 3.14 to test matrix

Updates CI workflow to test against Python 3.14 beta.
No changes to versioning or publishing logic."
```

## License

These workflow configurations are part of the valid8r project and follow the same MIT license.
