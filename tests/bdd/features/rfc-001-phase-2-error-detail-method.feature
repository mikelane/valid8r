Feature: Enhanced Failure Type with error_detail() Method
  As a Valid8r library user
  I want to access structured error information via error_detail() method
  So that I can programmatically handle validation errors with codes, paths, and context

  Background:
    Given the Valid8r library is imported
    And ValidationError is available from valid8r.core.errors

  Scenario: Access structured error via error_detail() with string error
    Given I create a Failure with a string error "Invalid input"
    When I call error_detail() on the Failure
    Then I receive a ValidationError instance
    And the ValidationError code is "VALIDATION_ERROR"
    And the ValidationError message is "Invalid input"
    And the ValidationError path is ""
    And the ValidationError context is None

  Scenario: Access structured error via error_detail() with ValidationError
    Given I create a ValidationError with:
      | field   | value                |
      | code    | INVALID_EMAIL        |
      | message | Email format invalid |
      | path    | .user.email          |
    And I create a Failure with that ValidationError
    When I call error_detail() on the Failure
    Then I receive a ValidationError instance
    And the ValidationError code is "INVALID_EMAIL"
    And the ValidationError message is "Email format invalid"
    And the ValidationError path is ".user.email"

  Scenario: error_detail() and validation_error property return same object
    Given I create a ValidationError with code "OUT_OF_RANGE"
    And I create a Failure with that ValidationError
    When I call error_detail() on the Failure
    And I access the validation_error property
    Then both references point to the same ValidationError instance

  Scenario: Backward compatibility - error_or() still returns string
    Given I create a Failure with a string error "Something went wrong"
    When I call error_or("default") on the Failure
    Then I receive the string "Something went wrong"
    And I can still call error_detail() to get structured information

  Scenario: Error detail provides context for debugging
    Given I create a ValidationError with:
      | field   | value                      |
      | code    | OUT_OF_RANGE               |
      | message | Value must be 0-100        |
      | path    | .temperature               |
      | context | {"min": 0, "max": 100}     |
    And I create a Failure with that ValidationError
    When I call error_detail() on the Failure
    Then I can access the context dictionary
    And the context contains "min" with value 0
    And the context contains "max" with value 100

  Scenario: Pattern matching still works with error_detail() method
    Given I create a Failure with a string error "Parse error"
    When I pattern match on the Failure
    Then the matched error message is "Parse error"
    And I can call error_detail() to get the full ValidationError

  Scenario: Multiple Failures preserve distinct ValidationErrors via error_detail()
    Given I create a Failure with code "ERROR_ONE" and message "First error"
    And I create a Failure with code "ERROR_TWO" and message "Second error"
    When I call error_detail() on each Failure
    Then the first error_detail() has code "ERROR_ONE"
    And the second error_detail() has code "ERROR_TWO"
    And both are distinct ValidationError instances

  Scenario: error_detail() works in monadic bind chain
    Given I create a Failure with code "INITIAL_ERROR"
    When I bind the Failure to a transformation function
    Then the result is still a Failure
    And calling error_detail() returns the original ValidationError
    And the error code is still "INITIAL_ERROR"

  Scenario: error_detail() works in monadic map chain
    Given I create a Failure with code "MAP_ERROR"
    When I map the Failure with a transformation function
    Then the result is still a Failure
    And calling error_detail() returns the original ValidationError
    And the error code is still "MAP_ERROR"
