# CI/CD Setup Summary for valid8r

This document provides a comprehensive summary of the GitHub Actions CI/CD workflows that have been set up for the valid8r Python package.

## Overview

A complete CI/CD pipeline has been configured that automates:
- Code quality checks (linting, type checking, testing)
- Semantic versioning based on conventional commits
- GitHub releases with auto-generated changelogs
- PyPI package publishing

## Files Created

### Workflow Files (`.github/workflows/`)

1. **`ci.yml`** (existing, confirmed working)
   - Runs on every PR and push to main
   - Executes linting, type checking, unit tests, BDD tests, docs build, and smoke tests
   - Tests against Python 3.11, 3.12, and 3.13
   - Location: `/Users/mikelane/dev/valid8r/.github/workflows/ci.yml`

2. **`version-and-release.yml`** (newly created)
   - Runs on every push to main
   - Analyzes commits using conventional commits format
   - Automatically bumps version in `pyproject.toml`
   - Creates git tags and GitHub releases
   - Generates categorized changelog
   - Location: `/Users/mikelane/dev/valid8r/.github/workflows/version-and-release.yml`

3. **`publish-pypi.yml`** (newly created)
   - Runs when GitHub release is published
   - Checks if version already exists on PyPI (prevents duplicates)
   - Builds wheel and source distribution
   - Tests built package on all Python versions
   - Publishes to PyPI automatically
   - Location: `/Users/mikelane/dev/valid8r/.github/workflows/publish-pypi.yml`

### Documentation Files (`.github/`)

4. **`WORKFLOWS.md`**
   - Complete guide to all workflows
   - Detailed explanation of triggers, jobs, and processes
   - Developer workflow guide
   - Conventional commits specification
   - Troubleshooting guide
   - Location: `/Users/mikelane/dev/valid8r/.github/WORKFLOWS.md`

5. **`CONVENTIONAL_COMMITS.md`**
   - Quick reference for commit message format
   - Examples for every commit type
   - Version bump rules
   - Decision tree for choosing commit types
   - Anti-patterns to avoid
   - Location: `/Users/mikelane/dev/valid8r/.github/CONVENTIONAL_COMMITS.md`

6. **`SETUP_CHECKLIST.md`**
   - Step-by-step repository setup guide
   - PyPI account and token configuration
   - GitHub secrets setup
   - Branch protection configuration
   - Testing procedures
   - Troubleshooting common issues
   - Location: `/Users/mikelane/dev/valid8r/.github/SETUP_CHECKLIST.md`

7. **`README.md`** (`.github` directory)
   - Overview of all GitHub configuration
   - Quick links to documentation
   - Summary of workflows
   - Quick start for contributors
   - Location: `/Users/mikelane/dev/valid8r/.github/README.md`

## Required Secrets Setup

Before the workflows can publish to PyPI, you need to configure GitHub secrets:

### Step 1: Create PyPI API Token

1. Go to https://pypi.org/account/register/ and create an account (if needed)
2. Enable 2FA (required for API tokens)
3. Go to https://pypi.org/manage/account/token/
4. Click "Add API token"
   - Name: `github-actions-valid8r`
   - Scope: "Entire account" (change to project scope after first publish)
5. Copy the token (starts with `pypi-`) - you won't see it again!

### Step 2: Add Secret to GitHub

1. Go to https://github.com/mikelane/valid8r/settings/secrets/actions
2. Click "New repository secret"
3. Name: `PYPI_API_TOKEN`
4. Value: Paste the token from step 1
5. Click "Add secret"

### Step 3: Configure GitHub Actions Permissions

1. Go to https://github.com/mikelane/valid8r/settings/actions
2. Under "Workflow permissions":
   - Select "Read and write permissions"
   - Check "Allow GitHub Actions to create and approve pull requests"
3. Click "Save"

### Optional: Test PyPI Token

For testing before publishing to production PyPI:

1. Create Test PyPI account: https://test.pypi.org/account/register/
2. Generate API token (same process as above)
3. Add `TEST_PYPI_API_TOKEN` secret to GitHub

