Feature: CLI Starter Template
  As a CLI developer
  I want a production-ready starter template
  So that I can build validated CLIs quickly

  Scenario: Template validates command arguments
    Given I clone the starter template
    When I run the CLI with invalid arguments
    Then I see clear error messages explaining what went wrong
    And the program exits cleanly
    And I understand how to fix the error

  Scenario: Template provides interactive prompts
    Given I clone the starter template
    When I run the CLI in interactive mode
    Then I am prompted for required information
    And invalid inputs are rejected with helpful feedback
    And I can successfully complete the workflow

  Scenario: Template validates configuration files
    Given I clone the starter template
    And I provide a configuration file
    When the CLI loads the configuration
    Then invalid configuration is rejected
    And I see which configuration values are wrong
    And I see the file location and line number

  Scenario: Template is easy to customize
    Given I clone the starter template
    When I want to add my own validation logic
    Then I can understand the code structure
    And I can find clear examples to follow
    And I can extend the template for my use case

  Scenario: Template demonstrates quality standards
    Given I clone the starter template
    Then the code is well-documented
    And the project structure is clear
    And I can run tests successfully
    And I can build the project without errors
