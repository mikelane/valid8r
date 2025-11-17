Feature: Schema validation with error accumulation
  As a developer using valid8r
  I want to validate complex objects against schemas
  So that I can collect all validation errors at once with clear field paths

  Background:
    Given the schema validation API is available

  Scenario: Validate object with all valid fields
    Given a schema with age as parse_int and email as parse_email
    And input with age "25" and email "alice@example.com"
    When Alice validates the input
    Then the validation succeeds
    And the result contains age 25
    And the result contains email "alice@example.com"

  Scenario: Collect multiple field errors
    Given a schema with age as parse_int and email as parse_email
    And input with age "invalid" and email "not-an-email"
    When Alice validates the input
    Then the validation fails
    And the result contains two errors
    And the result contains an error for path ".age"
    And the result contains an error for path ".email"

  Scenario: Track field paths for nested objects
    Given a schema with nested user object
    And the user schema has name as non_empty_string and email as parse_email
    And input with user name "" and user email "bad"
    When Alice validates the input
    Then the validation fails
    And the result contains an error for path ".user.name"
    And the result contains an error for path ".user.email"

  Scenario: Validate with combined validators
    Given a schema with age as parse_int with minimum 0 and maximum 120
    And input with only age "-5"
    When Alice validates the input
    Then the validation fails
    And the result contains an error for path ".age"
    And the validation error message contains "at least"

  Scenario: Validate optional fields
    Given a schema with required name and optional age
    And input with only name "Alice"
    When Alice validates the input
    Then the validation succeeds
    And the result contains name "Alice"
    And the result does not contain age

  Scenario: Missing required field fails validation
    Given a schema with required name and optional age
    And input with only age "25"
    When Alice validates the input
    Then the validation fails
    And the result contains an error for path ".name"
    And the validation error message contains "required"

  Scenario: Nested schema composition
    Given a schema with address object
    And the address schema has street and city as non_empty_string
    And input with address street "123 Main St" and city "Boston"
    When Alice validates the input
    Then the validation succeeds
    And the result contains address street "123 Main St"
    And the result contains address city "Boston"

  Scenario: Array field validation with errors
    Given a schema with tags as parse_list with parse_int elements
    And input with tags "1,2,invalid,3"
    When Alice validates the input
    Then the validation fails
    And the result contains an error for path ".tags"

  Scenario: Multiple validation errors across nested fields
    Given a schema with user name and addresses list
    And the address schema has street and zipcode
    And input with user name "" and two addresses with invalid data
    When Alice validates the input
    Then the validation fails
    And the result contains errors for multiple paths
    And the result contains an error for path ".user.name"
    And the result contains an error for path ".addresses.street"

  Scenario: Empty input with required fields
    Given a schema with required name and email
    And empty input
    When Alice validates the input
    Then the validation fails
    And the result contains an error for path ".name"
    And the result contains an error for path ".email"

  Scenario: Extra fields are allowed by default
    Given a schema with only name field
    And input with name "Alice" and extra field age "25"
    When Alice validates the input
    Then the validation succeeds
    And the result contains name "Alice"

  Scenario: Strict mode rejects extra fields
    Given a strict schema with only name field
    And input with name "Alice" and extra field age "25"
    When Alice validates the input
    Then the validation fails
    And the result contains an error mentioning "unexpected field"

  Scenario: Complex nested validation accumulates all errors
    Given a schema for user registration
    And the schema requires username, email, password, and address
    And input with invalid username, malformed email, weak password, and incomplete address
    When Alice validates the input
    Then the validation fails
    And the result contains at least four errors
    And each error has a clear field path

  Scenario: Successful validation returns typed result
    Given a schema with age as parse_int and active as parse_bool
    And input with age "25" and active "true"
    When Alice validates the input
    Then the validation succeeds
    And the result contains age as integer 25
    And the result contains active as boolean true

  Scenario: Error messages include helpful context
    Given a schema with age as parse_int with minimum 18
    And input with only age "15"
    When Alice validates the input
    Then the validation fails
    And the error includes the field path ".age"
    And the error includes the invalid value "15"
    And the error includes the constraint "minimum 18"
