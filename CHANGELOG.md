# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.0] - 2025-11-02

### Added

- **North American Phone Number Parsing (NANP)** - New `parse_phone()` function for parsing and validating US/Canada phone numbers
  - Supports multiple input formats: parentheses, dashes, dots, spaces, and plain digits
  - Handles country codes: `+1` and leading `1` prefixes
  - Parses extensions with multiple markers: `x`, `ext.`, `extension`, or comma-separated
  - Returns structured `PhoneNumber` dataclass with:
    - Decomposed components: `area_code`, `exchange`, `subscriber`, `country_code`, `region`, `extension`
    - Multiple output formats: `e164`, `national`, `international`, `raw_digits`
  - Comprehensive NANP validation rules:
    - Area code validation (rejects 0XX, 1XX, 555)
    - Exchange code validation (rejects 0XX, 1XX, 911, 555-5XXX fictional range)
    - Extension validation (numeric only, max 8 digits)
  - Optional `strict` mode to enforce formatting characters
  - Region parameter for US/CA distinction
  - Zero external dependencies (stdlib only)
  - Excellent performance: <1ms for valid numbers, <5ms for invalid
  - Comprehensive error messages for validation failures
  - Full type annotations with mypy strict mode compliance
  - 62 BDD scenarios + 36 unit tests with >95% coverage

## [0.7.6] - 2025-10-XX

### Changed

- Updated Python versions to latest patches
- Enhanced multi-version testing

## [0.7.5] - 2025-10-XX

### Added

- Codecov configuration for coverage reporting

## [0.7.4] - 2025-10-XX

### Fixed

- Renamed `.github/README.md` to prevent conflict with root README

[0.8.0]: https://github.com/mikelane/valid8r/compare/v0.7.6...v0.8.0
[0.7.6]: https://github.com/mikelane/valid8r/compare/v0.7.5...v0.7.6
[0.7.5]: https://github.com/mikelane/valid8r/compare/v0.7.4...v0.7.5
[0.7.4]: https://github.com/mikelane/valid8r/releases/tag/v0.7.4
