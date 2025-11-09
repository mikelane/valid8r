# Performance Characteristics

Valid8r is designed for **high-performance validation** with minimal overhead. This page provides comprehensive performance data comparing valid8r to popular Python validation libraries.

## TL;DR - The Bottom Line

**Valid8r is 4-300x faster than Pydantic for basic parsing, but Pydantic offers superior developer experience.**

Choose valid8r when:
- Performance is critical (APIs handling >10K req/sec)
- You need structured parsing (email parts, phone components)
- You value functional patterns and explicit error handling

Choose Pydantic when:
- You're building FastAPI applications
- Developer experience > raw performance
- You need automatic schema generation

## Benchmark Methodology

All benchmarks use **pytest-benchmark** with equivalent validation scenarios across:
- **valid8r** (this library)
- **Pydantic** (Rust-powered, industry standard)
- **marshmallow** (schema-based, mature)
- **cerberus** (lightweight)

**Environment**: macOS (Apple Silicon), Python 3.14, averaged over thousands of iterations.

**Full methodology**: See [benchmarks/README.md](../benchmarks/README.md)

## Performance Results

### Integer Parsing

Parsing the string `"42"` to an integer:

| Library      | Median Time | vs valid8r | Operations/sec |
|------------- |------------ |----------- |--------------- |
| valid8r      | 375ns       | baseline   | 2,762K ops/sec |
| cerberus     | 69,208ns    | 184x slower| 13K ops/sec    |
| marshmallow  | 67,041ns    | 179x slower| 13K ops/sec    |
| Pydantic     | 102,292ns   | 273x slower| 8.7K ops/sec   |

**Winner**: valid8r by a massive margin

**Insight**: For basic type parsing, valid8r's functional approach with minimal abstraction provides unmatched performance.

### Email Validation

Validating `"user@example.com"`:

| Library      | Median Time | vs valid8r | Operations/sec |
|------------- |------------ |----------- |--------------- |
| cerberus     | 500ns       | 78x faster | 1,966K ops/sec |
| valid8r      | 38,875ns    | baseline   | 24K ops/sec    |
| marshmallow  | 67,375ns    | 1.7x slower| 13K ops/sec    |
| Pydantic     | 507,729ns   | 13x slower | 1.9K ops/sec   |

**Winner**: cerberus (simple regex, no DNS validation)

**Insight**: valid8r uses `email-validator` which performs comprehensive validation including DNS checks. Cerberus uses a simple regex pattern which is faster but less thorough.

**Trade-off**: valid8r prioritizes correctness over raw speed for email validation.

### URL Validation

Validating `"https://example.com/path?query=value"`:

| Library      | Median Time | vs valid8r | Operations/sec |
|------------- |------------ |----------- |--------------- |
| cerberus     | 667ns       | 7.5x faster| 1,460K ops/sec |
| valid8r      | 4,875ns     | baseline   | 201K ops/sec   |
| marshmallow  | 71,209ns    | 14.6x slower| 11.8K ops/sec |
| Pydantic     | 110,875ns   | 22.7x slower| 7.8K ops/sec  |

**Winner**: cerberus (simple regex)

**Insight**: valid8r parses URLs into structured components (UrlParts), while cerberus just validates format. Different use cases.

### Nested Object Validation

Validating `{name: str, age: int, email: str}`:

| Library      | Median Time | vs valid8r | Operations/sec |
|------------- |------------ |----------- |--------------- |
| valid8r      | 36,749ns    | baseline   | 26.3K ops/sec  |
| marshmallow  | 82,958ns    | 2.3x slower| 10.4K ops/sec  |
| cerberus     | 151,167ns   | 4.1x slower| 6.0K ops/sec   |
| Pydantic     | 568,125ns   | 15.5x slower| 1.7K ops/sec  |

**Winner**: valid8r

**Insight**: valid8r's functional composition shines for complex objects. Pydantic's comprehensive features (JSON schema, serialization) add overhead.

### List Validation (100 items)

Parsing list of 100 string integers to `list[int]`:

| Library      | Median Time | vs valid8r | Operations/sec |
|------------- |------------ |----------- |--------------- |
| valid8r      | 29,709ns    | baseline   | 32.8K ops/sec  |
| Pydantic     | 125,875ns   | 4.2x slower| 7.0K ops/sec   |
| marshmallow  | 154,437ns   | 5.2x slower| 5.9K ops/sec   |
| cerberus     | 515,291ns   | 17.3x slower| 1.8K ops/sec  |

**Winner**: valid8r

**Insight**: valid8r processes each item independently with minimal overhead. Bulk validation scenarios favor valid8r's design.

## Real-World Performance Impact

### High-Throughput API Scenario

**Scenario**: REST API handling 10,000 requests/sec, each validating a user object (name, age, email).

**Per-request validation time**:
- valid8r: 37µs → **0.37% of 1ms request budget**
- Pydantic: 568µs → **56.8% of 1ms request budget**

**Bottleneck analysis**:
- At 10K req/sec, Pydantic spends 5.68 CPU seconds/sec on validation (requires 6 cores just for validation!)
- valid8r spends 0.37 CPU seconds/sec (single core handles it easily)

**Verdict**: For high-throughput APIs, valid8r's performance advantage is significant.

### CLI Input Validation

**Scenario**: Interactive CLI prompting for 10 user inputs (email, age, phone, etc.)

**Total validation overhead**:
- valid8r: ~400µs (imperceptible)
- Pydantic: ~5ms (imperceptible)

**Verdict**: For human-facing CLI tools, performance difference is negligible. Choose based on API preference.

