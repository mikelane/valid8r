# GitHub Repository Setup Checklist

This checklist ensures the valid8r repository is properly configured for the CI/CD workflows.

## Pre-Deployment Checklist

### 1. PyPI Account Setup

- [ ] Create PyPI account at https://pypi.org/account/register/
- [ ] Verify email address
- [ ] Enable 2FA (required for API tokens)
- [ ] (Optional) Create Test PyPI account at https://test.pypi.org/account/register/

### 2. PyPI API Tokens

#### Production PyPI Token

- [ ] Go to https://pypi.org/manage/account/token/
- [ ] Click "Add API token"
  - Token name: `github-actions-valid8r`
  - Scope: "Entire account" (change to project scope after first publish)
- [ ] Copy token (starts with `pypi-`, save securely)
- [ ] Store token in password manager

#### Test PyPI Token (Optional)

- [ ] Go to https://test.pypi.org/manage/account/token/
- [ ] Click "Add API token"
  - Token name: `github-actions-valid8r-test`
  - Scope: "Entire account"
- [ ] Copy token
- [ ] Store token in password manager

### 3. GitHub Repository Secrets

- [ ] Go to repository `Settings` → `Secrets and variables` → `Actions`
- [ ] Click "New repository secret"

**Required Secret**:
- [ ] Name: `PYPI_API_TOKEN`
  - Value: `pypi-...` (paste the production PyPI token)

**Optional Secrets**:
- [ ] Name: `TEST_PYPI_API_TOKEN`
  - Value: `pypi-...` (paste the test PyPI token)
- [ ] Name: `CODECOV_TOKEN`
  - Get from https://codecov.io/ after linking repository
  - Used for coverage reporting

### 4. GitHub Repository Settings

#### General Settings

- [ ] Go to `Settings` → `General`
- [ ] Ensure "Allow merge commits" is enabled (or squash/rebase as preferred)
- [ ] Consider enabling "Automatically delete head branches"

#### Actions Permissions

- [ ] Go to `Settings` → `Actions` → `General`
- [ ] Workflow permissions:
  - [ ] Select "Read and write permissions"
  - [ ] ✅ Check "Allow GitHub Actions to create and approve pull requests"

#### Branch Protection Rules

- [ ] Go to `Settings` → `Branches` → `Add rule`
- [ ] Branch name pattern: `main`

**Protection Settings**:
- [ ] ✅ Require pull request before merging
  - [ ] Required approvals: 1 (or more)
  - [ ] ✅ Dismiss stale pull request approvals when new commits are pushed
  - [ ] (Optional) ✅ Require review from Code Owners
- [ ] ✅ Require status checks to pass before merging
  - [ ] ✅ Require branches to be up to date before merging
  - [ ] Select required checks:
    - [ ] `Lint and Format Check`
    - [ ] `Type Check (mypy)`
    - [ ] `Test (Python 3.11)`
    - [ ] `Test (Python 3.12)`
    - [ ] `Test (Python 3.13)`
    - [ ] `BDD Tests`
    - [ ] `Build Documentation`
    - [ ] `Smoke Test`
    - [ ] `All Checks Passed`
- [ ] ✅ Require conversation resolution before merging
- [ ] (Optional) ✅ Require signed commits
- [ ] ✅ Require linear history
- [ ] ✅ Include administrators (enforce rules for admins too)
- [ ] ❌ DO NOT enable "Allow force pushes"
- [ ] ❌ DO NOT enable "Allow deletions"

#### Environments (for controlled PyPI publishing)

Create `pypi` environment:
- [ ] Go to `Settings` → `Environments` → `New environment`
- [ ] Name: `pypi`
- [ ] (Optional) Required reviewers: Add team members who should approve releases
- [ ] Environment secrets:
  - [ ] Add `PYPI_API_TOKEN` (same value as repository secret)

Create `test-pypi` environment (optional):
- [ ] Name: `test-pypi`
- [ ] Environment secrets:
  - [ ] Add `TEST_PYPI_API_TOKEN`

### 5. Codecov Integration (Optional)

- [ ] Go to https://codecov.io/
- [ ] Sign in with GitHub
- [ ] Add `mikelane/valid8r` repository
- [ ] Copy upload token
- [ ] Add `CODECOV_TOKEN` to GitHub secrets (see step 3)

### 6. Initial PyPI Registration

**Important**: PyPI requires the package name to be registered before the first publish.

**Option A: Manual First Publish** (Recommended)

```bash
# Ensure version is 0.1.0 in pyproject.toml
# Version is managed by semantic-release, but for first publish verify it's set correctly

# Build the package
uv build

# Publish to Test PyPI first (to verify)
uv publish --publish-url https://test.pypi.org/legacy/ --token pypi-...

# If test publish succeeds, publish to production PyPI
uv publish --token pypi-...
```

**Option B: Trusted Publisher** (More secure, no tokens needed)

- [ ] Go to https://pypi.org/manage/account/publishing/
- [ ] Click "Add a new pending publisher"
  - PyPI Project Name: `valid8r`
  - Owner: `mikelane`
  - Repository name: `valid8r`
  - Workflow filename: `publish-pypi.yml`
  - Environment name: `pypi`
- [ ] After setup, remove `password:` from workflow and it will use OIDC

### 7. Test Workflows

After setup is complete, test each workflow:

#### Test CI Workflow

