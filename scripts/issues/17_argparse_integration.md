Title: Add argparse integration helpers and documentation
Labels: enhancement, docs, integration

Provide helper functions and documentation to use Valid8r parsers/validators with argparse types/choices and post-parse validation.

Acceptance Criteria:
```gherkin
Feature: argparse integration
  Scenario: Example code compiles and runs
    Given the argparse integration example in docs
    When I run the snippet
    Then valid arguments parse successfully
    And invalid arguments display helpful validation errors
```