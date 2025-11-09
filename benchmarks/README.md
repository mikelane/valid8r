# Valid8r Performance Benchmarks

This directory contains comprehensive performance benchmarks comparing valid8r against popular Python validation libraries:

- **Pydantic** (Rust-powered, industry standard)
- **marshmallow** (schema-based, mature ecosystem)
- **cerberus** (lightweight, minimalist)

## Quick Start

### Running All Benchmarks

```bash
# Run all benchmarks with detailed output
uv run pytest tests/benchmarks/test_benchmarks.py --benchmark-only

# Sort by name for easier comparison
uv run pytest tests/benchmarks/test_benchmarks.py --benchmark-only --benchmark-sort=name

# Generate JSON report
uv run pytest tests/benchmarks/test_benchmarks.py --benchmark-only --benchmark-json=output.json

# Show only summary statistics
uv run pytest tests/benchmarks/test_benchmarks.py --benchmark-only --benchmark-columns=min,mean,median,ops
```

### Running Specific Benchmark Categories

```bash
# Integer parsing benchmarks only
uv run pytest tests/benchmarks/test_benchmarks.py::DescribeIntegerParsing --benchmark-only

# Email validation benchmarks only
uv run pytest tests/benchmarks/test_benchmarks.py::DescribeEmailValidation --benchmark-only

# URL validation benchmarks only
uv run pytest tests/benchmarks/test_benchmarks.py::DescribeUrlValidation --benchmark-only

# Nested object validation benchmarks only
uv run pytest tests/benchmarks/test_benchmarks.py::DescribeNestedObjectValidation --benchmark-only

# List validation benchmarks (100 items)
uv run pytest tests/benchmarks/test_benchmarks.py::DescribeListValidation --benchmark-only
```

## Benchmark Scenarios

All benchmarks test **equivalent validation scenarios** across all libraries to ensure fair comparison:

### 1. Integer Parsing
- **Success case**: Parse string "42" to integer
- **Failure case**: Reject string "not a number"

### 2. Email Validation
- **Success case**: Validate "user@example.com"
- **Failure case**: Reject "not-an-email"

### 3. URL Validation
- **Success case**: Validate "https://example.com/path?query=value"
- **Failure case**: Reject "not a url"

### 4. Nested Object Validation
- **Success case**: Validate `{name: str, age: int, email: str}`
- **Failure case**: Reject when age is not an integer

### 5. List Validation (100 items)
- **Success case**: Parse list of 100 string integers to `list[int]`
- **Failure case**: Reject list with invalid item at position 50

## Performance Summary

### Key Findings (MacBook Pro M-series, Python 3.14)

**Integer Parsing (success):**
- **valid8r**: 362ns (baseline)
- **cerberus**: 76,566ns (211x slower)
- **marshmallow**: 76,071ns (210x slower)
- **Pydantic**: 114,593ns (317x slower)

**Email Validation (success):**
- **valid8r**: 40,902ns (baseline)
- **cerberus**: 509ns (12x faster!) - simple regex, no DNS validation
- **marshmallow**: 75,702ns (1.85x slower)
- **Pydantic**: 534,445ns (13x slower)

**URL Validation (success):**
- **valid8r**: 4,971ns (baseline)
- **cerberus**: 685ns (7.3x faster) - simple regex validation
- **marshmallow**: 84,428ns (17x slower)
- **Pydantic**: 128,998ns (26x slower)

**Nested Object Validation (success):**
- **valid8r**: 38,004ns (baseline)
- **cerberus**: 166,433ns (4.4x slower)
- **marshmallow**: 95,710ns (2.5x slower)
- **Pydantic**: 593,685ns (15.6x slower)

**List Validation (100 items, success):**
- **valid8r**: 30,486ns (baseline)
- **cerberus**: 550,457ns (18x slower)
- **marshmallow**: 170,427ns (5.6x slower)
- **Pydantic**: 141,931ns (4.7x slower)

### Performance Characteristics

#### valid8r
- **Fastest for**: Basic type parsing (int, float), nested objects, lists
- **Strengths**: Minimal overhead, functional composition, structured parsing
- **Best for**: High-throughput APIs, CLI input validation, performance-critical paths
- **Trade-off**: Some validation scenarios are more verbose than Pydantic models

#### Pydantic
- **Strengths**: Developer experience, automatic schema generation, extensive ecosystem
- **Best for**: API development (FastAPI), data models with complex validation rules
- **Trade-off**: Highest overhead due to comprehensive features (serialization, JSON schema, etc.)
- **Note**: Rust-powered core is very fast, but the Python wrapper adds overhead