### Batch Processing

**Scenario**: Validating 1 million records from CSV file.

**Total validation time**:
- valid8r: ~37 seconds
- Pydantic: ~568 seconds (9.5 minutes)

**Verdict**: For batch processing, valid8r's 15x advantage significantly reduces job runtime.

## Performance Characteristics by Library

### valid8r

**Design Philosophy**: Minimal abstraction, functional composition, explicit error handling.

**Strengths**:
- Fastest for basic type parsing (int, float, bool, date)
- Excellent for nested objects and lists
- Structured parsing (email parts, URL components, phone numbers)
- Zero overhead from unused features

**Trade-offs**:
- More verbose than Pydantic for complex models
- No automatic schema generation
- Smaller ecosystem compared to Pydantic

**When to Use**:
- Performance-critical APIs (>5K req/sec)
- Batch processing pipelines
- CLI tools requiring structured parsing
- Functional programming preference

### Pydantic

**Design Philosophy**: Comprehensive data validation framework with rich features.

**Strengths**:
- Best developer experience
- Automatic JSON schema generation
- Tight FastAPI integration
- Extensive ecosystem (plugins, extensions)
- Built-in serialization/deserialization

**Trade-offs**:
- 4-300x slower than valid8r for basic parsing
- Higher memory overhead
- All-or-nothing feature set (can't opt out of overhead)

**When to Use**:
- FastAPI applications
- Complex data models with many validation rules
- Projects requiring JSON schema
- Developer productivity > raw performance

### marshmallow

**Design Philosophy**: Schema-based validation with serialization focus.

**Strengths**:
- Mature ecosystem (7+ years)
- Excellent for REST API serialization
- Flask/Django integration
- Flexible transformation pipelines

**Trade-offs**:
- 1.7-5x slower than valid8r
- Less type-safe than Pydantic
- Steeper learning curve for schema definitions

**When to Use**:
- Existing Flask/Django projects
- Complex serialization requirements
- Schema-based mental model

### cerberus

**Design Philosophy**: Lightweight, minimalist validation.

**Strengths**:
- Minimal dependencies
- Very fast for simple regex patterns
- Easy to understand rule syntax
- Small memory footprint

**Trade-offs**:
- Manual regex patterns (error-prone)
- Less comprehensive validation
- Smaller community
- Limited type safety

**When to Use**:
- Microservices with minimal dependencies
- Simple validation scenarios
- Projects where library size matters

## Optimization Tips

### For valid8r Users

1. **Reuse parsers**: Create parser functions once, reuse them:
   ```python
   # Good: Reuse parser
   email_parser = parsers.parse_email
   emails = [email_parser(e) for e in email_list]

   # Less efficient: Recreate parser each time
   emails = [parsers.parse_email(e) for e in email_list]
   ```

2. **Compose validators efficiently**:
   ```python
   # Good: Combine validators with &
   age_validator = validators.minimum(0) & validators.maximum(120)

   # Less efficient: Chain .bind() calls
   result = parse_int(text).bind(validators.minimum(0)).bind(validators.maximum(120))
   ```

3. **Use early returns for fast-fail**:
   ```python
   # Good: Fail fast on basic validation
   if not email:
       return Maybe.failure('Email required')
   return parsers.parse_email(email)
   ```

### For Pydantic Users

1. **Use `model_validate()` for Python objects** (faster than parsing from JSON)
2. **Enable `frozen=True`** if models are immutable (allows optimizations)
3. **Avoid computed fields** in performance-critical paths
4. **Use `ConfigDict(validate_assignment=False)`** if you don't modify models after creation

## FAQ

### Q: Why is Pydantic slower despite being Rust-powered?

**A**: Pydantic's Rust core (`pydantic-core`) is very fast, but the Python wrapper adds overhead for:
- JSON schema generation
- Serialization metadata
- Field annotations processing
- Model metaclass initialization

For basic parsing, this overhead dominates. Pydantic shines when you use its comprehensive features.

### Q: Should I switch from Pydantic to valid8r?

**A**: Only if:
- Performance profiling shows validation is a bottleneck (>10% of request time)
- You're handling >5K requests/sec
- You don't rely on Pydantic-specific features (JSON schema, FastAPI auto-docs)

For most applications, Pydantic's developer experience justifies the performance cost.

### Q: Can I use valid8r with FastAPI?

**A**: Yes! See the [FastAPI integration example](../examples/fastapi_example.py). You'll lose automatic schema generation but gain performance.

### Q: Is valid8r production-ready?

**A**: Yes. Valid8r is at version 1.10+, has 100% test coverage, comprehensive type annotations, and is actively maintained.

## Running Benchmarks Yourself

```bash
# Clone repository
git clone https://github.com/mikelane/valid8r
cd valid8r

# Install dependencies
uv sync

# Run benchmarks
uv run pytest tests/benchmarks/test_benchmarks.py --benchmark-only

# Generate detailed report
uv run pytest tests/benchmarks/test_benchmarks.py --benchmark-only --benchmark-json=output.json
```

See [benchmarks/README.md](../benchmarks/README.md) for detailed instructions.

## Conclusion

**Valid8r excels at what it does**: fast, explicit, structured parsing with functional composition.

**Pydantic excels at what it does**: comprehensive data validation framework with rich features.

**Choose based on your priorities**:
- **Performance-critical** → valid8r
- **Developer experience** → Pydantic
- **Both?** → Use valid8r for hot paths, Pydantic for complex models

Both are excellent libraries. The "best" choice depends on your specific use case.
