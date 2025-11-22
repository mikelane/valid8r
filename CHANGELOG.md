# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v1.17.0] (2025-11-22)

### Features

- **Type-Based Parser Generation and Dataclass Validation** ([#17](https://github.com/mikelane/valid8r/pull/17), [#16](https://github.com/mikelane/valid8r/pull/16), [#201](https://github.com/mikelane/valid8r/pull/201), [`f5c3230`](https://github.com/mikelane/valid8r/commit/f5c3230))
  - Added `from_type()` function for automatic parser generation from type annotations
  - Support for all standard types: int, str, float, bool, datetime, etc.
  - Collection types: `list[T]`, `dict[K,V]`, `set[T]`
  - Optional types with None handling
  - Union types with fallback behavior
  - Literal types for constrained values
  - Enum types with case-insensitive matching
  - Annotated types with validator chaining
  - Added `@validate` decorator for dataclass field validation
  - Automatic type coercion from strings
  - Nested dataclass validation with error paths
  - Multiple validator chaining per field
  - Comprehensive error aggregation
  - DoS protection: Input length validation before expensive operations
  - Safe parsing: `ast.literal_eval` with bounds checking (1000 char limit)
  - Public API usage: Replaced `ForwardRef._evaluate()` with `get_type_hints()`
  - 100+ new unit tests with 90%+ test coverage
  - Full BDD test coverage (63 scenarios: 41 type adapter + 22 dataclass)

## [v1.16.0] (2025-11-17)

### Features

- **Schema API with Error Accumulation and Field Path Tracking** ([#15](https://github.com/mikelane/valid8r/pull/15), [#198](https://github.com/mikelane/valid8r/pull/198), [`ffe418b`](https://github.com/mikelane/valid8r/commit/ffe418b))
  - Added `Schema` class for structured validation of complex, nested objects
  - Error accumulation: Collects ALL validation errors instead of stopping at first failure
  - Field path tracking: Precise error location (e.g., `.user.email`, `.addresses[0].street`)
  - Nested schema composition: Schemas can use other schemas as field parsers
  - Required/optional field control
  - Strict mode: Optionally reject unexpected fields
  - RFC-001 integration: Uses structured `ValidationError` with code, message, path, context
  - Python 3.10+ match/case pattern support for clean error handling
  - 18 comprehensive unit tests
  - Full BDD test coverage with Gherkin scenarios
  - Complete user guide documentation and runnable examples

## [v1.15.0] (2025-11-15)

### Features

- **Structured Error Model Foundation (RFC-001 Phase 1)** ([#189](https://github.com/mikelane/valid8r/pull/189), [`45409ad`](https://github.com/mikelane/valid8r/commit/45409ad))
  - Introduced `ValidationError` base class for structured error handling
  - Added `error_detail()` method to `Failure` class for rich error context
  - Implemented error categorization: `ParseError`, `ValidationError`, `ValueError`
  - Comprehensive test coverage for structured error model

### Documentation

- **RFC-001: Structured Error Model** ([#24](https://github.com/mikelane/valid8r/pull/24), [`0b07bd6`](https://github.com/mikelane/valid8r/commit/0b07bd6))
  - Added comprehensive RFC for multi-phase structured error implementation
  - Documented migration path from string-based to structured errors
  - Defined error categorization and rich error context

## [v1.14.0] (2025-11-14)

### Features

- **Enhanced parse_path with DoS Protection** ([#186](https://github.com/mikelane/valid8r/pull/186), [`8b361ac`](https://github.com/mikelane/valid8r/commit/8b361ac))
  - Added input length validation to prevent DoS attacks (1000 char limit)
  - Comprehensive test suite with 27 test cases covering edge cases
  - Performance testing to ensure <10ms rejection of malicious inputs

- **Pluggable IO Provider for Prompt Functions** ([#22](https://github.com/mikelane/valid8r/pull/22), [`e009f33`](https://github.com/mikelane/valid8r/commit/e009f33))
  - Introduced abstract `IOProvider` protocol for customizable I/O
  - Default `ConsoleIO` implementation maintains existing behavior
  - Enables non-interactive mode and TUI framework integration
  - Enhanced testing utilities with `MockIO` provider

## [v1.13.0] (2025-11-14)

### Features

- **Timezone-Aware Datetime and Timedelta Parsers** ([#13](https://github.com/mikelane/valid8r/pull/13), [`eaece5d`](https://github.com/mikelane/valid8r/commit/eaece5d))
  - Added `parse_datetime_tz()` for timezone-aware datetime parsing
  - Added `parse_timedelta()` for duration parsing (ISO 8601, human-readable)
  - Support for IANA timezone names and UTC offsets
  - Comprehensive test coverage for temporal parsing

## [v1.12.0] (2025-11-12)

### Features

- **Automated ReDoS Detection in CI/CD Pipeline** ([#134](https://github.com/mikelane/valid8r/pull/134), [`cdec054`](https://github.com/mikelane/valid8r/commit/cdec054))
  - Integrated `regexploit` for automated regular expression DoS vulnerability detection
  - CI pipeline fails on potential ReDoS vulnerabilities
  - Comprehensive test coverage for regex security

### CI/CD Improvements

- **Dependabot Auto-Merge Workflow** ([#184](https://github.com/mikelane/valid8r/pull/184), [`8ddbead`](https://github.com/mikelane/valid8r/commit/8ddbead))
  - Automated merging of Dependabot PRs after CI passes
  - Reduces maintenance burden for dependency updates

### Dependency Updates

- Bump `actions/upload-artifact` from 4.5.0 to 5.0.0 ([#182](https://github.com/mikelane/valid8r/pull/182))
- Bump `actions/github-script` from 7 to 8 ([#181](https://github.com/mikelane/valid8r/pull/181))
- Bump `actions/checkout` from 4.2.2 to 5.0.0 ([#183](https://github.com/mikelane/valid8r/pull/183))
- Bump `python-semantic-release` from 10.4.1 to 10.5.1 ([#180](https://github.com/mikelane/valid8r/pull/180))
- Bump `actions/download-artifact` from 4.1.8 to 6.0.0 ([#179](https://github.com/mikelane/valid8r/pull/179))

## [v1.11.0] (2025-11-09)

### Features

- **Comprehensive Performance Benchmarks** ([#178](https://github.com/mikelane/valid8r/pull/178), [`46dc036`](https://github.com/mikelane/valid8r/commit/46dc036))
  - Added benchmarks comparing valid8r vs Pydantic, marshmallow, cerberus
  - Demonstrates performance characteristics across different use cases
  - Automated benchmark suite in CI

### Documentation

- **Library Comparison Guide** ([#177](https://github.com/mikelane/valid8r/pull/177), [`1785f77`](https://github.com/mikelane/valid8r/commit/1785f77))
  - Comprehensive comparison with other validation libraries
  - Decision matrix for choosing validation approach
  - Migration guides from Pydantic, marshmallow, cerberus

- **Enable GitHub Discussions** ([#176](https://github.com/mikelane/valid8r/pull/176), [`6a5f2e9`](https://github.com/mikelane/valid8r/commit/6a5f2e9))
  - Community Q&A and feedback forum
  - Reduces issue tracker noise

### Testing

- Add coverage pragma to unreachable error handling in argparse integration ([#171](https://github.com/mikelane/valid8r/pull/171), [`1356d50`](https://github.com/mikelane/valid8r/commit/1356d50))

## [v1.10.0] (2025-11-09)

### Features

- **Argparse Integration** ([#19](https://github.com/mikelane/valid8r/pull/19), [`f20c634`](https://github.com/mikelane/valid8r/commit/f20c634))
  - Added `type_from_parser()` helper for argparse integration
  - Converts valid8r parsers to argparse-compatible type functions
  - Clean error messages for CLI validation failures

### Documentation

- **Pydantic-Settings Integration Guide** ([#18](https://github.com/mikelane/valid8r/pull/18), [`5a6ef29`](https://github.com/mikelane/valid8r/commit/5a6ef29))
  - Comprehensive guide for using valid8r with pydantic-settings
  - Examples for environment variable validation with schemas

## [v1.9.0] (2025-11-09)

### Features

- **Typer CLI Integration** ([#146](https://github.com/mikelane/valid8r/pull/146), [`f9670bc`](https://github.com/mikelane/valid8r/commit/f9670bc))
  - Added `TyperParamType` for seamless Typer integration
  - Automatic validation and error messaging in CLI applications
  - Example Typer applications demonstrating best practices

## [v1.8.0] (2025-11-09)

### Features

- **Pydantic AfterValidator and WrapValidator Support** ([#144](https://github.com/mikelane/valid8r/pull/144), [`bc3e733`](https://github.com/mikelane/valid8r/commit/bc3e733))
  - Extended Pydantic integration with AfterValidator and WrapValidator
  - Flexible validation strategies for complex use cases
  - Comprehensive examples and documentation

## [v1.7.1] (2025-11-09)

### Bug Fixes

- **Correct Parameter Names for actions/first-interaction@v3** ([#167](https://github.com/mikelane/valid8r/pull/167), [`7b726f3`](https://github.com/mikelane/valid8r/commit/7b726f3))
  - Fixed incorrect parameter names causing workflow failures

### Maintenance

- **Update GitHub Actions to Latest Stable Versions** ([#165](https://github.com/mikelane/valid8r/pull/165), [`6b758d5`](https://github.com/mikelane/valid8r/commit/6b758d5))
  - Updated all GitHub Actions to latest stable releases
  - Improved CI/CD reliability and security

## [v1.7.0] (2025-11-08)

### Features

- **Pydantic Nested Model Validation Support** ([#143](https://github.com/mikelane/valid8r/pull/143), [`465c109`](https://github.com/mikelane/valid8r/commit/465c109))
  - Added support for validating nested Pydantic models
  - Error propagation through model hierarchy
  - Comprehensive test coverage for nested validation

## [v1.6.0] (2025-11-08)

### Features

- **Filesystem Metadata Validators** ([#151](https://github.com/mikelane/valid8r/pull/151), [`860bfb5`](https://github.com/mikelane/valid8r/commit/860bfb5))
  - Added `max_size()` validator for file size constraints
  - Added `min_size()` validator for minimum file size
  - Added `has_extension()` validator for file extension checking
  - Path-based metadata validation for filesystem operations

## [v1.5.0] (2025-11-08)

### Features

- **Filesystem Permission Validators** ([#150](https://github.com/mikelane/valid8r/pull/150), [`02b9b29`](https://github.com/mikelane/valid8r/commit/02b9b29))
  - Added `is_readable()`, `is_writable()`, `is_executable()` validators
  - Permission-based validation for filesystem security
  - Comprehensive test coverage for permission checking

### Documentation

- **Require Fork-Based Contributions** ([#161](https://github.com/mikelane/valid8r/pull/161), [`f730eb7`](https://github.com/mikelane/valid8r/commit/f730eb7))
  - Updated CONTRIBUTING.md to require fork-based workflow
  - Improved security and repository organization

### Dependency Updates

- Bump `codecov/codecov-action` from 4 to 5 ([#40](https://github.com/mikelane/valid8r/pull/40))
- Bump `actions/checkout` from 4 to 5 ([#38](https://github.com/mikelane/valid8r/pull/38))

## [v1.4.0] (2025-11-07)

### Features

- **Environment Variable Integration with Schema Validation** ([#157](https://github.com/mikelane/valid8r/pull/157), [`9db8a86`](https://github.com/mikelane/valid8r/commit/9db8a86))
  - Added `EnvSchema` for declarative environment variable validation
  - Support for type coercion, default values, and required fields
  - Prefix support for environment variable namespacing
  - Integration examples for 12-factor applications

### CI/CD Improvements

- **Automate Issue Closing from PR Descriptions** ([#159](https://github.com/mikelane/valid8r/pull/159), [`5c41d05`](https://github.com/mikelane/valid8r/commit/5c41d05))
  - Automatic issue closing when PRs with "Closes #XXX" are merged
  - Works seamlessly with squash merge workflow
  - Adds traceability comments to closed issues

## [v1.3.0] (2025-11-07)

### Features

- **Pydantic Integration with validator_from_parser()** ([#153](https://github.com/mikelane/valid8r/pull/153), [`ee35b12`](https://github.com/mikelane/valid8r/commit/ee35b12))
  - Added `validator_from_parser()` helper for Pydantic v2 integration
  - Converts valid8r parsers to Pydantic field validators
  - Maintains monadic error handling within Pydantic models
  - Example integrations and comprehensive documentation

## [v1.2.0] (2025-11-07)

### Features

- **Click ParamType Integration** ([#152](https://github.com/mikelane/valid8r/pull/152), [`a27b6e1`](https://github.com/mikelane/valid8r/commit/a27b6e1))
  - Added `ClickParamType` for seamless Click CLI integration
  - Automatic validation and error messaging
  - Example Click applications with comprehensive documentation

- **Filesystem Validators** ([#156](https://github.com/mikelane/valid8r/pull/156), [`7f10998`](https://github.com/mikelane/valid8r/commit/7f10998))
  - Added `exists()` validator to verify path existence
  - Added `is_file()` and `is_dir()` validators for type checking
  - Foundation for comprehensive filesystem validation

## [v1.1.0] (2025-11-07)

### Features

- **Path Parser** ([#154](https://github.com/mikelane/valid8r/pull/154), [`45b1fac`](https://github.com/mikelane/valid8r/commit/45b1fac))
  - Added `parse_path()` parser for converting strings to `pathlib.Path`
  - Tilde expansion, relative path resolution
  - Validation for reserved names, max length, special characters
  - Cross-platform compatibility (Windows, POSIX)

### Maintenance

- Added `.worktrees/` to `.gitignore` for isolated development ([`4115e95`](https://github.com/mikelane/valid8r/commit/4115e95))

## [v1.0.0] (2025-11-06)

### Major Milestone: First Stable Release 🎉

This release marks the first stable version of valid8r, signifying commitment to API stability and backward compatibility.

### CI/CD Infrastructure

- **Modernize CI/CD Pipeline (72→100/100 Score)** ([#141](https://github.com/mikelane/valid8r/pull/141), [`876d612`](https://github.com/mikelane/valid8r/commit/876d612))
  - SHA-pinned GitHub Actions for security
  - Multi-version Python testing (3.11-3.14)
  - Comprehensive quality gates (linting, type checking, testing)
  - Automated releases with PyPI Trusted Publishing
  - Documentation deployment automation

### Documentation

- **Integrate Comprehensive Security Documentation** ([#140](https://github.com/mikelane/valid8r/pull/140), [`a424dd9`](https://github.com/mikelane/valid8r/commit/a424dd9))
  - Integrated SECURITY.md into Sphinx documentation
  - Comprehensive security best practices and vulnerability reporting
  - DoS protection patterns and examples

- **Add Comprehensive Security Documentation** ([#133](https://github.com/mikelane/valid8r/pull/133), [`aa18c4d`](https://github.com/mikelane/valid8r/commit/aa18c4d))
  - Security policy, responsible disclosure, and best practices
  - OWASP Top 10 awareness and mitigation strategies

- **Phase 1 DoS Vulnerability Assessment** ([#132](https://github.com/mikelane/valid8r/pull/132), [`6776746`](https://github.com/mikelane/valid8r/commit/6776746))
  - Systematic assessment of DoS vulnerabilities in all parsers
  - Recommendations for input validation and length guards

- Update documentation with v0.9.1 security fix and release process ([`ae2a266`](https://github.com/mikelane/valid8r/commit/ae2a266))

### Bug Fixes

- **Fix CI Configuration for Semantic Release v10** ([`731e5b2`](https://github.com/mikelane/valid8r/commit/731e5b2))
  - Disabled `build_command` parameter incompatible with semantic-release v10
  - Ensures clean release workflow

- **Remove Custom Changelog Template** ([`9bea7f5`](https://github.com/mikelane/valid8r/commit/9bea7f5))
  - Removed custom template incompatible with semantic-release v10
  - Uses default template for consistent changelog generation

## [v0.9.1] (2025-11-04)

### Bug Fixes

- **Semantic-Release Workflow Parameter + Phone Parser DoS Protection** ([#138](https://github.com/mikelane/valid8r/pull/138), [`6c7b2ff`](https://github.com/mikelane/valid8r/commit/6c7b2ff))

#### Fix 1: Semantic Release Workflow Parameter

**Problem**: Workflow failing with incorrect parameter name `build_command`

**Solution**: Changed to correct parameter `build: false` in semantic-release configuration

#### Fix 2: Phone Parser DoS Protection ([#131](https://github.com/mikelane/valid8r/issues/131))

**Problem**: Phone parser processed extremely large inputs (1MB) through regex operations before length checking, taking ~48ms to reject them (potential DoS vulnerability)

**Solution**: Moved length check to immediately after empty string validation (before regex operations)

**Performance Impact**:
- **Before**: 1MB input rejected in ~48ms
- **After**: 1MB input rejected in <1ms
- **Valid inputs**: No impact (median 0.0026ms)

**Testing**: Added `it_rejects_excessively_long_input()` test validating both error message and <10ms rejection time

- **Update Semantic-Release Workflow for uv Build Tool** ([#137](https://github.com/mikelane/valid8r/pull/137), [`712dfd8`](https://github.com/mikelane/valid8r/commit/712dfd8))
  - Fixed workflow failing with `uv: command not found` error
  - python-semantic-release runs in Docker container without uv access

## [v0.9.0] (2025-11-03)

*Note: This version predates the CHANGELOG tracking. See git history for details.*

---

[v1.17.0]: https://github.com/mikelane/valid8r/releases/tag/v1.17.0
[v1.16.0]: https://github.com/mikelane/valid8r/releases/tag/v1.16.0
[v1.15.0]: https://github.com/mikelane/valid8r/releases/tag/v1.15.0
[v1.14.0]: https://github.com/mikelane/valid8r/releases/tag/v1.14.0
[v1.13.0]: https://github.com/mikelane/valid8r/releases/tag/v1.13.0
[v1.12.0]: https://github.com/mikelane/valid8r/releases/tag/v1.12.0
[v1.11.0]: https://github.com/mikelane/valid8r/releases/tag/v1.11.0
[v1.10.0]: https://github.com/mikelane/valid8r/releases/tag/v1.10.0
[v1.9.0]: https://github.com/mikelane/valid8r/releases/tag/v1.9.0
[v1.8.0]: https://github.com/mikelane/valid8r/releases/tag/v1.8.0
[v1.7.1]: https://github.com/mikelane/valid8r/releases/tag/v1.7.1
[v1.7.0]: https://github.com/mikelane/valid8r/releases/tag/v1.7.0
[v1.6.0]: https://github.com/mikelane/valid8r/releases/tag/v1.6.0
[v1.5.0]: https://github.com/mikelane/valid8r/releases/tag/v1.5.0
[v1.4.0]: https://github.com/mikelane/valid8r/releases/tag/v1.4.0
[v1.3.0]: https://github.com/mikelane/valid8r/releases/tag/v1.3.0
[v1.2.0]: https://github.com/mikelane/valid8r/releases/tag/v1.2.0
[v1.1.0]: https://github.com/mikelane/valid8r/releases/tag/v1.1.0
[v1.0.0]: https://github.com/mikelane/valid8r/releases/tag/v1.0.0
[v0.9.1]: https://github.com/mikelane/valid8r/releases/tag/v0.9.1
[v0.9.0]: https://github.com/mikelane/valid8r/releases/tag/v0.9.0