## How It Works

### Workflow 1: Continuous Integration (Existing)

```
Pull Request Created → CI Workflow Triggers
                       ├── Lint Check (ruff)
                       ├── Format Check (ruff)
                       ├── Type Check (mypy)
                       ├── Unit Tests (pytest on 3.11, 3.12, 3.13)
                       ├── BDD Tests (behave)
                       ├── Documentation Build
                       └── Smoke Test
                            ↓
                       All Checks Pass → Ready to Merge
```

### Workflow 2: Version and Release (New)

```
Merge to Main → Version & Release Workflow Triggers
                ↓
             Analyze Commits Since Last Tag
                ↓
             Determine Version Bump:
             - feat: → Minor (0.1.0 → 0.2.0)
             - fix:/docs:/etc. → Patch (0.1.0 → 0.1.1)
             - BREAKING CHANGE → Major (0.1.0 → 1.0.0)
                ↓
             Update pyproject.toml
                ↓
             Commit & Push Version Bump
                ↓
             Create Git Tag (v0.2.0)
                ↓
             Generate Changelog from Commits
                ↓
             Create GitHub Release
```

### Workflow 3: Publish to PyPI (New)

```
GitHub Release Published → Publish Workflow Triggers
                          ↓
                       Check Version on PyPI
                          ↓
                    Version Already Exists?
                    ├── Yes → Skip (no duplicate)
                    └── No → Continue
                              ↓
                          Build Package (wheel + sdist)
                              ↓
                          Test Built Package on 3.11, 3.12, 3.13
                              ↓
                          Publish to PyPI
                              ↓
                          Verify Publication
```

## Conventional Commits Format

All commits must follow this format to trigger automatic versioning:

```
<type>[optional scope]: <description>

[optional body]

[optional footer]
```

### Version Bump Rules

| Commit Type | Example | Version Bump |
|-------------|---------|--------------|
| `feat:` | `feat: add UUID parsing` | 0.1.0 → 0.2.0 (minor) |
| `fix:` | `fix: handle None in validator` | 0.1.0 → 0.1.1 (patch) |
| `docs:` | `docs: update README` | 0.1.0 → 0.1.1 (patch) |
| `refactor:` | `refactor: simplify parser` | 0.1.0 → 0.1.1 (patch) |
| `perf:` | `perf: optimize validation` | 0.1.0 → 0.1.1 (patch) |
| `test:` | `test: add edge cases` | 0.1.0 → 0.1.1 (patch) |
| `chore:` | `chore: update deps` | 0.1.0 → 0.1.1 (patch) |
| `ci:` | `ci: update workflow` | No bump |
| `feat!:` or `BREAKING CHANGE:` | `feat!: redesign API` | 0.1.0 → 1.0.0 (major) |

### Examples

**Feature (minor bump)**:
```bash
git commit -m "feat(parsers): add phone number validation

Supports international formats using E.164 standard.
Returns PhoneNumber structured type."
```

**Bug Fix (patch bump)**:
```bash
git commit -m "fix(validators): maximum validator now handles floats correctly"
```

**Breaking Change (major bump)**:
```bash
git commit -m "feat!: migrate to Result monad

BREAKING CHANGE: All parsers now return Result[T, Error] instead of Maybe[T].
See migration guide in docs."
```

**Documentation (patch bump)**:
```bash
git commit -m "docs: add tutorial for custom validators"
```

**No version bump**:
```bash
git commit -m "ci: add Python 3.14 to test matrix"
```

## Developer Workflow

### Making Changes

1. **Create feature branch**:
   ```bash
   git checkout -b feat/add-parser
   ```

2. **Make changes and commit** (using conventional format):
   ```bash
   git add .
   git commit -m "feat(parsers): add IP address validation"
   ```

3. **Push and create PR**:
   ```bash
   git push origin feat/add-parser
   gh pr create --fill
   ```

