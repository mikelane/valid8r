Title: Fix README Quick Start examples and imports
Labels: documentation

The README Quick Start uses `parsers.int_parser` which does not exist (should be `parse_int`). Also ensure imports in README match the new public API once re-exports are added.

Acceptance Criteria:
```gherkin
Feature: README correctness
  Scenario: Quick Start parser function name
    Given the README.md file
    When I view the "Quick Start" section
    Then all code examples use "parsers.parse_int" instead of "parsers.int_parser"

  Scenario: Public API imports
    Given the README.md file
    When I view the import examples
    Then import lines use "from valid8r import parsers, validators, prompt"
```