#### marshmallow
- **Strengths**: Mature ecosystem, schema-based approach, serialization/deserialization
- **Best for**: REST APIs with transformation requirements
- **Trade-off**: Moderate overhead, less type-safe than Pydantic

#### cerberus
- **Strengths**: Lightweight, simple validation rules, very fast for basic regex patterns
- **Best for**: Simple validation scenarios, microservices with minimal dependencies
- **Trade-off**: Less feature-rich, manual regex patterns can be error-prone

## Benchmark Correctness

All benchmark scenarios are validated for correctness in `tests/benchmarks/test_benchmark_correctness.py`:

```bash
# Verify all libraries produce correct results
uv run pytest tests/benchmarks/test_benchmark_correctness.py -v
```

This ensures we're measuring equivalent validation logic across all libraries.

## Interpreting Results

### Timing Units
- **ns** = nanoseconds (1 billionth of a second)
- **µs** = microseconds (1 millionth of a second)
- **ms** = milliseconds (1 thousandth of a second)

### Columns Explained
- **Min**: Fastest single iteration
- **Max**: Slowest single iteration (includes outliers)
- **Mean**: Average time across all iterations
- **Median**: Middle value (less affected by outliers)
- **OPS**: Operations per second (higher is better)
- **Rounds**: Number of iterations executed

### What to Focus On
- **Median** is more reliable than Mean for comparing performance
- **OPS** (operations/sec) shows throughput capacity
- Compare **same scenarios** across libraries (e.g., int success vs int success)

## When to Choose Each Library

### Choose valid8r when:
- Performance is critical (high-throughput APIs, CLI tools)
- You want functional programming patterns (Maybe monad, composition)
- You need structured parsing (email parts, URL components, phone numbers)
- You value explicit error handling without exceptions

### Choose Pydantic when:
- You're building FastAPI applications (tight integration)
- You need automatic JSON schema generation
- Developer experience is priority over raw performance
- You want comprehensive validation with minimal code

### Choose marshmallow when:
- You need mature REST API serialization
- You're working with Flask/Django REST frameworks
- You require extensive transformation logic
- Schema-based validation fits your mental model

### Choose cerberus when:
- You want minimal dependencies
- Simple validation rules are sufficient
- You're building lightweight microservices
- You need quick validation without overhead

## Methodology

### Fair Comparison Principles

1. **Equivalent Validation**: All scenarios validate the same inputs with the same logic
2. **Consistent Return Values**: All functions return parsed value on success, `None` on failure
3. **No Unfair Optimizations**: No scenario is optimized for one library over others
4. **Realistic Use Cases**: Benchmarks reflect real-world validation patterns

### Benchmark Environment

- **Platform**: macOS (Apple Silicon)
- **Python**: 3.14.0
- **pytest-benchmark**: 5.2.3
- **Libraries**:
  - valid8r: 1.10.0
  - Pydantic: 2.12.3 (with pydantic-core 2.41.4)
  - marshmallow: 4.1.0
  - cerberus: 1.3.8

### Reproducibility

```bash
# Clone repository and create worktree
git clone https://github.com/mikelane/valid8r
cd valid8r
git worktree add /tmp/benchmarks feature/performance-benchmarks-172

# Install dependencies
cd /tmp/benchmarks
uv sync

# Run benchmarks
uv run pytest tests/benchmarks/test_benchmarks.py --benchmark-only
```

## Adding New Benchmarks

1. **Add scenario function** to `benchmarks/scenarios.py`:
   ```python
   def benchmark_valid8r_custom(data: str) -> CustomType | None:
       """Your validation logic."""
       result = parsers.parse_custom(data)
       return result.value_or(None)
   ```

2. **Add test to `test_benchmark_correctness.py`**:
   ```python
   def it_validates_custom_parsing_success(self) -> None:
       """Ensure all libraries correctly parse valid input."""
       assert benchmark_valid8r_custom('valid') is not None
       assert benchmark_pydantic_custom('valid') is not None
       # ... etc
   ```

3. **Add benchmark to `test_benchmarks.py`**:
   ```python
   class DescribeCustomValidation:
       def it_benchmarks_valid8r_custom_success(self, benchmark) -> None:
           result = benchmark(benchmark_valid8r_custom, 'valid')
           assert result is not None
   ```

4. **Run tests** to verify correctness, then benchmarks to measure performance

## License

MIT License - same as valid8r project
