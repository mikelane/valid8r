Feature: Collection Type Parsing
  As a developer
  I want to parse string inputs into collection types like lists and dictionaries
  So that I can safely work with structured data in my applications

  Background:
    Given the input validation module is available

  Scenario: Successfully parse string to list of integers
    When I parse "1,2,3" to a list of integers
    Then the result should be a successful Maybe with list value [1, 2, 3]

  Scenario: Successfully parse string to list with custom separator
    When I parse "1|2|3" to a list of integers with separator "|"
    Then the result should be a successful Maybe with list value [1, 2, 3]

  Scenario: Parse string to list with invalid element
    When I parse "1,a,3" to a list of integers
    Then the result should be a failure Maybe with error containing "Failed to parse element"

  Scenario: Successfully parse string to dictionary
    When I parse "a:1,b:2,c:3" to a dictionary with string keys and integer values
    Then the result should be a successful Maybe with dictionary value {"a": 1, "b": 2, "c": 3}

  Scenario: Successfully parse string to dictionary with custom separators
    When I parse "a=1|b=2|c=3" to a dictionary with pair separator "|" and key-value separator "="
    Then the result should be a successful Maybe with dictionary value {"a": 1, "b": 2, "c": 3}

  Scenario: Parse string to dictionary with invalid key-value pair
    When I parse "a:1,b2,c:3" to a dictionary
    Then the result should be a failure Maybe with error containing "Invalid key-value pair"

  Scenario: Parse string to dictionary with invalid value
    When I parse "a:1,b:x,c:3" to a dictionary with integer values
    Then the result should be a failure Maybe with error containing "Failed to parse value"

  Scenario: Parse list with length validation
    When I parse "1,2,3" to a list with minimum length 5
    Then the result should be a failure Maybe with error containing "List must have at least 5 elements"

  Scenario: Parse dictionary with required keys
    When I parse "a:1,b:2" to a dictionary with required keys "a,b,c"
    Then the result should be a failure Maybe with error containing "Missing required keys"

  Scenario: Register custom parser
    Given I have registered a custom parser for IP addresses
    When I parse "192.168.1.1" using the registry with type "IPv4Address"
    Then the result should be a successful Maybe with IP value "192.168.1.1"

  Scenario: Parse using registered default parsers
    Given the parser registry has default parsers registered
    When I parse "123" using the registry with type "int"
    Then the result should be a successful Maybe with integer value 123