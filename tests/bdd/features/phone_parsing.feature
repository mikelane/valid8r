Feature: Phone Number Parsing
  As a developer
  I want to parse phone numbers into structured components
  So that I can validate contact information and format for different systems

  Background:
    Given the valid8r library is available
    And the phone parsing module supports North American numbers

  # Happy Path - Basic Parsing

  Scenario: Parse standard formatted US phone number
    Given a phone number string "(415) 555-2671"
    When the parser parses the phone number
    Then the result is a success
    And the area code is "415"
    And the exchange is "555"
    And the subscriber number is "2671"
    And the country code is "1"
    And the region is "US"

  Scenario: Parse phone number with dashes
    Given a phone number string "415-555-2671"
    When the parser parses the phone number
    Then the result is a success
    And the area code is "415"
    And the exchange is "555"
    And the subscriber number is "2671"

  Scenario: Parse phone number with country code
    Given a phone number string "+1 415 555 2671"
    When the parser parses the phone number
    Then the result is a success
    And the country code is "1"
    And the area code is "415"

  Scenario: Parse plain 10-digit number
    Given a phone number string "4155552671"
    When the parser parses the phone number
    Then the result is a success
    And the area code is "415"
    And the exchange is "555"
    And the subscriber number is "2671"

  # Format Variations - Lenient Parsing

  Scenario: Parse phone with dot separators
    Given a phone number string "415.555.2671"
    When the parser parses the phone number
    Then the result is a success
    And the area code is "415"

  Scenario: Parse phone with spaces only
    Given a phone number string "415 555 2671"
    When the parser parses the phone number
    Then the result is a success
    And the area code is "415"

  Scenario: Parse phone with mixed formatting
    Given a phone number string "1(415)555-2671"
    When the parser parses the phone number
    Then the result is a success
    And the country code is "1"

  Scenario: Parse Canadian phone number with region hint
    Given a phone number string "+1 604 555 1234"
    And the region hint is "CA"
    When the parser parses the phone number with region hint
    Then the result is a success
    And the region is "CA"
    And the country code is "1"

  # Extension Handling

  Scenario: Parse phone with extension using x
    Given a phone number string "415-555-2671 x123"
    When the parser parses the phone number
    Then the result is a success
    And the extension is "123"
    And the area code is "415"

  Scenario: Parse phone with extension using ext
    Given a phone number string "415-555-2671 ext. 456"
    When the parser parses the phone number
    Then the result is a success
    And the extension is "456"

  Scenario: Parse phone with extension using word extension
    Given a phone number string "(415) 555-2671 extension 789"
    When the parser parses the phone number
    Then the result is a success
    And the extension is "789"

  Scenario: Parse phone without extension has None extension
    Given a phone number string "415-555-2671"
    When the parser parses the phone number
    Then the result is a success
    And the extension is None

  # Format Conversions - E.164

  Scenario: Parsed phone provides E.164 format
    Given a successfully parsed phone "415-555-2671"
    When the E.164 format is requested
    Then the E.164 format is "+14155552671"

  Scenario: E.164 format includes extension
    Given a successfully parsed phone "415-555-2671 x123"
    When the E.164 format is requested
    Then the E.164 format is "+14155552671 x123"

  # Format Conversions - National

  Scenario: Parsed phone provides national format
    Given a successfully parsed phone "4155552671"
    When the national format is requested
    Then the national format is "(415) 555-2671"

  Scenario: National format includes extension
    Given a successfully parsed phone "415-555-2671 extension 123"
    When the national format is requested
    Then the national format is "(415) 555-2671 ext. 123"

  # Format Conversions - International

  Scenario: Parsed phone provides international format
    Given a successfully parsed phone "(415) 555-2671"
    When the international format is requested
    Then the international format is "+1 415-555-2671"

  Scenario: International format includes extension
    Given a successfully parsed phone "+1 415 555 2671 x456"
    When the international format is requested
    Then the international format is "+1 415-555-2671 ext. 456"

  # Error Cases - Invalid Inputs

  Scenario: Reject phone with too few digits
    Given a phone number string "555-2671"
    When the parser parses the phone number
    Then the result is a failure
    And the error message contains "must have 10 digits"

  Scenario: Reject phone with too many digits
    Given a phone number string "1234567890123"
    When the parser parses the phone number
    Then the result is a failure
    And the error message contains "must have 10 digits"

  Scenario: Reject phone with invalid area code starting with 0
    Given a phone number string "055-555-2671"
    When the parser parses the phone number
    Then the result is a failure
    And the error message contains "invalid area code"

  Scenario: Reject phone with invalid area code starting with 1
    Given a phone number string "155-555-2671"
    When the parser parses the phone number
    Then the result is a failure
    And the error message contains "invalid area code"

  Scenario: Reject phone with reserved area code 555
    Given a phone number string "555-123-4567"
    When the parser parses the phone number
    Then the result is a failure
    And the error message contains "reserved"

  Scenario: Reject phone with invalid exchange 555
    Given a phone number string "415-555-5555"
    When the parser parses the phone number
    Then the result is a failure
    And the error message contains "invalid exchange"

  Scenario: Reject phone with emergency exchange 911
    Given a phone number string "415-911-2671"
    When the parser parses the phone number
    Then the result is a failure
    And the error message contains "invalid exchange"

  Scenario: Reject non-North American country code
    Given a phone number string "+44 20 7946 0958"
    When the parser parses the phone number
    Then the result is a failure
    And the error message contains "only North American"

  Scenario: Reject phone with alphabetic characters
    Given a phone number string "1-800-FLOWERS"
    When the parser parses the phone number
    Then the result is a failure
    And the error message contains "invalid format"

  Scenario: Reject empty phone number
    Given an empty phone number string
    When the parser parses the phone number
    Then the result is a failure
    And the error message contains "cannot be empty"

  # Strict Mode Behavior

  Scenario: Strict mode rejects unformatted number
    Given a phone number string "4155552671"
    And strict mode is enabled
    When the parser parses the phone number in strict mode
    Then the result is a failure
    And the error message contains "strict mode requires formatting"

  Scenario: Strict mode accepts properly formatted number
    Given a phone number string "(415) 555-2671"
    And strict mode is enabled
    When the parser parses the phone number in strict mode
    Then the result is a success

  Scenario: Lenient mode accepts unformatted number
    Given a phone number string "4155552671"
    When the parser parses the phone number
    Then the result is a success

  # Edge Cases - Whitespace

  Scenario: Parse phone with leading and trailing whitespace
    Given a phone number string "  (415) 555-2671  "
    When the parser parses the phone number
    Then the result is a success
    And the area code is "415"

  Scenario: Parse phone with multiple spaces between parts
    Given a phone number string "415    555    2671"
    When the parser parses the phone number
    Then the result is a success
    And the area code is "415"

  Scenario: Parse phone with tabs and newlines
    Given a phone number string "415\t555\n2671"
    When the parser parses the phone number
    Then the result is a success
    And the area code is "415"

  # Edge Cases - Extensions

  Scenario: Parse phone with very long extension
    Given a phone number string "415-555-2671 x123456"
    When the parser parses the phone number
    Then the result is a success
    And the extension is "123456"

  Scenario: Parse phone with single digit extension
    Given a phone number string "415-555-2671 x5"
    When the parser parses the phone number
    Then the result is a success
    And the extension is "5"

  Scenario: Reject phone with non-numeric extension
    Given a phone number string "415-555-2671 xABC"
    When the parser parses the phone number
    Then the result is a failure
    And the error message contains "invalid"

  # Security - Injection Attacks

  Scenario: Reject phone with SQL injection pattern
    Given a phone number string "415-555-2671'; DROP TABLE users--"
    When the parser parses the phone number
    Then the result is a failure
    And the error message contains "invalid format"

  Scenario: Reject phone with script tag
    Given a phone number string "<script>alert('xss')</script>"
    When the parser parses the phone number
    Then the result is a failure
    And the error message contains "invalid format"

  Scenario: Reject phone with null byte
    Given a phone number string "415-555-2671\x00"
    When the parser parses the phone number
    Then the result is a failure
    And the error message contains "invalid"

  Scenario: Reject phone with command injection pattern
    Given a phone number string "415-555-2671; rm -rf /"
    When the parser parses the phone number
    Then the result is a failure
    And the error message contains "invalid"

  # Security - Unicode and Special Characters

  Scenario: Reject phone with emoji
    Given a phone number string "415-555-2671📱"
    When the parser parses the phone number
    Then the result is a failure
    And the error message contains "invalid format"

  Scenario: Reject phone with zero-width space
    Given a phone number string "415​555​2671"
    When the parser parses the phone number
    Then the result is a failure
    And the error message contains "invalid"

  Scenario: Reject phone with unicode lookalike digits
    Given a phone number string "４１５-５５５-２６７１"
    When the parser parses the phone number
    Then the result is a failure
    And the error message contains "invalid"

  Scenario: Reject phone with mixed ascii and unicode
    Given a phone number string "415-５５５-2671"
    When the parser parses the phone number
    Then the result is a failure
    And the error message contains "invalid"

  # Edge Cases - Boundary Testing

  Scenario: Parse phone with exactly 10 digits
    Given a phone number string "2025551234"
    When the parser parses the phone number
    Then the result is a success
    And the area code is "202"

  Scenario: Reject phone with 9 digits
    Given a phone number string "202555123"
    When the parser parses the phone number
    Then the result is a failure
    And the error message contains "10 digits"

  Scenario: Accept 11 digits starting with 1 as valid NANP
    Given a phone number string "12025551234"
    When the parser parses the phone number
    Then the result is a success
    And the country code is "1"
    And the area code is "202"

  Scenario: Accept 11 digits with explicit +1 country code
    Given a phone number string "+12025551234"
    When the parser parses the phone number
    Then the result is a success
    And the country code is "1"

  # Edge Cases - Format Confusion

  Scenario: Distinguish valid from similar invalid format
    Given a phone number string "415-555-2671"
    When the parser parses the phone number
    Then the result is a success
    And the area code is "415"

  Scenario: Distinguish valid from similar invalid format with wrong digit count
    Given a phone number string "415-555-267"
    When the parser parses the phone number
    Then the result is a failure
    And the error message contains "10 digits"

  # Edge Cases - Toll-Free Numbers

  Scenario: Parse toll-free 800 number
    Given a phone number string "1-800-555-1234"
    When the parser parses the phone number
    Then the result is a success
    And the area code is "800"

  Scenario: Parse toll-free 888 number
    Given a phone number string "888-555-1234"
    When the parser parses the phone number
    Then the result is a success
    And the area code is "888"

  # Edge Cases - Special Separators

  Scenario: Parse phone with no separators
    Given a phone number string "4155552671"
    When the parser parses the phone number
    Then the result is a success
    And the area code is "415"

  Scenario: Parse phone with mixed separators
    Given a phone number string "415.555-2671"
    When the parser parses the phone number
    Then the result is a success
    And the area code is "415"

  Scenario: Reject phone with invalid separators
    Given a phone number string "415:555:2671"
    When the parser parses the phone number
    Then the result is a failure
    And the error message contains "invalid format"

  # Edge Cases - None and Type Confusion

  Scenario: Reject None as phone number
    Given a None phone number value
    When the parser parses the phone number
    Then the result is a failure
    And the error message contains "cannot be empty"

  Scenario: Parse phone number from string with only whitespace
    Given a phone number string "   "
    When the parser parses the phone number
    Then the result is a failure
    And the error message contains "cannot be empty"

  # Edge Cases - Extension Edge Cases

  Scenario: Reject phone with extension that is too long
    Given a phone number string "415-555-2671 x1234567890"
    When the parser parses the phone number
    Then the result is a failure
    And the error message contains "extension"

  Scenario: Parse phone with extension preceded by comma
    Given a phone number string "415-555-2671,123"
    When the parser parses the phone number
    Then the result is a success
    And the extension is "123"

  # Edge Cases - Extremely Long Input

  Scenario: Reject extremely long phone string
    Given an extremely long phone number string
    When the parser parses the phone number
    Then the result is a failure
    And the error message contains "too long"

  # Raw Digits Property

  Scenario: Parsed phone provides raw digits
    Given a successfully parsed phone "(415) 555-2671"
    When the raw digits are requested
    Then the raw digits are "14155552671"