4. **Wait for CI checks** - All must pass before merging

5. **Get review approval and merge**

6. **Automatic version bump** - Happens when merged to main

7. **Automatic PyPI publish** - Happens after GitHub release is created

### What Happens After Merge

When you merge a PR with a `feat:` commit:

1. **Version bump workflow runs**:
   - Detects `feat:` commit
   - Bumps minor version (e.g., 0.1.0 → 0.2.0)
   - Updates `pyproject.toml`
   - Commits the change
   - Creates tag `v0.2.0`
   - Generates changelog
   - Creates GitHub Release

2. **PyPI publish workflow runs**:
   - Triggered by the GitHub Release
   - Checks if v0.2.0 exists on PyPI
   - Builds the package
   - Tests it on all Python versions
   - Publishes to PyPI
   - Package is now available: `pip install valid8r==0.2.0`

## Manual Operations

### Manual Version Bump

If you need to override automatic version detection:

```bash
# Trigger minor version bump manually
gh workflow run version-and-release.yml -f version_bump=minor

# Or major/patch
gh workflow run version-and-release.yml -f version_bump=major
gh workflow run version-and-release.yml -f version_bump=patch
```

### Test PyPI Publishing

To test the publishing workflow without affecting production:

```bash
# Publish to Test PyPI
gh workflow run publish-pypi.yml -f test_pypi=true

# Then test installation
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ valid8r
```

## Testing the Setup

### Before First Production Release

1. **Test with Test PyPI**:
   ```bash
   # First, ensure version in pyproject.toml is something like 0.1.0-alpha1
   poetry version 0.1.0-alpha1

   # Commit and push
   git add pyproject.toml
   git commit -m "chore: set alpha version for testing"
   git push

   # Manually trigger test publish
   gh workflow run publish-pypi.yml -f test_pypi=true
   ```

2. **Verify test publish**:
   ```bash
   # Install from Test PyPI
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ valid8r

   # Test import
   python -c "from valid8r import parsers; print(parsers.parse_int('42'))"
   ```

3. **Reset to production version**:
   ```bash
   poetry version 0.1.0
   git add pyproject.toml
   git commit -m "chore: reset to production version"
   git push
   ```

### First Production Release

1. **Create a feature to trigger version bump**:
   ```bash
   git checkout -b feat/initial-release
   # Make a small change or update docs
   git commit -m "feat: initial PyPI release"
   git push origin feat/initial-release
   gh pr create --title "feat: initial PyPI release" --body "First production release to PyPI"
   ```

2. **Merge PR** - This will trigger:
   - Version bump (0.1.0 → 0.2.0)
   - GitHub Release creation
   - PyPI publishing

3. **Verify release**:
   - Check https://github.com/mikelane/valid8r/releases
   - Check https://pypi.org/project/valid8r/
   - Test: `pip install valid8r`

## Monitoring and Maintenance

### Check Workflow Status

- View all workflow runs: https://github.com/mikelane/valid8r/actions
- Check latest releases: https://github.com/mikelane/valid8r/releases
- Monitor PyPI: https://pypi.org/project/valid8r/

### Regular Maintenance

- **Monthly**: Review failed workflows and fix issues
- **Quarterly**: Update Python versions in test matrix
- **Semi-annually**: Rotate PyPI API tokens
- **Annually**: Review and update branch protection rules

## Troubleshooting

### Issue: Version Not Bumping

**Symptom**: Merged to main but no version bump occurred

**Cause**: Commits don't follow conventional format

**Solution**:
```bash
# Check recent commits
git log --oneline -5

# If needed, trigger manual bump
gh workflow run version-and-release.yml -f version_bump=patch
```

### Issue: PyPI Publishing Failed - 403 Forbidden

**Cause**: API token issue

**Solutions**:
1. Check token is correctly set in GitHub secrets
2. Ensure PyPI account has 2FA enabled
3. Verify token hasn't expired
4. Regenerate token and update secret if needed

### Issue: PyPI Publishing Skipped - Version Exists

