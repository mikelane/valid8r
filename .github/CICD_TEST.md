# CI/CD Pipeline Test

This file was created to test the automated CI/CD pipeline for valid8r.

## Test Purpose

Verify that the complete automation workflow functions correctly:

1. ✅ CI runs on PR (tests, linting, type checking)
2. ✅ Auto version bump on merge to main (0.1.0 → 0.2.0)
3. ✅ GitHub Release created automatically
4. ✅ Package builds and publishes to PyPI
5. ✅ `pip install valid8r` installs the latest version

## Test Date

2025-10-21

## Expected Result

- Version bumps from 0.1.0 to 0.2.0 (feat: triggers minor bump)
- GitHub Release created with changelog
- Package available on PyPI
- Installable via: `pip install valid8r==0.2.0`

## Notes

This test uses a conventional commit with `feat:` prefix to trigger a minor version bump.
