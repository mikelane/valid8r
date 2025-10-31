# Valid8r Roadmap

This document outlines the strategic direction for valid8r development. The roadmap is organized into phases that build upon each other, with each phase delivering meaningful value to users.

## Current State

**Version**: 0.6.3 (Production/Stable)
**Status**: Mature core library with parsers for basic types, collections, and network formats

### Recent Achievements
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

## Phase 1: Foundation & Quick Wins (v0.7.x)

**Goal**: Establish CI/CD pipeline and add commonly requested parsers/validators

### Infrastructure
- [ ] **#45**: Implement comprehensive CI/CD pipeline with quality gates
  - Automated testing across Python 3.11-3.14
  - Code coverage reporting and enforcement
  - Security scanning and dependency updates
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

- [ ] **#12**: Filesystem Path parsers and validators
  - `parse_path` - Parse string to pathlib.Path
  - `exists()` - Verify path exists
  - `is_file()` / `is_dir()` - Type validation
  - `is_readable()` / `is_writable()` - Permission validation
  - `max_size()` - File size constraints
  - `has_extension()` - Extension validation

**Deliverable**: Robust CI/CD foundation and expanded parser/validator library

---

## Phase 2: Framework Adoption (v0.8.x)

**Goal**: Make valid8r easy to integrate with popular Python frameworks

### CLI Framework Integration
- [ ] **#20**: Click/Typer integration
  - Custom `ParamType` classes backed by valid8r parsers
  - Automatic validation and error messaging
  - Example CLI applications
  - Documentation and migration guides

- [ ] **#19**: argparse integration helpers
  - `ValidatedAction` class for argparse
  - Type converters from valid8r parsers
  - Custom error formatting
  - Example applications

### Configuration & Environment
- [ ] **#18**: Environment variable parsing
  - Schema-based env var validation
  - Prefix support for namespacing
  - Type coercion using valid8r parsers
  - `.env` file support
  - Integration examples (12-factor apps)

### Enhanced Parsers
- [ ] **#13**: Timezone-aware datetime parsing
  - `parse_datetime_tz` - Parse with timezone awareness
  - `parse_timedelta` - Duration parsing
  - ISO 8601 extended support
  - Timezone validation helpers

**Deliverable**: Seamless integration with CLI tools and configuration systems

---

## Phase 3: Advanced Features (v0.9.x)

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

### Schema API
- [ ] **#15**: Introduce schema API with error accumulation
  - Define validation schemas for complex objects
  - Accumulate all errors (not just first failure)
  - Field path tracking in error messages
  - Nested schema composition
  - JSON Schema compatibility (optional)

### Extensibility
- [ ] **#22**: Pluggable prompt IO provider
  - Abstract IO interface for prompts
  - Non-interactive mode support
  - TUI framework integration (Rich, Textual)
  - Testing utilities for custom providers

**Deliverable**: Type-safe schema validation and advanced framework integration

---

## Phase 4: Stabilization (v1.0)

**Goal**: API stabilization, breaking changes, and production hardening

### Breaking Changes
- [ ] **#24**: Design and implement structured error model
  - Error codes for programmatic handling
  - Field paths for nested validation errors
  - Rich error context (input value, constraints, suggestions)
  - Internationalization support for error messages
  - Migration guide from v0.x error strings

### Quality & Polish
- [ ] API audit and deprecation cleanup
  - Remove deprecated functions
  - Finalize public API surface
  - Performance optimization pass
  - Security audit

- [ ] Documentation refresh
  - Comprehensive tutorials
  - Framework integration guides
  - Architecture decision records
  - Migration guides
  - Video tutorials

- [ ] Community & Ecosystem
  - Plugin system for custom parsers
  - Community parser registry
  - Integration with popular libraries (Pydantic, attrs, etc.)

**Deliverable**: Stable, production-ready v1.0 release with commitment to API compatibility

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

*Last Updated: 2025-10-31*
*Current Version: 0.6.3*
*Target v1.0: TBD based on Phase 1-3 completion*
