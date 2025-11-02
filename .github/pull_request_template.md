# Description

## Summary

<!-- Provide a clear and concise description of the changes in this PR -->

## Motivation and Context

<!-- Why is this change required? What problem does it solve? -->
<!-- If it fixes an open issue, please link to the issue here using #issue_number -->

Fixes #

## Type of Change

<!-- Mark the relevant option with an 'x' -->

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Refactoring (no functional changes, code improvements)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Test coverage improvement

# Testing

## Test Coverage

<!-- Describe the tests you added or modified -->

- [ ] Unit tests added/updated
- [ ] BDD tests added/updated (if applicable)
- [ ] All tests pass locally (`uv run tox`)
- [ ] Test coverage maintained or improved

## Test Evidence

<!-- Paste relevant test output showing your tests pass -->

```
# Example:
$ uv run pytest tests/unit/test_my_feature.py
================================ test session starts =================================
collected 15 items

tests/unit/test_my_feature.py ............... [100%]
================================ 15 passed in 0.45s ==================================
```

# Code Quality

## Checklist

- [ ] Code follows the project's style guidelines (`uv run ruff check .`)
- [ ] Code is formatted properly (`uv run ruff format .`)
- [ ] Type hints are complete and pass mypy (`uv run mypy valid8r`)
- [ ] Docstrings added/updated for public API
- [ ] `__all__` exports updated if public API changed
- [ ] CLAUDE.md updated if architecture/patterns changed
- [ ] No breaking changes to public API (or clearly documented)

## Breaking Changes

<!-- If this PR includes breaking changes, describe them here -->
<!-- Include migration guide for users if applicable -->

N/A

# Documentation

- [ ] README.md updated (if needed)
- [ ] API documentation updated (docstrings)
- [ ] Usage examples added (if new feature)
- [ ] Sphinx docs build successfully (`uv run docs-build`)

# Additional Notes

## Dependencies

<!-- List any new dependencies added and justify why -->

N/A

## Performance Impact

<!-- Describe any performance implications -->

N/A

## Screenshots/Examples

<!-- If applicable, add screenshots or code examples showing the new functionality -->

```python
# Example usage
from valid8r import parsers

result = parsers.parse_int("42")
```

## Reviewer Notes

<!-- Any specific areas you'd like reviewers to focus on? -->

---

**Reviewer Checklist:**

- [ ] Code changes are clear and well-documented
- [ ] Tests adequately cover the changes
- [ ] No obvious bugs or security issues
- [ ] Performance implications are acceptable
- [ ] Documentation is complete and accurate
- [ ] Public API changes are backward compatible (or breaking changes justified)
