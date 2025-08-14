Title: Update project metadata and include py.typed
Labels: packaging

- Replace placeholder authors in `pyproject.toml` with real values.
- Add `py.typed` file and package data so type hints are distributed to users.

Acceptance Criteria:
```gherkin
Feature: Packaging metadata and typing
  Scenario: Authors field is set
    Given the pyproject.toml file
    When I inspect the [tool.poetry] authors field
    Then it contains a real author name and email

  Scenario: py.typed distributed
    Given a built wheel for the project
    When I inspect the package contents
    Then a "py.typed" file exists under the package root (valid8r/py.typed)
    And the file is included in package data so type checkers detect typing
```