**Symptom**: Workflow says "Version already exists on PyPI"

**Cause**: This is expected behavior - prevents duplicate uploads

**Solution**: This is normal. To publish new version, make new commits and merge to trigger version bump

### Issue: CI Checks Failing

**Solution**: Run checks locally:
```bash
poetry run ruff check .
poetry run ruff format --check .
poetry run mypy valid8r
poetry run pytest
poetry run behave tests/bdd/features
```

Fix issues and push again.

### Issue: Permission Denied in Workflow

**Symptom**: Workflow fails to push commits or create tags

**Solution**:
1. Go to Settings → Actions → General
2. Set "Workflow permissions" to "Read and write permissions"
3. Enable "Allow GitHub Actions to create and approve pull requests"

## Security Best Practices

1. **Never commit secrets** - Always use GitHub encrypted secrets
2. **Rotate tokens regularly** - Every 6 months minimum
3. **Use scoped tokens** - After first publish, change PyPI token to project-scoped
4. **Enable 2FA** - Required on PyPI account
5. **Branch protection** - Prevent force pushes and require reviews
6. **Review workflow runs** - Monitor for suspicious activity

## Documentation Reference

All documentation is in the `.github/` directory:

- **[.github/WORKFLOWS.md](file:///Users/mikelane/dev/valid8r/.github/WORKFLOWS.md)** - Complete workflows documentation (30+ pages)
- **[.github/CONVENTIONAL_COMMITS.md](file:///Users/mikelane/dev/valid8r/.github/CONVENTIONAL_COMMITS.md)** - Commit message quick reference
- **[.github/SETUP_CHECKLIST.md](file:///Users/mikelane/dev/valid8r/.github/SETUP_CHECKLIST.md)** - Step-by-step setup guide
- **[.github/README.md](file:///Users/mikelane/dev/valid8r/.github/README.md)** - GitHub configuration overview

## Next Steps

### Immediate (Required for Publishing)

1. **Create PyPI account** and generate API token
2. **Add `PYPI_API_TOKEN`** to GitHub repository secrets
3. **Configure Actions permissions** (read/write)
4. **Test with Test PyPI** (optional but recommended)

### Short-term (Within First Week)

1. **Configure branch protection** rules on main
2. **Test the complete workflow** with a real feature
3. **Share documentation** with team members
4. **Set up Codecov** (optional, for coverage reporting)

### Long-term (Ongoing)

1. **Monitor releases** and ensure smooth operation
2. **Update documentation** as workflows evolve
3. **Rotate API tokens** every 6 months
4. **Review and improve** based on team feedback

## Support

**Questions or issues?**

1. Check the documentation in `.github/` directory
2. Review workflow logs in the Actions tab
3. Check this summary document
4. Open an issue with details

## Success Criteria

You'll know the setup is working when:

- ✅ CI runs on every PR and all checks pass
- ✅ Merging to main creates a new version and release
- ✅ GitHub releases appear at https://github.com/mikelane/valid8r/releases
- ✅ Package publishes to PyPI automatically
- ✅ You can install with `pip install valid8r`
- ✅ Version in PyPI matches version in pyproject.toml

## Summary

This CI/CD pipeline provides:

- **Automated quality checks** - Catch bugs before they reach production
- **Semantic versioning** - Consistent, predictable version numbers
- **Automatic releases** - No manual steps needed
- **PyPI publishing** - Package available immediately after merge
- **Safety checks** - Prevents duplicates and validates before publishing
- **Full transparency** - All changes tracked in git and releases

The entire process from PR to PyPI is fully automated, requiring only that developers follow conventional commit format. This ensures consistent quality, reduces manual work, and makes releases predictable and reliable.

---

**Setup Status**: Workflows configured ✓ | Documentation complete ✓ | Ready for secrets configuration

**Next Action**: Follow [SETUP_CHECKLIST.md](file:///Users/mikelane/dev/valid8r/.github/SETUP_CHECKLIST.md) to complete repository setup.
