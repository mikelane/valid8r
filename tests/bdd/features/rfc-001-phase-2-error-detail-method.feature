Feature: Structured Error Information
  As a developer using Valid8r
  I want structured error information from validation failures
  So that I can provide detailed debugging information and user-friendly error messages

  Scenario: Access error details from simple validation failure
    Given I validate user input that fails with "Invalid email format"
    When I examine the validation error
    Then I can access the error code
    And I can access the error message "Invalid email format"
    And the error path is empty
    And no additional context is provided

  Scenario: Access detailed error information with context
    Given I validate a temperature value that is out of range
    When I examine the validation error
    Then the error code indicates "OUT_OF_RANGE"
    And the error message explains the constraint
    And the error path points to the temperature field
    And the context includes minimum and maximum values

  Scenario: Backward compatibility with string-based error handling
    Given I have existing code that uses string error messages
    When a validation fails
    Then I can still access the error as a string
    And I can optionally access structured error details

  Scenario: Error information persists through transformations
    Given a validation failure occurs
    When I chain additional transformations
    Then the original error information is preserved
    And I can still access the complete error details

  Scenario: Multiple validation failures have distinct error details
    Given I have two different validation failures
    When I examine each error
    Then each has its own error code
    And each has its own error message
    And the error objects are independent

  Scenario: Consistent error information from different access methods
    Given a validation failure has occurred
    When I access the error information
    Then the structured error details are consistent
    And the same information is available regardless of access method
