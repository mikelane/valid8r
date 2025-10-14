# Valid8r Examples

This directory contains practical examples showing how to integrate Valid8r with popular Python frameworks and tools.

## FastAPI + Pydantic Integration

**File**: `fastapi_integration.py`

Demonstrates how to use Valid8r with FastAPI and Pydantic for robust API validation.

### What's Demonstrated

1. **Pydantic Field Validators**: Using Valid8r parsers in `@field_validator` decorators
2. **Custom Validation Functions**: Dependency injection style with Valid8r
3. **Batch Validation**: Processing multiple inputs with detailed results
4. **Configuration Parsing**: Validating complex configurations
5. **Chained Validators**: Using `bind()` to compose multiple validations

### Running the Example

```bash
# Install dependencies
pip install fastapi pydantic uvicorn

# Run the server
uvicorn examples.fastapi_integration:app --reload

# Or run directly
python examples/fastapi_integration.py
```

Visit http://localhost:8000/docs for interactive API documentation powered by FastAPI's automatic OpenAPI generation.

### Example Requests

**Create User:**
```bash
curl -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "age": 25,
    "website": "https://example.com"
  }'
```

**Batch Email Validation:**
```bash
curl -X POST "http://localhost:8000/validate-emails" \
  -H "Content-Type: application/json" \
  -d '{
    "emails": [
      "valid@example.com",
      "invalid-email",
      "another@test.org"
    ]
  }'
```

### Key Takeaways

- **Seamless Integration**: Valid8r's Maybe monad fits naturally with Pydantic's validation
- **Clear Error Messages**: Valid8r's error messages integrate with FastAPI's validation errors
- **Composability**: Chain validators using `bind()` for complex validation logic
- **Type Safety**: Full type hints throughout for excellent IDE support

## Adding More Examples

To add a new example:

1. Create a new Python file in this directory
2. Include comprehensive docstrings and comments
3. Show real-world use cases
4. Provide clear running instructions
5. Update this README with the new example

## Contributing

If you have an example that would help others, please submit a pull request!
