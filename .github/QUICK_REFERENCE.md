# Quick Reference - valid8r CI/CD

## Commit Message Format

```
<type>[optional scope]: <description>
```

### Version Bumps

| Type | Version Change | Example |
|------|----------------|---------|
| `feat:` | 0.1.0 → **0.2.0** | `feat: add UUID parser` |
| `fix:` | 0.1.0 → **0.1.1** | `fix: handle None values` |
| `docs:` | 0.1.0 → **0.1.1** | `docs: update README` |
| `feat!:` | 0.1.0 → **1.0.0** | `feat!: redesign API` |
| `ci:` | **no change** | `ci: update workflow` |

## Common Commands

### Development

```bash
# Create feature branch
git checkout -b feat/my-feature

# Commit with conventional format
git commit -m "feat(parsers): add phone validation"

# Create PR
gh pr create --fill

# Run checks locally
uv run pytest
uv run mypy valid8r
uv run ruff check .
```

### Manual Workflow Triggers

```bash
# Manual version bump
gh workflow run version-and-release.yml -f version_bump=minor

# Test PyPI publish
gh workflow run publish-pypi.yml -f test_pypi=true

# Manual CI run
gh workflow run ci.yml
```

### Check Status

```bash
# View workflow runs
gh run list

# View latest release
gh release view

# Check PyPI version
pip index versions valid8r
```

## Workflow Sequence

1. **Create PR** → CI runs (tests, linting, type checking)
2. **Merge to main** → Version bump + GitHub Release
3. **Release created** → Publish to PyPI
4. **Published** → Available via `pip install valid8r`

## Secrets Required

- `PYPI_API_TOKEN` - Required for PyPI publishing
- `TEST_PYPI_API_TOKEN` - Optional for testing
- `CODECOV_TOKEN` - Optional for coverage

## Documentation

- **[WORKFLOWS.md](WORKFLOWS.md)** - Complete workflows guide
- **[CONVENTIONAL_COMMITS.md](CONVENTIONAL_COMMITS.md)** - Commit format reference
- **[SETUP_CHECKLIST.md](SETUP_CHECKLIST.md)** - Repository setup steps
- **[README.md](README.md)** - GitHub config overview

## Links

- Workflows: https://github.com/mikelane/valid8r/actions
- Releases: https://github.com/mikelane/valid8r/releases
- PyPI: https://pypi.org/project/valid8r/

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Version not bumping | Check commits follow `feat:`, `fix:` format |
| PyPI publish fails | Verify `PYPI_API_TOKEN` secret is set |
| CI checks failing | Run locally: `poetry run pytest && poetry run ruff check .` |
| Permission denied | Enable write permissions in Actions settings |

## Example Commits

```bash
# Feature (minor)
git commit -m "feat(parsers): add email validation"

# Bug fix (patch)
git commit -m "fix(validators): correct regex pattern"

# Breaking change (major)
git commit -m "feat!: replace Maybe with Result

BREAKING CHANGE: All parsers return Result instead of Maybe"

# Documentation (patch)
git commit -m "docs: add examples to tutorial"

# No version change
git commit -m "ci: add Python 3.14 to matrix"
```
