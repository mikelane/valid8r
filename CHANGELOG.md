# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive documentation for structured result types (PhoneNumber, UrlParts, EmailAddress)
- Expanded testing utilities documentation with examples
- Complete parser reference in README
- Docstring examples for parse_url and parse_email functions

### Changed
- Updated README with phone number parsing examples
- Enhanced docs/index.rst with structured results and testing sections

## [0.2.7] - 2025-10-22

### Fixed
- Consolidated Read the Docs build steps to fix documentation deployment

## [0.2.6] - 2025-10-22

### Fixed
- Added actions:write permission to enable PyPI workflow dispatch

## [0.2.5] - 2025-10-22

### Fixed
- Configured workflow to trigger PyPI publish after release creation

## [0.2.4] - 2025-10-22

### Fixed
- Updated Read the Docs to use Poetry for Sphinx build

## [0.2.3] - 2025-10-22

### Fixed
- Read version from pyproject.toml in documentation configuration

## [0.2.2] - 2025-10-22

### Fixed
- Corrected Poetry installation order in Read the Docs configuration

## [0.2.1] - 2025-10-22

### Added
- Read the Docs configuration for documentation hosting

## [0.2.0] - 2025-10-21

### Added
- Phone number parsing with `parse_phone` function
  - North American Numbering Plan (NANP) validation
  - PhoneNumber dataclass with structured components (area_code, exchange, subscriber)
  - Support for various phone number formats
  - E.164 and national format properties
  - Extension support
- URL parsing with `parse_url` function
  - UrlParts dataclass with structured components
  - Support for scheme, host, port, path, query, fragment
  - Username and password extraction
  - IPv4 and IPv6 host support
- Email parsing with `parse_email` function
  - EmailAddress dataclass with local and domain parts
  - RFC 5322 compliant validation using email-validator library
  - Domain normalization to lowercase
  - IDNA (internationalized domain names) support
- UUID parsing with `parse_uuid` function
  - Optional version validation (UUID v1-v5)
  - Support for both hyphenated and non-hyphenated formats
- IP address and CIDR network parsing
  - `parse_ipv4`, `parse_ipv6`, `parse_ip` functions
  - `parse_cidr` with strict/non-strict modes
- Comprehensive testing utilities
  - `assert_maybe_success` for testing Success results
  - `assert_maybe_failure` for testing Failure results
  - `MockInputContext` for testing interactive prompts
- py.typed marker for type checker support

### Changed
- Enhanced Maybe monad with comprehensive monadic operations
- Improved error messages across all parsers
- Updated public API exports

### Documentation
- Added comprehensive README with examples
- Sphinx documentation with autoapi integration
- BDD feature files for behavioral specifications

## [0.1.0] - Initial Release

### Added
- Basic type parsers (int, float, bool, date)
- Collection parsers (list, dict, set)
- Validator combinators
- Interactive input prompting
- Maybe monad for error handling
- Pattern matching support

---

[Unreleased]: https://github.com/mikelane/valid8r/compare/v0.2.7...HEAD
[0.2.7]: https://github.com/mikelane/valid8r/compare/v0.2.6...v0.2.7
[0.2.6]: https://github.com/mikelane/valid8r/compare/v0.2.5...v0.2.6
[0.2.5]: https://github.com/mikelane/valid8r/compare/v0.2.4...v0.2.5
[0.2.4]: https://github.com/mikelane/valid8r/compare/v0.2.3...v0.2.4
[0.2.3]: https://github.com/mikelane/valid8r/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/mikelane/valid8r/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/mikelane/valid8r/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/mikelane/valid8r/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/mikelane/valid8r/releases/tag/v0.1.0
