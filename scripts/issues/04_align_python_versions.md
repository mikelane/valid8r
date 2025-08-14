Title: Align Python version configuration across tools
Labels: tooling

`pyproject.toml` declares Python ">=3.11", ruff targets 3.12, while mypy is set to 3.10. Align these to the supported versions.

Acceptance Criteria:
```gherkin
Feature: Consistent Python versions
  Scenario: Mypy version alignment
    Given the pyproject configuration
    When I review the [tool.mypy] section
    Then "python_version" equals "3.11" or higher consistent with [tool.poetry.dependencies.python]

  Scenario: Ruff target alignment
    Given the pyproject configuration
    When I review ruff target-version
    Then it matches a supported minor (e.g., "py311" or "py312") and is consistent across docs and classifiers
```