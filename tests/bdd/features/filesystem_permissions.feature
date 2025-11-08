Feature: Filesystem Permission Validators
  As a developer building file-handling applications
  I want to validate file permissions
  So that I can provide helpful error messages before attempting I/O operations

  Background:
    Given the filesystem permission validators are available
    And I have a temporary test directory

  Scenario: Validate a readable file
    Given a temporary file with read permissions
    And I have a Path object for that file
    When I validate the path with is_readable
    Then the validation result is a Success
    And the result contains the same Path

  Scenario: Reject a non-readable file
    Given a temporary file without read permissions
    And I have a Path object for that file
    When I validate the path with is_readable
    Then the validation result is a Failure
    And the error message contains "not readable"

  Scenario: Validate a writable file
    Given a temporary file with write permissions
    And I have a Path object for that file
    When I validate the path with is_writable
    Then the validation result is a Success
    And the result contains the same Path

  Scenario: Reject a non-writable file
    Given a temporary file without write permissions
    And I have a Path object for that file
    When I validate the path with is_writable
    Then the validation result is a Failure
    And the error message contains "not writable"

  Scenario: Validate an executable file
    Given a temporary file with execute permissions
    And I have a Path object for that file
    When I validate the path with is_executable
    Then the validation result is a Success
    And the result contains the same Path

  Scenario: Reject a non-executable file
    Given a temporary file without execute permissions
    And I have a Path object for that file
    When I validate the path with is_executable
    Then the validation result is a Failure
    And the error message contains "not executable"

  Scenario: Validate a readable directory
    Given a temporary directory with read permissions
    And I have a Path object for that directory
    When I validate the path with is_readable
    Then the validation result is a Success
    And the result contains the same Path

  Scenario: Validate a writable directory
    Given a temporary directory with write permissions
    And I have a Path object for that directory
    When I validate the path with is_writable
    Then the validation result is a Success
    And the result contains the same Path

  Scenario: Reject validation of non-existent path for readability
    Given a non-existent file path
    When I validate the path with is_readable
    Then the validation result is a Failure
    And the error message contains "not readable"

  Scenario: Reject validation of non-existent path for writability
    Given a non-existent file path
    When I validate the path with is_writable
    Then the validation result is a Failure
    And the error message contains "not writable"

  Scenario: Chain readable and writable validators
    Given a temporary file with read and write permissions
    And I have a Path object for that file
    And a combined validator with is_readable and is_writable
    When I validate the path with the combined validator
    Then the validation result is a Success
    And the result contains the same Path

  Scenario: Chain fails when file is readable but not writable
    Given a temporary file with read-only permissions
    And I have a Path object for that file
    And a combined validator with is_readable and is_writable
    When I validate the path with the combined validator
    Then the validation result is a Failure
    And the error message contains "not writable"

  Scenario: Validate readable symlink to readable file
    Given a temporary file with read permissions
    And a symbolic link pointing to that file
    And I have a Path object for the symlink
    When I validate the path with is_readable
    Then the validation result is a Success
    And the result contains the symlink Path

  Scenario: Reject symlink to non-readable file
    Given a temporary file without read permissions
    And a symbolic link pointing to that file
    And I have a Path object for the symlink
    When I validate the path with is_readable
    Then the validation result is a Failure
    And the error message contains "not readable"

  Scenario: Reject broken symlink
    Given a symbolic link pointing to a non-existent file
    And I have a Path object for the symlink
    When I validate the path with is_readable
    Then the validation result is a Failure
    And the error message contains "not readable"

  Scenario: Full validation pipeline with parse_path
    Given a readable file at a known path
    When I parse the path string with parse_path
    And bind the result with is_readable validator
    Then the final result is a Success
    And the result contains the parsed Path

  Scenario: Full pipeline fails on non-readable file
    Given a non-readable file at a known path
    When I parse the path string with parse_path
    And bind the result with is_readable validator
    Then the final result is a Failure
    And the error message contains "not readable"

  Scenario: Complex validation chain with exists, is_file, and is_readable
    Given a readable regular file at a known path
    When I parse the path string with parse_path
    And bind with exists validator
    And bind with is_file validator
    And bind with is_readable validator
    Then the final result is a Success
    And the result contains the parsed Path

  Scenario: Chain fails at is_file when path is a directory
    Given a readable directory at a known path
    When I parse the path string with parse_path
    And bind with exists validator
    And bind with is_file validator
    And bind with is_readable validator
    Then the final result is a Failure
    And the error message contains "not a file"

  Scenario: Chain fails at is_readable when file is not readable
    Given a non-readable regular file at a known path
    When I parse the path string with parse_path
    And bind with exists validator
    And bind with is_file validator
    And bind with is_readable validator
    Then the final result is a Failure
    And the error message contains "not readable"

  Scenario: Validate directory write permissions for output path
    Given a writable directory for output
    And I have a Path object for that directory
    When I parse the path string with parse_path
    And bind with exists validator
    And bind with is_dir validator
    And bind with is_writable validator
    Then the final result is a Success
    And the result contains the parsed Path

  Scenario: File with all permissions passes all validators
    Given a temporary file with read, write, and execute permissions
    And I have a Path object for that file
    And a combined validator with is_readable, is_writable, and is_executable
    When I validate the path with the combined validator
    Then the validation result is a Success
    And the result contains the same Path

  Scenario: File with read-only permissions fails writable check
    Given a temporary file with read-only permissions
    And I have a Path object for that file
    When I validate the path with is_writable
    Then the validation result is a Failure
    And the error message contains "not writable"

  Scenario: File with write-only permissions fails readable check
    Given a temporary file with write-only permissions
    And I have a Path object for that file
    When I validate the path with is_readable
    Then the validation result is a Failure
    And the error message contains "not readable"
