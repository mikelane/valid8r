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
│   ├── semantic-release.yml        # Automated semantic versioning, changelog, and PyPI publishing
│   ├── welcome.yml                 # Welcome bot for first-time contributors
│   ├── labeler.yml                 # Auto-label PRs based on files changed
│   ├── size-label.yml              # PR size classification (XS/S/M/L/XL)
│   └── stale.yml                   # Close inactive issues and PRs
├── ISSUE_TEMPLATE/
│   └── ... (issue templates)
├── labeler.yml                      # Configuration for auto-labeler
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
- Unit tests on Python 3.11, 3.12, 3.13, 3.14
- BDD tests with behave
- Documentation build
- Smoke tests
- Coverage reporting with Codecov

**Status**: ✅ All checks must pass before merging

### 2. Semantic Release Workflow (`workflows/semantic-release.yml`)

**Runs on**: Pushes to main branch (and manual trigger)

**Purpose**: Fully automated versioning, changelog generation, and PyPI publishing

**Process**:
1. Analyzes commit messages since last release using python-semantic-release
2. Determines version bump (major, minor, or patch) based on conventional commits
3. Updates `pyproject.toml` version automatically
4. Generates comprehensive changelog from commit history
5. Creates git tag (e.g., `v0.3.0`)
6. Creates GitHub Release with generated changelog
7. Builds package (wheel and source distribution)
8. Publishes to PyPI automatically

**Versioning Rules** (Conventional Commits):
- `feat:` commits → Minor version bump (0.1.0 → 0.2.0)
- `fix:`, `perf:` → Patch version bump (0.1.0 → 0.1.1)
- `BREAKING CHANGE:` or `feat!:` → Major version bump (0.1.0 → 1.0.0)
- `docs:`, `style:`, `refactor:`, `test:`, `build:`, `ci:`, `chore:` → No version bump

**Fully Automated**: No manual intervention required after merging PRs with conventional commits

### 3. Welcome Bot (`workflows/welcome.yml`)

**Runs on**: First-time issue or PR from contributor

**Purpose**: Welcome new contributors to the project

**Actions**:
- Posts friendly welcome message on first issue
- Posts contribution guidelines on first PR
- Links to CONTRIBUTING.md and code of conduct

### 4. Auto-Labeler (`workflows/labeler.yml`)

**Runs on**: PR opened, synchronized, or reopened

**Purpose**: Automatically label PRs based on changed files

**Labels Applied**:
- `core` - Changes to core library files
- `parsers` - Changes to parser modules
- `validators` - Changes to validator modules
- `tests` - Changes to test files
- `documentation` - Changes to docs or markdown files
- `ci-cd` - Changes to workflows or CI configuration

**Configuration**: `.github/labeler.yml`

### 5. Size Labeler (`workflows/size-label.yml`)

**Runs on**: PR opened, synchronized, or reopened

**Purpose**: Classify PRs by size for easier review prioritization

**Size Classifications**:
- `size/XS` - < 10 lines changed
- `size/S` - < 100 lines changed
- `size/M` - < 500 lines changed
- `size/L` - < 1000 lines changed
- `size/XL` - > 1000 lines changed (suggests breaking into smaller PRs)

**Ignores**: poetry.lock file

### 6. Stale Bot (`workflows/stale.yml`)

**Runs on**: Daily at midnight UTC (and manual trigger)

**Purpose**: Manage inactive issues and pull requests

**Behavior**:
- Marks issues/PRs as stale after 60 days of inactivity
- Closes stale items after additional 7 days
- Exempts items with labels: `keep-open`, `bug`, `security`, `enhancement` (issues) or `work-in-progress`, `blocked` (PRs)

**Override**: Add `keep-open` label to prevent auto-closure

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
uv run pytest
uv run mypy valid8r
uv run ruff check .

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
- `GH_TOKEN` - GitHub Personal Access Token with repo permissions (for semantic-release)

**Optional**:
- `CODECOV_TOKEN` - Codecov token for coverage reporting (auto-detected if repository is public)

### Branch Protection

The `main` branch should be protected with these rules:
- Require pull request reviews (1+ approvals)
- Require status checks to pass:
  - Lint and Format Check
  - Type Check (mypy)
  - Test (Python 3.11, 3.12, 3.13, 3.14)
  - BDD Tests
  - All Checks Passed
- Require conversation resolution
- Require linear history
- Prevent force pushes
- Prevent deletions

### Manual Triggers

Workflows can be manually triggered via GitHub Actions UI or CLI:

```bash
# Manual semantic release (analyzes commits and publishes if needed)
gh workflow run semantic-release.yml

# Manual CI run
gh workflow run ci.yml

# Manual stale issue/PR check
gh workflow run stale.yml
```

## Troubleshooting

### Workflows Not Running

**Check**:
1. GitHub Actions enabled: `Settings` → `Actions` → `General`
2. Workflow files in correct location: `.github/workflows/`
3. Valid YAML syntax: Use `yamllint` or GitHub's editor

### Version Not Bumping

**Check**:
1. Commits follow conventional commits format (see CONTRIBUTING.md)
2. Commits since last release use types that trigger bumps: `feat:`, `fix:`, `perf:`
3. Not only non-releasing types (`docs:`, `ci:`, `build:`, `chore:`, `style:`, `refactor:`, `test:`)
4. Check semantic-release workflow logs for analysis details

### PyPI Publishing Failed

**Check**:
1. `GH_TOKEN` secret is set correctly with repo permissions
2. python-semantic-release configuration in pyproject.toml is correct
3. Package name not already taken
4. Version not already published
5. Check semantic-release workflow logs for detailed error messages

### CI Checks Failing

**Run locally**:
```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy valid8r
uv run pytest
uv run behave tests/bdd/features
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
┌─────────────────────┐
│ Create PR           │
│ (feat: new parser)  │
└──────────┬──────────┘
           │
           ▼
      ┌────────┐
      │   CI   │ ◄── Lint, Type Check, Test, BDD, Coverage
      └────┬───┘
           │
           ├─► Auto-labeler (file-based labels)
           ├─► Size labeler (XS/S/M/L/XL)
           └─► Welcome bot (first-time contributors)
           │
           ▼
      ┌─────────┐
      │ Merge   │
      │ to main │
      └────┬────┘
           │
           ▼
┌──────────────────────┐
│ Semantic Release     │ ◄── python-semantic-release analyzes commits
│                      │     • Determine version bump
│ 1. Version Bump      │     • Generate changelog
│ 2. Changelog         │     • Create tag & GitHub Release
│ 3. GitHub Release    │     • Build package
│ 4. PyPI Publish      │     • Publish to PyPI
└──────────────────────┘
           │
           ▼
      ┌────────┐
      │ Done!  │ Package available: pip install valid8r
      └────────┘

Background:
  Stale Bot → Runs daily to manage inactive issues/PRs
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
git commit -m "ci: update semantic-release configuration

Adjusts version_toml paths in semantic-release config.
No changes to application code or test logic."
```

## License

These workflow configurations are part of the valid8r project and follow the same MIT license.
