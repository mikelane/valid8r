Title: Add filesystem Path parsers and validators (exists, is_file, is_dir, max_size)
Labels: enhancement, parsers, validators

Implement `parse_path` returning `pathlib.Path`, and validators for `exists`, `is_file`, `is_dir`, and `max_size(bytes)` for files.

Acceptance Criteria:
```gherkin
Feature: Filesystem validation
  Scenario: Validate existing directory
    Given a temporary directory path
    When I parse it and validate with is_dir
    Then I get Success with that Path

  Scenario: Reject missing file
    Given a non-existent file path
    When I validate with exists & is_file
    Then I get Failure mentioning "exists"
```