- [ ] Create a test branch: `git checkout -b test/ci-workflow`
- [ ] Make a small change (e.g., update README)
- [ ] Push and create PR
- [ ] Verify all CI checks pass in PR
- [ ] Close PR without merging

#### Test Version Bump Workflow

- [ ] Create a feature branch: `git checkout -b feat/test-versioning`
- [ ] Make a small change
- [ ] Commit with conventional format: `git commit -m "feat: test versioning workflow"`
- [ ] Create PR and merge to main
- [ ] Check Actions tab for "Version and Release" workflow
- [ ] Verify:
  - [ ] Version bumped in pyproject.toml
  - [ ] Git tag created (e.g., v0.2.0)
  - [ ] GitHub Release created with changelog
- [ ] Check releases: https://github.com/mikelane/valid8r/releases

#### Test PyPI Publishing Workflow

After version bump creates a release:

- [ ] Go to Actions tab
- [ ] Check "Publish to PyPI" workflow
- [ ] Verify:
  - [ ] Package built successfully
  - [ ] Tests passed on built package
  - [ ] Published to PyPI (if configured)
- [ ] Test installation: `pip install valid8r`
- [ ] Check PyPI page: https://pypi.org/project/valid8r/

### 8. Verify Complete Setup

Final verification checklist:

- [ ] All GitHub secrets are configured
- [ ] Branch protection rules are active
- [ ] CI workflow runs on PRs
- [ ] Version workflow runs on main branch pushes
- [ ] PyPI workflow runs on releases
- [ ] Can install package from PyPI: `pip install valid8r`
- [ ] Documentation is up to date

## Troubleshooting Common Issues

### Issue: "Permission denied" when workflow tries to push

**Solution**:
- Go to `Settings` → `Actions` → `General`
- Set "Workflow permissions" to "Read and write permissions"
- Enable "Allow GitHub Actions to create and approve pull requests"

### Issue: "PyPI upload failed: 403 Forbidden"

**Possible causes**:
1. Invalid API token
   - Solution: Regenerate token and update secret
2. Package name already taken
   - Solution: Change package name in pyproject.toml
3. 2FA not enabled on PyPI account
   - Solution: Enable 2FA in PyPI account settings

### Issue: "Version already exists on PyPI"

**Expected behavior**: The workflow skips publishing if version exists.

**If you need to republish**:
1. Version bump happens automatically via semantic-release based on conventional commits
2. Commit with appropriate conventional commit type and push to trigger new release
3. Or manually trigger version bump: `gh workflow run semantic-release.yml`

### Issue: Required checks not appearing in branch protection

**Solution**:
1. The checks must run at least once before they appear in the list
2. Create a test PR to trigger all workflows
3. After workflows complete, the checks will be available in settings

### Issue: Workflow not triggering

**Check**:
1. Workflow file has correct `on:` triggers
2. Branch protection isn't blocking pushes
3. Actions are enabled: `Settings` → `Actions` → `General` → "Allow all actions"

## Post-Setup Maintenance

### After First Successful Publish

- [ ] Update PyPI API token scope from "Entire account" to "Project: valid8r"
- [ ] Go to https://pypi.org/manage/account/token/
- [ ] Delete old token
- [ ] Create new token with project scope
- [ ] Update `PYPI_API_TOKEN` secret in GitHub

### Regular Maintenance

- [ ] Review and rotate API tokens every 6 months
- [ ] Check for workflow updates in GitHub Actions marketplace
- [ ] Update Python versions in test matrix as new versions release
- [ ] Review branch protection rules periodically

### Documentation Updates

- [ ] Update README with installation instructions after first PyPI publish
- [ ] Add badge for PyPI version
- [ ] Add badge for CI status
- [ ] Add badge for coverage (if using Codecov)

Example badges for README.md:

```markdown
[![PyPI version](https://badge.fury.io/py/valid8r.svg)](https://badge.fury.io/py/valid8r)
[![CI](https://github.com/mikelane/valid8r/actions/workflows/ci.yml/badge.svg)](https://github.com/mikelane/valid8r/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/mikelane/valid8r/branch/main/graph/badge.svg)](https://codecov.io/gh/mikelane/valid8r)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
```

## Security Considerations

### Secrets Management

- [ ] Never commit secrets to repository
- [ ] Use GitHub encrypted secrets for all tokens
- [ ] Rotate tokens regularly
- [ ] Use environment-specific secrets for production vs test

### Branch Protection

- [ ] Prevent force pushes to main
- [ ] Require PR reviews
- [ ] Require status checks
- [ ] Protect against accidental deletions

### PyPI Security

- [ ] Enable 2FA on PyPI account
- [ ] Use scoped tokens (project-specific, not account-wide)
- [ ] Consider trusted publishers (OIDC) instead of API tokens
- [ ] Monitor PyPI package for unauthorized changes

## Support

If you encounter issues during setup:

1. Review this checklist
2. Check GitHub Actions logs
3. Review `.github/WORKFLOWS.md` documentation
4. Open an issue with details

## Checklist Complete!

Once all items are checked:

- [ ] Repository is fully configured
- [ ] CI/CD workflows are operational
- [ ] PyPI publishing is automated
- [ ] Team members are informed of conventional commit requirements
- [ ] Documentation is accessible

**Next Steps**:
- Share `.github/CONVENTIONAL_COMMITS.md` with team
- Add contributing guidelines to README
- Start using conventional commits for all changes
- Monitor first few releases to ensure smooth operation
