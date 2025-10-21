# PyPI Token Setup Guide for valid8r

This guide will walk you through setting up PyPI publishing for the valid8r package.

## Step 1: Create PyPI Account (if you don't have one)

1. Go to: https://pypi.org/account/register/
2. Fill in the registration form:
   - Username: Choose a username
   - Email: Your email address
   - Password: Create a strong password
3. Verify your email address (check inbox)
4. **IMPORTANT**: Enable Two-Factor Authentication (2FA)
   - Go to: https://pypi.org/manage/account/
   - Click "Account security"
   - Click "Set up 2FA with an authentication app"
   - Use an app like Google Authenticator, Authy, or 1Password
   - Follow the setup wizard
   - **Save your recovery codes** in a safe place!

> ⚠️ **Note**: 2FA is REQUIRED to create API tokens. You cannot skip this step.

## Step 2: Generate PyPI API Token

1. Go to: https://pypi.org/manage/account/token/
2. Click **"Add API token"**
3. Configure the token:
   - **Token name**: `github-actions-valid8r`
   - **Scope**: Select **"Entire account"** (for now)
     - After first successful publish, you can create a project-specific token
4. Click **"Add token"**
5. **COPY THE TOKEN IMMEDIATELY** (you'll only see it once!)
   - Token format: `pypi-AgEIcHlwaS5vcmc...` (starts with `pypi-`)
   - Store it temporarily in a password manager or secure note

> ⚠️ **IMPORTANT**: You cannot see the token again after closing the page! If you lose it, you'll need to delete and create a new one.

## Step 3: Add Token to GitHub Secrets

### Option A: Using GitHub Web Interface (Recommended)

1. Go to: https://github.com/mikelane/valid8r/settings/secrets/actions
   - If you don't have access, you need repository admin permissions
2. Click **"New repository secret"**
3. Configure the secret:
   - **Name**: `PYPI_API_TOKEN` (must be exactly this)
   - **Value**: Paste the token from Step 2 (starts with `pypi-`)
4. Click **"Add secret"**
5. Verify the secret appears in the list (value will be hidden)

### Option B: Using GitHub CLI (Alternative)

```bash
# Make sure you have the token copied to clipboard
gh secret set PYPI_API_TOKEN --repo mikelane/valid8r

# When prompted, paste the token and press Enter
```

## Step 4: Configure GitHub Actions Permissions

1. Go to: https://github.com/mikelane/valid8r/settings/actions
2. Under **"Workflow permissions"**:
   - Select: ✅ **"Read and write permissions"**
   - Check: ✅ **"Allow GitHub Actions to create and approve pull requests"**
3. Click **"Save"**

## Step 5: Verify Configuration

### Check 1: Secrets are configured
```bash
gh secret list --repo mikelane/valid8r
```

Expected output:
```
PYPI_API_TOKEN      Updated YYYY-MM-DD
```

### Check 2: Workflows exist
```bash
ls -la .github/workflows/
```

Expected output:
```
ci.yml
publish-pypi.yml
version-and-release.yml
```

### Check 3: Permissions are correct
- Go to: https://github.com/mikelane/valid8r/settings/actions
- Confirm "Read and write permissions" is selected

## Step 6: Test the Setup (Optional but Recommended)

### Option A: Test with Test PyPI (Safest)

1. **Create Test PyPI account**: https://test.pypi.org/account/register/
2. **Generate Test PyPI token**: https://test.pypi.org/manage/account/token/
3. **Add to GitHub secrets** as `TEST_PYPI_API_TOKEN`
4. **Manually trigger test publish**:
   ```bash
   gh workflow run publish-pypi.yml -f test_pypi=true
   ```
5. **Check Test PyPI**: https://test.pypi.org/project/valid8r/
6. **Test installation**:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ \
               --extra-index-url https://pypi.org/simple/ valid8r
   ```

### Option B: Create a Test Release (Real PyPI)

1. **Create a small test commit**:
   ```bash
   git checkout -b feat/test-release
   echo "# Testing CI/CD" >> .github/CICD_TEST.md
   git add .github/CICD_TEST.md
   git commit -m "feat: test CI/CD pipeline"
   git push origin feat/test-release
   ```

2. **Create and merge PR**:
   ```bash
   gh pr create --title "feat: test CI/CD pipeline" \
                --body "Testing the automated release and PyPI publishing workflow"
   # After CI passes, merge the PR
   gh pr merge --squash
   ```

3. **Watch the automation**:
   - Go to: https://github.com/mikelane/valid8r/actions
   - Watch the workflows run:
     1. Version & Release workflow bumps version
     2. Publish to PyPI workflow builds and publishes
   - Check the release: https://github.com/mikelane/valid8r/releases
   - Check PyPI: https://pypi.org/project/valid8r/

4. **Test installation**:
   ```bash
   pip install valid8r
   python -c "from valid8r.core.parsers import parse_int; print(parse_int('42'))"
   ```

## Troubleshooting

### Issue: "Secret PYPI_API_TOKEN is not set"

**Solution**:
- Verify the secret name is EXACTLY `PYPI_API_TOKEN` (case-sensitive)
- Check you added it to the correct repository
- Verify you have admin access to the repository

### Issue: "Invalid credentials" when publishing

**Solution**:
- Token might be expired or invalid
- Regenerate token on PyPI: https://pypi.org/manage/account/token/
- Delete old secret and add new one to GitHub

### Issue: "2FA required" error

**Solution**:
- Enable 2FA on your PyPI account: https://pypi.org/manage/account/
- You MUST have 2FA enabled to create API tokens

### Issue: "Package name already taken"

**Solution**:
- Check if `valid8r` is already registered on PyPI
- If it's your package, you need to add your PyPI username as a maintainer
- If it's someone else's package, you need to choose a different name in `pyproject.toml`

### Issue: "Version already exists" (expected behavior)

This is **normal** and **expected**! The workflow will skip publishing if the version already exists.

**To publish a new version**:
1. Make changes and commit with conventional commit format
2. The version will auto-bump based on your commit
3. New version will be published automatically

### Issue: Workflow runs but doesn't publish

**Check**:
1. Does the version in `pyproject.toml` already exist on PyPI?
   ```bash
   pip index versions valid8r
   ```
2. Did the version actually bump?
   ```bash
   git log --oneline -5
   git tag -l
   ```
3. Check the workflow logs for error messages

## Security Best Practices

### Token Security
- ✅ Never commit tokens to git
- ✅ Never share tokens in chat/email
- ✅ Store tokens only in GitHub Secrets
- ✅ Use project-scoped tokens when possible
- ✅ Rotate tokens every 6-12 months

### Account Security
- ✅ Enable 2FA on PyPI account
- ✅ Use a strong, unique password
- ✅ Save recovery codes in a password manager
- ✅ Review account activity regularly

### Token Permissions
- 🔶 Initially use "Entire account" scope
- ✅ After first publish, create project-specific token:
  1. Go to: https://pypi.org/manage/project/valid8r/settings/
  2. Create new token with scope: "Project: valid8r"
  3. Update GitHub secret with new token
  4. Delete the "Entire account" token

## Monitoring

### Check Recent Publishes
```bash
# View PyPI package page
open https://pypi.org/project/valid8r/

# Check installed version
pip show valid8r

# View all versions
pip index versions valid8r
```

### Monitor Workflow Runs
```bash
# List recent workflow runs
gh run list --workflow=publish-pypi.yml --limit 5

# View specific run
gh run view <run-id>

# Watch live
gh run watch
```

### Check Download Stats
- PyPI Stats: https://pypistats.org/packages/valid8r
- Downloads badge: ![PyPI Downloads](https://img.shields.io/pypi/dm/valid8r)

## Next Steps

Once setup is complete:

1. ✅ Token configured in GitHub secrets
2. ✅ Permissions enabled for GitHub Actions
3. ✅ Test release created (optional)
4. ✅ Package published to PyPI

You're ready to use the automated workflow! 🎉

### Normal Developer Workflow

From now on, publishing is automatic:

```bash
# Make changes
git checkout -b feat/new-feature
# ... edit code ...

# Commit with conventional format
git commit -m "feat: add amazing feature"

# Create PR
gh pr create --title "feat: add amazing feature"

# After review and merge to main:
# - Version auto-bumps (0.1.0 → 0.2.0)
# - Release created on GitHub
# - Package published to PyPI
# - pip install valid8r gets the new version!
```

## Support

If you need help:
- Review `.github/WORKFLOWS.md` for detailed workflow documentation
- Check `.github/TROUBLESHOOTING.md` for common issues
- Review GitHub Actions logs for error messages
- Check PyPI account for token status

---

**Status**: Setup guide created on 2025-10-21
**Maintainer**: Mike Lane
**Repository**: https://github.com/mikelane/valid8r
