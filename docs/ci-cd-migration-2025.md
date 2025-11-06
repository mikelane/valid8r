# CI/CD Migration to 2025 Best Practices

**Completed**: November 2025
**Impact**: Security hardening, full automation, zero-touch releases

## What Changed

### 1. PyPI Trusted Publishing (Security)
- **Before**: API tokens stored in GitHub secrets
- **After**: OIDC authentication via GitHub Actions
- **Benefit**: Eliminated secret management, reduced attack surface

### 2. Dynamic Versioning (Automation)
- **Before**: Hardcoded version in pyproject.toml
- **After**: VCS-based dynamic versioning with hatch-vcs
- **Benefit**: Single source of truth (git tags), no manual version updates

### 3. Consolidated Workflow (Simplicity)
- **Before**: Two workflows (semantic-release.yml + publish-pypi.yml)
- **After**: Single unified release.yml workflow
- **Benefit**: Reduced duplication, clearer release process

### 4. SHA-Pinned Actions (Security)
- **Before**: Tag-based action references (@v4)
- **After**: Commit SHA references (@b4ffde65...)
- **Benefit**: Protected against supply chain attacks

### 5. Enhanced Testing (Quality)
- **Before**: Testing wheel installation only
- **After**: Isolated testing of both wheel and sdist
- **Benefit**: Catches packaging issues before PyPI publish

### 6. Composite Actions (Maintainability)
- **Before**: Duplicated setup steps across all jobs
- **After**: Reusable composite action for uv setup
- **Benefit**: DRY principle, easier maintenance

### 7. Upgraded Tools (Modern)
- **Before**: python-semantic-release v9.21.1, setup-uv v4
- **After**: python-semantic-release v10.4.1, setup-uv v6
- **Benefit**: Latest features, better performance

## Breaking Changes

None for end users. For contributors:
- Version is now managed by semantic-release (don't edit pyproject.toml version)
- Conventional commits are required for automatic versioning
- Release happens automatically on every merge to main

## Rollback Procedure

If issues occur:
1. Revert the merge commit that introduced the change
2. Temporarily re-enable API token: `gh secret set PYPI_API_TOKEN`
3. Investigate and fix
4. Re-apply changes when ready

## Validation

All changes validated through:
- [x] Test release on feature branch
- [x] Dry-run with semantic-release --noop
- [x] SHA-pinned actions verified
- [x] Composite action tested
- [ ] Successful production release (pending PyPI Trusted Publishing setup)

## Score Improvement

- **Starting Score**: 72/100
- **Target Score**: 100/100
- **Improvements**:
  - Security: +20 (PyPI Trusted Publishing + SHA-pinned actions)
  - Version Management: +10 (Dynamic versioning)
  - Workflow Consolidation: +8 (Unified release workflow)
  - Composite Actions: +3 (Reusable setup)
  - Enhanced Changelog: +4 (Template-based generation)
  - Documentation: +2 (Updated badges and docs)
  - Modernization: +3 (Upgraded dependencies)

---

**Document Version**: 1.0
**Last Updated**: November 5, 2025
**Maintained By**: mikelane
**Status**: Implementation Complete (Pending PyPI Trusted Publishing activation)
