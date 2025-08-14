Title: Add URL and Email parsers
Labels: enhancement, parsers

Implement `parse_url` (stdlib `urllib.parse`) and `parse_email` (RFC-5322-lite) with sensible validation.

Acceptance Criteria:
```gherkin
Feature: URL and Email parsing
  Scenario: Parse valid http URL
    Given "https://example.com/path?q=1"
    When I call parse_url
    Then I get Success with a structured URL object or result tuple

  Scenario: Reject malformed email
    Given "not-an-email"
    When I call parse_email
    Then I get Failure containing "email"
```