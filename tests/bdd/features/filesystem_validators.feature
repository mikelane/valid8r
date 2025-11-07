Feature: Filesystem metadata validators
  As a developer building file-handling applications
  I want to validate file size and extensions
  So that I can enforce business rules and prevent issues

  Background:
    Given the validators max_size, min_size, has_extension are available
    And I have a temporary directory for test files

  # ===== File Size Validation: max_size() =====

  Scenario: Accept file under maximum size limit
    Given a temporary file of 1024 bytes
    When I validate with max_size(2048)
    Then I get Success with the Path

  Scenario: Accept file exactly at maximum size limit
    Given a temporary file of 2048 bytes
    When I validate with max_size(2048)
    Then I get Success with the Path

  Scenario: Reject file exceeding maximum size limit
    Given a temporary file of 5120 bytes
    When I validate with max_size(1024)
    Then I get Failure mentioning "exceeds maximum size"

  Scenario: Accept empty file under maximum size
    Given an empty temporary file
    When I validate with max_size(1024)
    Then I get Success with the Path

  Scenario: Reject very large file to prevent DoS
    Given a temporary file of 11534336 bytes
    When I validate with max_size(10485760)
    Then I get Failure mentioning "exceeds maximum size"

  Scenario: Error message includes actual size
    Given a temporary file of 5120 bytes
    When I validate with max_size(1024)
    Then I get Failure mentioning "5120"

  # ===== File Size Validation: min_size() =====

  Scenario: Accept file above minimum size limit
    Given a temporary file of 2048 bytes
    When I validate with min_size(1024)
    Then I get Success with the Path

  Scenario: Accept file exactly at minimum size limit
    Given a temporary file of 1024 bytes
    When I validate with min_size(1024)
    Then I get Success with the Path

  Scenario: Reject file below minimum size limit
    Given a temporary file of 512 bytes
    When I validate with min_size(1024)
    Then I get Failure mentioning "smaller than minimum size"

  Scenario: Reject empty file below minimum size
    Given an empty temporary file
    When I validate with min_size(1)
    Then I get Failure mentioning "smaller than minimum size"

  Scenario: Error message includes minimum size
    Given a temporary file of 512 bytes
    When I validate with min_size(1024)
    Then I get Failure mentioning "1024"

  # ===== File Extension Validation: has_extension() =====

  Scenario: Accept file with single allowed extension
    Given a file named "document.pdf"
    When I validate with has_extension('.pdf')
    Then I get Success with the Path

  Scenario: Accept file with one of multiple allowed extensions
    Given a file named "document.docx"
    When I validate with has_extension('.pdf', '.doc', '.docx')
    Then I get Success with the Path

  Scenario: Reject file with wrong extension
    Given a file named "image.png"
    When I validate with has_extension('.pdf', '.docx')
    Then I get Failure mentioning "allowed extensions"

  Scenario: Reject file with no extension
    Given a file named "README"
    When I validate with has_extension('.md', '.txt')
    Then I get Failure mentioning "allowed extensions"

  Scenario: Accept file with uppercase extension (case-insensitive)
    Given a file named "DOCUMENT.PDF"
    When I validate with has_extension('.pdf')
    Then I get Success with the Path

  Scenario: Accept file with mixed-case extension
    Given a file named "Report.Pdf"
    When I validate with has_extension('.pdf')
    Then I get Success with the Path

  Scenario: Accept file with multiple dots in name
    Given a file named "my.backup.file.tar.gz"
    When I validate with has_extension('.gz')
    Then I get Success with the Path

  Scenario: Reject file with multiple dots but wrong extension
    Given a file named "my.backup.file.tar.gz"
    When I validate with has_extension('.zip', '.7z')
    Then I get Failure mentioning "allowed extensions"

  Scenario: Error message lists all allowed extensions
    Given a file named "image.png"
    When I validate with has_extension('.pdf', '.docx', '.txt')
    Then I get Failure mentioning ".pdf"
    And the failure message mentions ".docx"
    And the failure message mentions ".txt"

  # ===== Combined Size and Extension Validation =====

  Scenario: Accept file meeting both size and extension requirements
    Given a temporary file named "document.pdf" of 5242880 bytes
    When I validate with max_size(10485760) and has_extension('.pdf')
    Then I get Success with the Path

  Scenario: Reject file with correct extension but exceeding size
    Given a temporary file named "large.pdf" of 15728640 bytes
    When I validate with max_size(10485760) and has_extension('.pdf')
    Then I get Failure mentioning "exceeds maximum size"

  Scenario: Reject file with correct size but wrong extension
    Given a temporary file named "document.png" of 5242880 bytes
    When I validate with max_size(10485760) and has_extension('.pdf')
    Then I get Failure mentioning "allowed extensions"

  Scenario: Validate file in size range with allowed extensions
    Given a temporary file named "data.csv" of 2048 bytes
    When I validate with min_size(1024) and max_size(10485760) and has_extension('.csv', '.xlsx')
    Then I get Success with the Path

  # ===== Full Upload Validation Pipeline =====

  Scenario: Accept valid upload meeting all criteria
    Given a temporary file named "upload.pdf" of 5242880 bytes that exists
    When I validate with parse_path and is_file and max_size(10485760) and has_extension('.pdf')
    Then I get Success with the Path

  Scenario: Reject non-existent file in upload pipeline
    Given a non-existent file path "missing.pdf"
    When I validate with parse_path and exists and max_size(10485760) and has_extension('.pdf')
    Then I get Failure mentioning "does not exist"

  Scenario: Reject directory instead of file in upload pipeline
    Given a temporary directory named "uploads"
    When I validate with parse_path and is_file and max_size(10485760)
    Then I get Failure mentioning "not a file"

  # ===== Edge Cases =====

  Scenario: Handle dot files with extensions
    Given a file named ".gitignore"
    When I validate with has_extension('')
    Then I get Failure mentioning "allowed extensions"

  Scenario: Accept dot file with proper extension
    Given a file named ".config.json"
    When I validate with has_extension('.json')
    Then I get Success with the Path

  Scenario: Handle symbolic links to files
    Given a symbolic link to a file of 1024 bytes
    When I validate with max_size(2048)
    Then I get Success with the Path

  Scenario: Reject file path that is actually a directory
    Given a temporary directory
    When I validate with max_size(1024)
    Then I get Failure mentioning "not a file"

  Scenario: Validate zero-byte file with correct extension
    Given an empty temporary file named "empty.txt"
    When I validate with max_size(1024) and has_extension('.txt')
    Then I get Success with the Path

  # ===== Real-World Use Cases =====

  Scenario: File upload API with 10MB PDF limit
    Given a temporary file named "invoice.pdf" of 5242880 bytes
    When I validate as an upload with 10MB limit and PDF extension
    Then I get Success with the Path

  Scenario: Image upload with size and format restrictions
    Given a temporary file named "profile.jpg" of 2097152 bytes
    When I validate with max_size(5242880) and has_extension('.jpg', '.jpeg', '.png', '.webp')
    Then I get Success with the Path

  Scenario: CSV data file must be non-empty and correct format
    Given a temporary file named "data.csv" of 2048 bytes
    When I validate with min_size(1) and has_extension('.csv')
    Then I get Success with the Path

  Scenario: Reject oversized document upload
    Given a temporary file named "presentation.pptx" of 52428800 bytes
    When I validate as an upload with 10MB limit and office extensions
    Then I get Failure mentioning "exceeds maximum size"
