Title: Introduce schema API with error accumulation and field paths
Labels: enhancement, design

Provide a schema-based API to validate dict-like inputs and nested structures, accumulating multiple errors with paths.

Acceptance Criteria:
```gherkin
Feature: Schema validation
  Scenario: Collect multiple field errors
    Given input {"age": "-1", "email": "bad"}
    And a schema with age parse_int & minimum(0), and email parse_email
    When I validate the input
    Then the result contains two errors with paths ".age" and ".email"
```