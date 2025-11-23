Feature: String Parser with Type Validation
  As a developer using Valid8r
  I want to parse and validate string inputs
  So that I can ensure type safety before content validation

  Scenario: Parse valid string input
    Given the input "hello world"
    When I call parse_str with the input
    Then it returns Success with value "hello world"

  Scenario: Parse empty string (valid type, empty content)
    Given the input ""
    When I call parse_str with the input
    Then it returns Success with value ""

  Scenario: Parse string with only whitespace
    Given the input "   "
    When I call parse_str with the input
    Then it returns Success with value "   "

  Scenario: Parse unicode string
    Given the input "hello 世界 🌍"
    When I call parse_str with the input
    Then it returns Success with value "hello 世界 🌍"

  Scenario: Parse very long string
    Given the input is a string with 10000 characters
    When I call parse_str with the input
    Then it returns Success with the 10000 character string

  Scenario: Reject None input
    Given the input None
    When I call parse_str with the input
    Then it returns Failure with message containing "cannot be None"

  Scenario: Reject integer input
    Given the input 42
    When I call parse_str with the input
    Then it returns Failure with message containing "Expected string, got int"

  Scenario: Reject float input
    Given the input 3.14
    When I call parse_str with the input
    Then it returns Failure with message containing "Expected string, got float"

  Scenario: Reject boolean input
    Given the input True
    When I call parse_str with the input
    Then it returns Failure with message containing "Expected string, got bool"

  Scenario: Reject dict input
    Given the input {"key": "value"}
    When I call parse_str with the input
    Then it returns Failure with message containing "Expected string, got dict"

  Scenario: Reject list input
    Given the input ["a", "b", "c"]
    When I call parse_str with the input
    Then it returns Failure with message containing "Expected string, got list"

  Scenario: Custom error message for type mismatch
    Given the input 42
    And the error message "Invalid username format"
    When I call parse_str with the input and custom error message
    Then it returns Failure with message "Invalid username format"

  Scenario: Use in Schema with required string field
    Given a schema with a required "name" field using parse_str
    When I validate data {"name": "Alice"}
    Then validation succeeds with name "Alice"

  Scenario: Schema rejects non-string type in string field
    Given a schema with a required "name" field using parse_str
    When I validate data {"name": 42}
    Then validation fails with error at path ".name" containing "Expected string"

  Scenario: Combine with validators for content validation
    Given parse_str to validate type
    And non_empty_string validator for content
    When I parse and validate ""
    Then type validation succeeds but content validation fails

  Scenario: Chain parse_str with custom validator
    Given parse_str parser
    And a custom validator checking string length
    When I parse "hello" and validate
    Then parsing succeeds and validation applies to the string value
