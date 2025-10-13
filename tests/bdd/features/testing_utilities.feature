Feature: Testing Utilities for Valid8r
  As a developer using Valid8r
  I want to have convenient testing utilities
  So that I can easily test my validation logic

  Background:
    Given the testing utilities module is available

  Scenario: Mock user input for prompt testing
    When I configure the mock input to return a single value "42"
    And I use the testing utility to test a prompt for an integer
    Then the prompt should return a successful Maybe with value 42

  Scenario: Simulate multiple user inputs
    When I configure the mock input to return a sequence "invalid" then "42"
    And I use the testing utility to test a prompt with retry
    Then the prompt should return a successful Maybe with value 42

  Scenario: Test failing validation
    When I configure the mock input to return a single value "-5"
    And I use the testing utility to test a prompt with minimum 0 validation
    Then the prompt should return a failure Maybe with error "Value must be at least 0"

  Scenario: Assert on Maybe results
    When I have a Maybe result from a validation
    And I use the assertion helper to verify it succeeded with value 42
    Then the assertion should pass

  Scenario: Generate test data for validators
    When I request test data for the minimum validator with value 0
    Then I should receive valid and invalid test cases
    And the valid cases should be greater than or equal to 0
    And the invalid cases should be less than 0

  Scenario: Helper for testing validator composition
    When I compose a validator using minimum 0 AND maximum 100
    And I use the testing utility to verify the composition
    Then it should verify behavior for multiple test cases

  Scenario: Input generator for property-based testing
    When I request random test inputs for a specific validator
    Then I should receive inputs that both pass and fail the validation

  Scenario: Test context manager for mocking input
    When I use the test context manager with input "42"
    And I call a function that prompts for input
    Then the function should receive "42" as input
