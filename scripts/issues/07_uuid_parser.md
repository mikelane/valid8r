Title: Add UUID parser with version and strictness options
Labels: enhancement, parsers

Implement `parse_uuid(text: str, version: int | None = None, strict: bool = True)` supporting v1-v5 and validating version when provided.

Acceptance Criteria:
```gherkin
Feature: UUID parsing
  Scenario: Parse valid v4 UUID
    Given a valid v4 UUID string
    When I call parse_uuid with version 4
    Then I get Success with a UUID object of version 4

  Scenario: Reject wrong version when strict
    Given a valid v1 UUID string
    When I call parse_uuid with version 4 and strict True
    Then I get Failure mentioning wrong version
```