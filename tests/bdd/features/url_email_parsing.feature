Feature: URL and Email Parsing
  As a developer using valid8r
  I want to parse URLs and email addresses
  So that I can validate and extract structured information from web-related data

  Scenario: Parse basic HTTP URL
    Given I have the URL string "http://example.com/path"
    When I parse it with parse_url
    Then the result is a Success
    And the URL scheme is "http"
    And the URL host is "example.com"
    And the URL path is "/path"

  Scenario: Parse HTTPS URL with port and query
    Given I have the URL string "https://example.com:8080/api?key=value"
    When I parse it with parse_url
    Then the result is a Success
    And the URL scheme is "https"
    And the URL host is "example.com"
    And the URL port is 8080
    And the URL path is "/api"
    And the URL query is "key=value"

  Scenario: Parse URL with credentials
    Given I have the URL string "https://user:pass@example.com/secure"
    When I parse it with parse_url
    Then the result is a Success
    And the URL username is "user"
    And the URL password is "pass"
    And the URL host is "example.com"

  Scenario: Parse URL with IPv4 address
    Given I have the URL string "http://192.168.1.1:8080/api"
    When I parse it with parse_url
    Then the result is a Success
    And the URL host is "192.168.1.1"
    And the URL port is 8080

  Scenario: Parse URL with IPv6 address
    Given I have the URL string "http://[2001:db8::1]:8080/path"
    When I parse it with parse_url
    Then the result is a Success
    And the URL host is "2001:db8::1"
    And the URL port is 8080

  Scenario: Parse URL with fragment
    Given I have the URL string "https://example.com/page#section"
    When I parse it with parse_url
    Then the result is a Success
    And the URL path is "/page"
    And the URL fragment is "section"

  Scenario: Parse URL with empty path
    Given I have the URL string "https://example.com"
    When I parse it with parse_url
    Then the result is a Success
    And the URL path is ""

  Scenario: Reject empty URL
    Given I have the URL string ""
    When I parse it with parse_url
    Then the result is a Failure
    And the error message contains "empty"

  Scenario: Reject URL with unsupported scheme
    Given I have the URL string "ftp://example.com/file"
    When I parse it with parse_url
    Then the result is a Failure
    And the error message contains "unsupported"

  Scenario: Reject URL without scheme
    Given I have the URL string "example.com/path"
    When I parse it with parse_url
    Then the result is a Failure

  Scenario: Parse simple email address
    Given I have the email string "user@example.com"
    When I parse it with parse_email
    Then the result is a Success
    And the email local part is "user"
    And the email domain is "example.com"

  Scenario: Parse email with subdomain
    Given I have the email string "admin@mail.example.com"
    When I parse it with parse_email
    Then the result is a Success
    And the email local part is "admin"
    And the email domain is "mail.example.com"

  Scenario: Parse email with plus addressing
    Given I have the email string "user+tag@example.com"
    When I parse it with parse_email
    Then the result is a Success
    And the email local part is "user+tag"
    And the email domain is "example.com"

  Scenario: Email domain is normalized to lowercase
    Given I have the email string "User@EXAMPLE.COM"
    When I parse it with parse_email
    Then the result is a Success
    And the email domain is "example.com"

  Scenario: Reject empty email
    Given I have the email string ""
    When I parse it with parse_email
    Then the result is a Failure
    And the error message contains "empty"

  Scenario: Reject email without at sign
    Given I have the email string "userexample.com"
    When I parse it with parse_email
    Then the result is a Failure

  Scenario: Reject email without domain
    Given I have the email string "user@"
    When I parse it with parse_email
    Then the result is a Failure

  Scenario: Reject email with invalid domain
    Given I have the email string "user@invalid..domain"
    When I parse it with parse_email
    Then the result is a Failure

  Scenario: Parse email with numeric domain
    Given I have the email string "user@123.456.789.012"
    When I parse it with parse_email
    Then the result is a Failure
    And the error message contains "domain"
