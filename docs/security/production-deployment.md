# Production Deployment Security Guide

This guide provides framework-specific recommendations for deploying Valid8r securely in production environments.

## Table of Contents

- [Defense in Depth Strategy](#defense-in-depth-strategy)
- [Framework-Specific Guides](#framework-specific-guides)
  - [Flask](#flask)
  - [Django](#django)
  - [FastAPI](#fastapi)
- [Rate Limiting](#rate-limiting)
- [Monitoring and Logging](#monitoring-and-logging)
- [Security Testing](#security-testing)

## Defense in Depth Strategy

**Never rely on a single layer of validation.** Use multiple defensive layers:

```
┌─────────────────────────────────────────┐
│  Layer 1: WAF / Load Balancer          │  ← DDoS protection, IP filtering
├─────────────────────────────────────────┤
│  Layer 2: Framework Middleware          │  ← Request size limits, rate limiting
├─────────────────────────────────────────┤
│  Layer 3: Application Validation        │  ← Business logic, field-level checks
├─────────────────────────────────────────┤
│  Layer 4: Valid8r Parsers               │  ← Type safety, format validation
├─────────────────────────────────────────┤
│  Layer 5: Database Constraints          │  ← Final data integrity checks
└─────────────────────────────────────────┘
```

## Framework-Specific Guides

### Flask

#### Basic Setup

```python
from flask import Flask, request, jsonify
from valid8r import parsers
from valid8r.core.maybe import Success, Failure

app = Flask(__name__)

# Configure request size limits
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024  # 10KB max request

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "Request too large"}), 413
```

#### Input Validation Pattern

```python
@app.route('/api/users', methods=['POST'])
def create_user():
    """Create user with defense-in-depth validation."""

    # Layer 1: Check content type
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json()

    # Layer 2: Check required fields
    if 'email' not in data or 'phone' not in data:
        return jsonify({"error": "Missing required fields"}), 400

    # Layer 3: Pre-validation (application-level)
    email_input = data['email']
    phone_input = data['phone']

    if len(email_input) > 254:
        return jsonify({"error": "Email too long"}), 400
    if len(phone_input) > 100:
        return jsonify({"error": "Phone too long"}), 400

    # Layer 4: Valid8r validation
    email_result = parsers.parse_email(email_input)
    phone_result = parsers.parse_phone(phone_input)

    if email_result.is_failure():
        # DON'T expose internal error details
        return jsonify({"error": "Invalid email format"}), 400

    if phone_result.is_failure():
        return jsonify({"error": "Invalid phone format"}), 400

    # Extract validated values
    email = email_result.value_or(None)
    phone = phone_result.value_or(None)

    # Layer 5: Database constraints will validate uniqueness, etc.
    user = create_user_in_db(email, phone)

    return jsonify({"id": user.id, "email": email.local + "@" + email.domain}), 201
```

#### Rate Limiting

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="redis://localhost:6379"
)

@app.route('/api/validate')
@limiter.limit("10 per minute")
def validate_endpoint():
    """Strict rate limit for validation endpoints."""
    # Validation logic
    pass
```

#### Error Logging

```python
import logging

logger = logging.getLogger(__name__)

@app.route('/api/submit', methods=['POST'])
def submit():
    data = request.get_json()
    email_input = data.get('email', '')

    result = parsers.parse_email(email_input)

    match result:
        case Success(email):
            logger.info(
                "Email validation succeeded",
                extra={"domain": email.domain, "ip": request.remote_addr}
            )
            return jsonify({"success": True})
        case Failure(error):
            # Log detailed error (not exposed to user)
            logger.warning(
                "Email validation failed",
                extra={
                    "error": error,
                    "input_length": len(email_input),
                    "ip": request.remote_addr
                }
            )
            # Generic user-facing message
            return jsonify({"error": "Invalid email format"}), 400
```

### Django

#### Settings Configuration

```python
# settings.py

# Request size limits
DATA_UPLOAD_MAX_MEMORY_SIZE = 10240  # 10KB

# Security middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # ... other middleware
]

# Rate limiting (using django-ratelimit)
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'
```

#### View-Based Validation

```python
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django_ratelimit.decorators import ratelimit
from valid8r import parsers
from valid8r.core.maybe import Success, Failure

import logging
logger = logging.getLogger(__name__)

@require_http_methods(["POST"])
@csrf_protect
@ratelimit(key='ip', rate='10/m', method='POST')
def create_user(request):
    """Create user with comprehensive validation."""

    # Layer 1: Check request size (already enforced by Django settings)

    # Layer 2: Parse JSON
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # Layer 3: Application-level validation
    email_input = data.get('email', '')
    if not email_input or len(email_input) > 254:
        return JsonResponse({"error": "Invalid email"}, status=400)

    # Layer 4: Valid8r validation
    result = parsers.parse_email(email_input)

    match result:
        case Success(email):
            # Create user
            user = User.objects.create(
                email=f"{email.local}@{email.domain}"
            )
            return JsonResponse({"id": user.id}, status=201)
        case Failure(error):
            logger.warning(f"Email validation failed: {error}")
            return JsonResponse({"error": "Invalid email format"}, status=400)
```

#### Form Validation

```python
from django import forms
from valid8r import parsers

class UserForm(forms.Form):
    email = forms.CharField(max_length=254)
    phone = forms.CharField(max_length=100)

    def clean_email(self):
        """Validate email using Valid8r."""
        email_input = self.cleaned_data['email']

        result = parsers.parse_email(email_input)

        if result.is_failure():
            raise forms.ValidationError("Invalid email format")

        email = result.value_or(None)
        return f"{email.local}@{email.domain}"

    def clean_phone(self):
        """Validate phone using Valid8r."""
        phone_input = self.cleaned_data['phone']

        result = parsers.parse_phone(phone_input)

        if result.is_failure():
            raise forms.ValidationError("Invalid phone format")

        phone = result.value_or(None)
        return phone.formatted  # e.g., "(415) 555-2671"
```

### FastAPI

#### Application Configuration

```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel, field_validator
from valid8r import parsers
from valid8r.core.maybe import Success, Failure

app = FastAPI()

# Request size limit
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["example.com", "*.example.com"]
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

#### Pydantic Integration

```python
from typing import Annotated
from pydantic import AfterValidator

def validate_email(value: str) -> str:
    """Pydantic validator using Valid8r."""
    if len(value) > 254:
        raise ValueError("Email too long")

    result = parsers.parse_email(value)

    if result.is_failure():
        raise ValueError("Invalid email format")

    email = result.value_or(None)
    return f"{email.local}@{email.domain}"

def validate_phone(value: str) -> str:
    """Pydantic validator using Valid8r."""
    if len(value) > 100:
        raise ValueError("Phone too long")

    result = parsers.parse_phone(value)

    if result.is_failure():
        raise ValueError("Invalid phone format")

    phone = result.value_or(None)
    return phone.formatted

Email = Annotated[str, AfterValidator(validate_email)]
Phone = Annotated[str, AfterValidator(validate_phone)]

class UserCreate(BaseModel):
    email: Email
    phone: Phone

@app.post("/api/users")
@limiter.limit("10/minute")
async def create_user(request: Request, user: UserCreate):
    """
    Create user with automatic validation.

    Pydantic will automatically validate using Valid8r validators.
    """
    # user.email and user.phone are already validated
    return {"email": user.email, "phone": user.phone}
```

#### Manual Validation Pattern

```python
from fastapi import Body

@app.post("/api/validate")
@limiter.limit("10/minute")
async def validate_input(
    request: Request,
    email: str = Body(..., max_length=254),
    phone: str = Body(..., max_length=100)
):
    """Validate input with explicit Valid8r calls."""

    email_result = parsers.parse_email(email)
    phone_result = parsers.parse_phone(phone)

    if email_result.is_failure() or phone_result.is_failure():
        raise HTTPException(status_code=400, detail="Invalid input")

    return {
        "email": email_result.value_or(None).domain,
        "phone": phone_result.value_or(None).formatted
    }
```

## Rate Limiting

### Redis-Based Rate Limiting (Production)

```python
from redis import Redis
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

redis_client = Redis(host='localhost', port=6379, db=0)

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379",
    strategy="fixed-window"
)

# Different limits for different endpoints
@app.route('/api/public')
@limiter.limit("100/hour")
def public_endpoint():
    pass

@app.route('/api/validation')
@limiter.limit("10/minute")
def validation_endpoint():
    pass
```

### Per-User Rate Limiting

```python
from flask import g

def get_user_id():
    """Get current user ID for rate limiting."""
    return g.user.id if hasattr(g, 'user') else get_remote_address()

limiter = Limiter(
    app=app,
    key_func=get_user_id,
    default_limits=["200 per day", "50 per hour"]
)
```

## Monitoring and Logging

### Structured Logging

```python
import logging
import json
from pythonjsonlogger import jsonlogger

# Configure JSON logging
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Usage
@app.route('/api/submit', methods=['POST'])
def submit():
    email_input = request.form.get('email')
    result = parsers.parse_email(email_input)

    if result.is_failure():
        logger.warning(
            "Validation failed",
            extra={
                "event": "validation_failure",
                "parser": "parse_email",
                "error": result.error_or("unknown"),
                "input_length": len(email_input),
                "ip": request.remote_addr,
                "user_agent": request.headers.get('User-Agent')
            }
        )
        return jsonify({"error": "Invalid email"}), 400
```

### Metrics Collection

```python
from prometheus_client import Counter, Histogram

# Define metrics
validation_failures = Counter(
    'validation_failures_total',
    'Total validation failures',
    ['parser', 'error_type']
)

validation_duration = Histogram(
    'validation_duration_seconds',
    'Time spent in validation',
    ['parser']
)

# Usage
@app.route('/api/validate', methods=['POST'])
def validate():
    email_input = request.form.get('email')

    with validation_duration.labels(parser='parse_email').time():
        result = parsers.parse_email(email_input)

    if result.is_failure():
        validation_failures.labels(
            parser='parse_email',
            error_type='format_error'
        ).inc()
        return jsonify({"error": "Invalid email"}), 400
```

## Security Testing

### Integration Tests

```python
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_request_size_limit(client):
    """Test that large requests are rejected."""
    large_payload = {'data': 'x' * 20000}  # > 10KB
    response = client.post('/api/submit', json=large_payload)
    assert response.status_code == 413

def test_malicious_email_input(client):
    """Test that malicious email input is rejected quickly."""
    import time

    malicious_email = 'x' * 1000000  # 1MB
    start = time.perf_counter()
    response = client.post('/api/submit', json={'email': malicious_email})
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert response.status_code == 400
    assert elapsed_ms < 100  # Should reject in < 100ms

def test_rate_limiting(client):
    """Test that rate limiting works."""
    # Make 11 requests (limit is 10/minute)
    for i in range(11):
        response = client.post('/api/validate', json={'email': f'test{i}@example.com'})

    # 11th request should be rate limited
    assert response.status_code == 429
```

### Load Testing

```python
# locustfile.py
from locust import HttpUser, task, between

class ValidationUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def validate_email(self):
        self.client.post("/api/validate", json={
            "email": "test@example.com"
        })

    @task(3)  # 3x more frequent
    def validate_phone(self):
        self.client.post("/api/validate", json={
            "phone": "415-555-2671"
        })
```

Run with:
```bash
locust -f locustfile.py --host=http://localhost:5000
```

## Best Practices Checklist

- [ ] Request size limits configured at framework level
- [ ] Rate limiting implemented for validation endpoints
- [ ] Multiple layers of validation (defense in depth)
- [ ] Error messages don't expose internal details
- [ ] Validation failures are logged with context
- [ ] Metrics collected for monitoring
- [ ] Security tests in CI/CD pipeline
- [ ] Load testing performed before production
- [ ] WAF/CDN configured for DDoS protection
- [ ] HTTPS enforced for all endpoints

## Additional Resources

- [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
- [OWASP Defense in Depth](https://owasp.org/www-community/Defense_in_Depth)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/stable/security/)
- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
