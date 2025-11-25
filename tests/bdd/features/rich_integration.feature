Feature: Rich Integration Example
  As a CLI developer using Rich
  I want an example of valid8r + Rich integration
  So that I can build beautiful, validated CLIs

  Scenario: Example shows Rich console output
    Given I run the example application
    When validation succeeds
    Then I see success messages in Rich panels
    And I see validated data in Rich tables

  Scenario: Example shows Rich error handling
    Given I run the example application
    When Rich validation fails
    Then I see error messages styled with Rich
    And errors are highlighted with appropriate colors
    And errors include helpful suggestions

  Scenario: Example shows Rich progress bars
    Given I run the example with batch processing
    When multiple items are validated
    Then I see a Rich progress bar
    And progress updates reflect validation status

  Scenario: Example shows Rich prompts
    Given I run the example in interactive mode
    When I am prompted for input
    Then prompts use Rich styling
    And invalid input shows styled error messages

  Scenario: Example is visually impressive
    Given I run the example
    Then I see professional-quality terminal output
    And I want to share screenshots on social media
