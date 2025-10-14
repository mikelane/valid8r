Feature: Phone Number Parsing
  As a developer
  I want to parse phone numbers into structured components
  So that I can validate contact information and format for different systems

  Background:
    Given the valid8r library is available

  # Happy Path - Basic Parsing

  Scenario: Parse standard formatted US phone number
    Given a phone number string "(415) 555-2671"
    When the parser parses the phone number
    Then the result is a Success
    And the area code is "415"
    And the exchange is "555"
    And the subscriber number is "2671"
    And the country code is "1"
    And the region is "US"

  Scenario: Parse phone number with dashes
    Given a phone number string "415-555-2671"
    When the parser parses the phone number
    Then the result is a Success
    And the area code is "415"
    And the exchange is "555"
    And the subscriber number is "2671"

  Scenario: Parse phone number with country code
    Given a phone number string "+1 415 555 2671"
    When the parser parses the phone number
    Then the result is a Success
    And the country code is "1"
    And the area code is "415"

  Scenario: Parse plain 10-digit number
    Given a phone number string "4155552671"
    When the parser parses the phone number
    Then the result is a Success
    And the area code is "415"
    And the exchange is "555"
    And the subscriber number is "2671"

  # Format Variations - Lenient Parsing

  Scenario: Parse phone with dot separators
    Given a phone number string "415.555.2671"
    When the parser parses the phone number
    Then the result is a Success
    And the area code is "415"
    And the exchange is "555"

  Scenario: Parse phone with spaces only
    Given a phone number string "415 555 2671"
    When the parser parses the phone number
    Then the result is a Success
    And the area code is "415"

  Scenario: Parse phone with mixed formatting
    Given a phone number string "1(415)555-2671"
    When the parser parses the phone number
    Then the result is a Success
    And the country code is "1"
    And the area code is "415"

  Scenario: Parse Canadian phone number with region hint
    Given a phone number string "+1 604 555 1234"
    And the region hint is "CA"
    When the parser parses the phone number with region
    Then the result is a Success
    And the region is "CA"
    And the country code is "1"
    And the area code is "604"

  # Extension Handling

  Scenario: Parse phone with extension using x
    Given a phone number string "415-555-2671 x123"
    When the parser parses the phone number
    Then the result is a Success
    And the extension is "123"
    And the area code is "415"

  Scenario: Parse phone with extension using ext
    Given a phone number string "415-555-2671 ext. 456"
    When the parser parses the phone number
    Then the result is a Success
    And the extension is "456"

  Scenario: Parse phone with extension using word extension
    Given a phone number string "(415) 555-2671 extension 789"
    When the parser parses the phone number
    Then the result is a Success
    And the extension is "789"

  Scenario: Parse phone without extension
    Given a phone number string "415-555-2671"
    When the parser parses the phone number
    Then the result is a Success
    And the extension is None

  # Format Conversions

  Scenario: Successfully parsed phone provides E.164 format
    Given a phone number string "415-555-2671"
    When the parser parses the phone number
    Then the result is a Success
    And the E.164 format is "+14155552671"

  Scenario: Successfully parsed phone provides national format
    Given a phone number string "4155552671"
    When the parser parses the phone number
    Then the result is a Success
    And the national format is "(415) 555-2671"

  Scenario: Successfully parsed phone provides international format
    Given a phone number string "(415) 555-2671"
    When the parser parses the phone number
    Then the result is a Success
    And the international format is "+1 415-555-2671"

  Scenario: E.164 format includes extension
    Given a phone number string "415-555-2671 x123"
    When the parser parses the phone number
    Then the result is a Success
    And the E.164 format is "+14155552671 x123"

  Scenario: National format includes extension
    Given a phone number string "415-555-2671 ext. 123"
    When the parser parses the phone number
    Then the result is a Success
    And the national format is "(415) 555-2671 ext. 123"

  # Error Cases - Invalid Inputs

  Scenario: Reject phone with too few digits
    Given a phone number string "555-2671"
    When the parser parses the phone number
    Then the result is a Failure
    And the error message contains "must have 10 digits"

  Scenario: Reject phone with too many digits
    Given a phone number string "1234567890123"
    When the parser parses the phone number
    Then the result is a Failure
    And the error message contains "must have 10 digits"

  Scenario: Reject phone with invalid area code starting with 0
    Given a phone number string "055-555-2671"
    When the parser parses the phone number
    Then the result is a Failure
    And the error message contains "invalid area code"

  Scenario: Reject phone with invalid area code starting with 1
    Given a phone number string "155-555-2671"
    When the parser parses the phone number
    Then the result is a Failure
    And the error message contains "invalid area code"

  Scenario: Reject phone with reserved area code 555
    Given a phone number string "555-123-4567"
    When the parser parses the phone number
    Then the result is a Failure
    And the error message contains "reserved"

  Scenario: Reject phone with invalid exchange 555 in specific pattern
    Given a phone number string "415-555-0100"
    When the parser parses the phone number
    Then the result is a Failure
    And the error message contains "reserved"

  Scenario: Reject phone with emergency exchange 911
    Given a phone number string "415-911-2671"
    When the parser parses the phone number
    Then the result is a Failure
    And the error message contains "invalid exchange"

  Scenario: Reject non-North American country code
    Given a phone number string "+44 20 7946 0958"
    When the parser parses the phone number
    Then the result is a Failure
    And the error message contains "only North American"

  Scenario: Reject phone with alphabetic characters
    Given a phone number string "1-800-FLOWERS"
    When the parser parses the phone number
    Then the result is a Failure
    And the error message contains "invalid format"

  Scenario: Reject empty phone number
    Given a phone number string ""
    When the parser parses the phone number
    Then the result is a Failure
    And the error message contains "cannot be empty"

  # Strict Mode Behavior

  Scenario: Strict mode rejects unformatted number
    Given a phone number string "4155552671"
    And strict mode is enabled
    When the parser parses the phone number in strict mode
    Then the result is a Failure
    And the error message contains "strict mode requires formatting"

  Scenario: Strict mode accepts properly formatted number with parens
    Given a phone number string "(415) 555-2671"
    And strict mode is enabled
    When the parser parses the phone number in strict mode
    Then the result is a Success
    And the area code is "415"

  Scenario: Strict mode accepts properly formatted number with dashes
    Given a phone number string "415-555-2671"
    And strict mode is enabled
    When the parser parses the phone number in strict mode
    Then the result is a Success
    And the area code is "415"

  # Edge Cases

  Scenario: Parse phone with extra whitespace
    Given a phone number string "  (415) 555-2671  "
    When the parser parses the phone number
    Then the result is a Success
    And the area code is "415"
    And the exchange is "555"

  Scenario: Parse phone with multiple spaces between components
    Given a phone number string "415    555    2671"
    When the parser parses the phone number
    Then the result is a Success
    And the area code is "415"

  Scenario: Parse phone with long extension
    Given a phone number string "415-555-2671 x123456"
    When the parser parses the phone number
    Then the result is a Success
    And the extension is "123456"

  Scenario: Distinguish valid from nearly valid format
    Given a phone number string "415-555-267"
    When the parser parses the phone number
    Then the result is a Failure
    And the error message contains "must have 10 digits"

  # Raw digits property

  Scenario: Successfully parsed phone provides raw digits
    Given a phone number string "(415) 555-2671"
    When the parser parses the phone number
    Then the result is a Success
    And the raw digits are "14155552671"

  Scenario: Raw digits include country code but not extension
    Given a phone number string "415-555-2671 x123"
    When the parser parses the phone number
    Then the result is a Success
    And the raw digits are "14155552671"
