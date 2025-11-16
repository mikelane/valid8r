# Valid8r Roadmap

This document outlines the strategic direction for valid8r development. The roadmap is organized into phases that build upon each other, with each phase delivering meaningful value to users.

## Current State

**Version**: 1.15.0 (Production/Stable)
**Status**: Mature core library with extensive framework integrations and structured error model foundation

### Recently Completed (v1.0.0-v1.15.0)

**v1.15.0 - Structured Error Model Foundation (RFC-001 Phase 1)**
- ✅ ValidationError base class for structured error handling (#189)
- ✅ Error categorization: ParseError, ValidationError, ValueError
- ✅ error_detail() method for rich error context
- ✅ RFC-001 documentation for multi-phase implementation (#24)

**v1.14.0 - Enhanced Security and Pluggable I/O**
- ✅ parse_path with DoS protection (1000 char limit) (#186)
- ✅ Pluggable IOProvider for prompt functions (#22)
- ✅ Non-interactive mode support and TUI framework integration

**v1.13.0 - Temporal Parsers**
- ✅ parse_datetime_tz() for timezone-aware parsing (#13)
- ✅ parse_timedelta() for duration parsing (ISO 8601, human-readable)

**v1.12.0 - Security Infrastructure**
- ✅ Automated ReDoS detection in CI/CD pipeline (#134)
- ✅ Dependabot auto-merge workflow (#184)

**v1.11.0 - Performance and Documentation**
- ✅ Comprehensive benchmarks vs Pydantic/marshmallow/cerberus (#178)
- ✅ Library comparison guide and migration docs (#177)
- ✅ GitHub Discussions enabled (#176)

**v1.10.0 - CLI Framework Integration**
- ✅ argparse integration with type_from_parser() (#19)
- ✅ Pydantic-settings integration guide (#18)

**v1.9.0 - v1.8.0 - Typer and Pydantic Extensions**
- ✅ Typer CLI integration (#146)
- ✅ Pydantic AfterValidator and WrapValidator support (#144)

**v1.7.x - Pydantic and CI Improvements**
- ✅ Pydantic nested model validation (#143)
- ✅ GitHub Actions updated to latest stable versions (#165)

**v1.6.0 - v1.5.0 - Filesystem Validators**
- ✅ Filesystem metadata validators: max_size, min_size, has_extension (#151)
- ✅ Permission validators: is_readable, is_writable, is_executable (#150)

**v1.4.0 - Environment Variables**
- ✅ EnvSchema for declarative environment variable validation (#157)
- ✅ Auto-close issues from PR descriptions (#159)

**v1.3.0 - v1.2.0 - Framework Integrations**
- ✅ Pydantic integration with validator_from_parser() (#153)
- ✅ Click ParamType integration (#152)
- ✅ Filesystem validators: exists, is_file, is_dir (#156)

**v1.1.0 - Path Parser**
- ✅ parse_path() for pathlib.Path parsing (#154)
- ✅ Tilde expansion, relative path resolution, cross-platform support

**v1.0.0 - First Stable Release 🎉**
- ✅ CI/CD pipeline modernization (72→100/100 score) (#141)
- ✅ Comprehensive security documentation (#140, #133, #132)
- ✅ PyPI Trusted Publishing and automated releases
- ✅ API stability commitment

### Foundation Achievements (v0.x)
- ✅ Common validators: matches_regex, in_set, non_empty_string, unique_items, subset_of, superset_of, is_sorted (#14, #116)
- ✅ Phone number parsing with NANP validation (#43)
- ✅ URL and Email parsers with structured results (#11)
- ✅ IP address and CIDR parsers (#10)
- ✅ UUID parser with version validation (#9)
- ✅ Comprehensive testing utilities and documentation

## Strategic Vision

Valid8r aims to become the go-to validation library for Python applications by:
1. **Framework Integration**: Making validation seamless across CLI frameworks, web frameworks, and config systems
2. **Type Safety**: Leveraging Python's type system for automatic parser/validator generation
3. **Developer Experience**: Providing clear error messages, great docs, and easy adoption
4. **Functional Patterns**: Maintaining clean monadic error handling without exceptions

---

## Phase 1: Foundation & Quick Wins (v0.7.x-v1.x) ✅ COMPLETED

**Goal**: Establish CI/CD pipeline and add commonly requested parsers/validators

### Infrastructure
- [x] **#45**: Implement comprehensive CI/CD pipeline with quality gates ✅ *Completed in v1.0.0 (#141)*
  - Automated testing across Python 3.11-3.14
  - Code coverage reporting and enforcement
  - Security scanning and dependency updates (ReDoS detection #134)
  - Automated releases with semantic versioning
  - Documentation deployment

### Parsers & Validators
- [x] **#14**: Add common validators ✅ *Completed in v0.6.3 (#116)*
  - `matches_regex` - Pattern matching with compiled regex
  - `in_set` - Membership validation
  - `non_empty_string` - String presence validation
  - `unique_items` - Collection uniqueness
  - `subset_of` / `superset_of` - Set relationship validation
  - `is_sorted` - Order validation for sequences

- [x] **#12**: Filesystem Path parsers and validators ✅ *Completed in v1.1.0-v1.6.0*
  - `parse_path` - Parse string to pathlib.Path (#154)
  - `exists()` - Verify path exists (#156)
  - `is_file()` / `is_dir()` - Type validation (#156)
  - `is_readable()` / `is_writable()` - Permission validation (#150)
  - `max_size()` - File size constraints (#151)
  - `has_extension()` - Extension validation (#151)

**Deliverable**: ✅ Robust CI/CD foundation and expanded parser/validator library

---

## Phase 2: Framework Adoption (v0.8.x-v1.x) ✅ COMPLETED

**Goal**: Make valid8r easy to integrate with popular Python frameworks

### CLI Framework Integration
- [x] **#20**: Click/Typer integration ✅ *Completed in v1.2.0 and v1.9.0*
  - Custom `ParamType` classes backed by valid8r parsers (#152, #146)
  - Automatic validation and error messaging
  - Example CLI applications
  - Documentation and migration guides

- [x] **#19**: argparse integration helpers ✅ *Completed in v1.10.0 (#170)*
  - `type_from_parser()` helper for argparse
  - Type converters from valid8r parsers
  - Custom error formatting
  - Example applications

### Configuration & Environment
- [x] **#18**: Environment variable parsing ✅ *Completed in v1.4.0 (#157) and v1.10.0 (#169)*
  - Schema-based env var validation with `EnvSchema`
  - Prefix support for namespacing
  - Type coercion using valid8r parsers
  - Integration examples (12-factor apps)
  - Pydantic-settings integration guide

### Enhanced Parsers
- [x] **#13**: Timezone-aware datetime parsing ✅ *Completed in v1.13.0 (#188)*
  - `parse_datetime_tz()` - Parse with timezone awareness
  - `parse_timedelta()` - Duration parsing
  - ISO 8601 extended support
  - IANA timezone names and UTC offsets

**Deliverable**: ✅ Seamless integration with CLI tools and configuration systems

---

## Phase 3: Advanced Features (v0.9.x-v1.x) 🚧 IN PROGRESS

**Goal**: Enable advanced use cases with type system integration and schema validation

### Type System Integration
- [ ] **#17**: Build parsers/validators from typing annotations
  - `from_type()` - Generate parser from type hint
  - Support for `Annotated`, `Literal`, `Union`, `Optional`
  - Custom metadata for constraints
  - Recursive type handling for nested structures

- [ ] **#16**: Dataclass integration
  - Field-level validation with decorators
  - Automatic parser generation from dataclass fields
  - Error aggregation across fields
  - Pre/post validation hooks
  - **Note**: Pydantic integration completed (#153, #144, #143) - provides similar functionality

### Schema API
- [ ] **#15**: Introduce schema API with error accumulation
  - Define validation schemas for complex objects
  - Accumulate all errors (not just first failure)
  - Field path tracking in error messages
  - Nested schema composition
  - JSON Schema compatibility (optional)

### Extensibility
- [x] **#22**: Pluggable prompt IO provider ✅ *Completed in v1.14.0 (#187)*
  - Abstract IO interface for prompts (`IOProvider` protocol)
  - Non-interactive mode support
  - TUI framework integration (Rich, Textual)
  - Testing utilities with `MockIO` provider

**Deliverable**: 🚧 Type-safe schema validation and advanced framework integration (partial - Pydantic integration complete)

---

## Phase 4: Stabilization & Structured Errors (v1.0-v2.0) 🚧 IN PROGRESS

**Goal**: API stabilization, structured error model, and production hardening

### Structured Error Model (RFC-001)
- [x] **#24 Phase 1**: Foundation ✅ *Completed in v1.15.0 (#189, #24)*
  - `ValidationError` base class for structured error handling
  - Error categorization: `ParseError`, `ValidationError`, `ValueError`
  - `error_detail()` method for rich error context
  - Comprehensive RFC documentation

- [ ] **#24 Phase 2**: Parser Integration (v1.16.0-v1.17.0)
  - Migrate parsers to return structured errors
  - Maintain backward compatibility with `.error_or()`
  - Enhanced error messages with field paths

- [ ] **#24 Phase 3**: Validator Integration (v1.18.0-v1.19.0)
  - Migrate validators to structured errors
  - Error aggregation across validation chains
  - Rich error context (input, constraints, suggestions)

- [ ] **#24 Phase 4**: Advanced Features (v1.20.0+)
  - Error codes for programmatic handling
  - Internationalization support
  - Complete migration guide from string-based errors

### Quality & Polish
- [x] **v1.0.0**: First stable release ✅
  - API stability commitment
  - Finalized public API surface
  - Performance optimization (benchmarks #178)
  - Security audit (ReDoS detection #134, DoS protection #186)

- [x] Documentation excellence ✅
  - Comprehensive tutorials and guides
  - Framework integration guides (Click, Typer, argparse, Pydantic)
  - Library comparison guide (#177)
  - Migration guides from other libraries
  - Architecture documentation

- [x] Community & Ecosystem ✅
  - GitHub Discussions enabled (#176)
  - Integration with popular libraries (Pydantic #153, Click #152, Typer #146)
  - Comprehensive benchmarking (#178)

- [ ] Future Enhancements
  - Plugin system for custom parsers
  - Community parser registry
  - Additional framework integrations (attrs, etc.)

**Deliverable**: 🚧 Production-ready library with structured error model (Phase 1 complete, Phases 2-4 in progress)

---

## Future Considerations (Post-1.0)

### Potential Features
- **Async validation**: Support for async validators (API calls, database lookups)
- **Localization**: Multi-language error messages
- **GraphQL integration**: Schema validation for GraphQL APIs
- **OpenAPI integration**: Generate validators from OpenAPI specs
- **Performance**: Compiled validators using Cython or Rust extensions
- **Web frameworks**: FastAPI, Flask, Django integration helpers

### Community Requests
Feature requests and priorities will evolve based on community feedback. Issues labeled `enhancement` are candidates for future roadmap inclusion.

---

## Contributing

This roadmap is a living document. We welcome:
- **Feature requests**: Open an issue with the `enhancement` label
- **Implementation**: Comment on issues to claim work, follow BDD+TDD workflow
- **Feedback**: Discuss priorities and direction in GitHub Discussions

See [CLAUDE.md](./CLAUDE.md) for development workflow and [CONTRIBUTING.md](./CONTRIBUTING.md) for contribution guidelines.

---

## Roadmap Principles

1. **Backward Compatibility**: Minimize breaking changes until v1.0
2. **Quality First**: All features require comprehensive tests and documentation
3. **User-Centric**: Prioritize features that solve real user problems
4. **Functional Core**: Maintain clean functional patterns and monadic error handling
5. **Zero Dependencies**: Keep core library dependency-free when possible

---

*Last Updated: 2025-11-16*
*Current Version: 1.15.0*
*v1.0 Released: 2025-11-06*
*Next Major Milestone: v2.0 (RFC-001 Complete - Estimated Q1 2026)*
