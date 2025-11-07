Environment Variables Integration
==================================

This guide demonstrates how to use Valid8r's environment variable integration to load typed, validated configuration from environment variables following the 12-factor app methodology.

Overview
--------

Valid8r provides a schema-based approach to environment variable configuration that:

1. Parses environment variables using Valid8r's type-safe parsers
2. Validates values against constraints (ranges, formats, patterns)
3. Supports nested configuration with hierarchical prefixes
4. Provides detailed error messages for missing or invalid values
5. Uses the Maybe monad for composable error handling

Installation
------------

The environment variables integration is included in the core Valid8r package:

.. code-block:: bash

   pip install valid8r

Why Use Valid8r for Environment Configuration?
-----------------------------------------------

Traditional environment variable handling has several pain points:

**Problem: Type Safety**

.. code-block:: python

   # Traditional approach - everything is a string
   import os

   port = os.getenv('PORT', '8080')  # Returns string "8080"
   debug = os.getenv('DEBUG', 'false')  # Returns string "false"

   # Requires manual conversion and error handling
   try:
       port = int(port)
   except ValueError:
       port = 8080

   debug = debug.lower() in ('true', '1', 'yes')  # Manual bool parsing

**Solution: Type-Safe Parsing**

.. code-block:: python

   from valid8r.integrations.env import load_env_config, EnvSchema, EnvField
   from valid8r.core.parsers import parse_int, parse_bool
   from valid8r.core.maybe import Success

   schema = EnvSchema(fields={
       'port': EnvField(parser=parse_int, default=8080),
       'debug': EnvField(parser=parse_bool, default=False),
   })

   result = load_env_config(schema)

   match result:
       case Success(config):
           port = config['port']    # int (not str!)
           debug = config['debug']  # bool (not str!)

**Problem: Validation**

.. code-block:: python

   # Traditional approach - manual validation
   port = int(os.getenv('PORT', '8080'))

   if port < 1 or port > 65535:
       raise ValueError('Port must be between 1 and 65535')

**Solution: Declarative Validation**

.. code-block:: python

   from valid8r.core.validators import between

   schema = EnvSchema(fields={
       'port': EnvField(
           parser=lambda x: parse_int(x).bind(between(1, 65535)),
           default=8080
       ),
   })

**Problem: Missing Required Values**

.. code-block:: python

   # Traditional approach - manual checks
   database_url = os.getenv('DATABASE_URL')
   if not database_url:
       raise ValueError('DATABASE_URL is required')

**Solution: Required Fields**

.. code-block:: python

   schema = EnvSchema(fields={
       'database_url': EnvField(parser=parse_str, required=True),
   })

   result = load_env_config(schema)

   match result:
       case Success(config):
           # database_url is guaranteed to be present
           db_url = config['database_url']
       case Failure(error):
           # Clear error: "database_url: required field is missing"
           print(f"Configuration error: {error}")

12-Factor App Principles
-------------------------

Valid8r's environment variable integration follows the `12-Factor App <https://12factor.net/config>`_ methodology:

**Factor III: Configuration**

   Store config in the environment. The twelve-factor app stores config in environment variables (often shortened to env vars or env). Env vars are easy to change between deploys without changing any code.

Valid8r makes this pattern type-safe and composable while following these principles:

1. **Strict separation** of config from code
2. **Environment-specific** configuration without code changes
3. **No grouping** of config into "environments" (dev/staging/prod)
4. **Declarative schema** for all configuration values

Basic Usage
-----------

Define a Configuration Schema
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create a schema that describes your expected environment variables:

.. code-block:: python

   from valid8r.integrations.env import EnvSchema, EnvField, load_env_config
   from valid8r.core.parsers import parse_int, parse_bool, parse_str
   from valid8r.core.maybe import Success, Failure

   def parse_str(text: str | None) -> Success[str] | Failure[str]:
       """Parse a string value."""
       if text is None or not isinstance(text, str):
           return Failure('Value must be a string')
       return Success(text)

   # Define your configuration schema
   schema = EnvSchema(fields={
       'port': EnvField(parser=parse_int, default=8080),
       'debug': EnvField(parser=parse_bool, default=False),
       'database_url': EnvField(parser=parse_str, required=True),
       'api_key': EnvField(parser=parse_str, required=True),
   })

Load and Validate Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Load configuration from environment variables with a prefix:

.. code-block:: python

   # Environment variables:
   # APP_PORT=3000
   # APP_DEBUG=true
   # APP_DATABASE_URL=postgresql://localhost/mydb
   # APP_API_KEY=secret123

   result = load_env_config(schema, prefix='APP_')

   match result:
       case Success(config):
           print(f"Port: {config['port']}")              # 3000 (int)
           print(f"Debug: {config['debug']}")            # True (bool)
           print(f"Database: {config['database_url']}")  # postgresql://localhost/mydb
           print(f"API Key: {config['api_key']}")        # secret123
       case Failure(error):
           print(f"Configuration error: {error}")

Schema-Based vs Dataclass Approach
-----------------------------------

Valid8r supports two approaches for environment variable configuration:

Schema-Based (Recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The schema-based approach uses ``EnvSchema`` and ``EnvField`` for maximum flexibility:

.. code-block:: python

   from valid8r.integrations.env import EnvSchema, EnvField, load_env_config
   from valid8r.core.parsers import parse_int, parse_bool, parse_email
   from valid8r.core.validators import between

   schema = EnvSchema(fields={
       'port': EnvField(
           parser=lambda x: parse_int(x).bind(between(1024, 65535)),
           default=8080
       ),
       'workers': EnvField(parser=parse_int, default=4),
       'debug': EnvField(parser=parse_bool, default=False),
       'admin_email': EnvField(parser=parse_email, required=True),
   })

   result = load_env_config(schema, prefix='APP_')

**Advantages:**

- Flexible validation with composable parsers
- Supports nested schemas
- Clear separation of parsing and validation
- No class definition required

Dataclass-Based (Alternative)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For type hinting and IDE support, you can use dataclasses:

.. code-block:: python

   from dataclasses import dataclass
   from valid8r.integrations.env import EnvSchema, EnvField, load_env_config
   from valid8r.core.parsers import parse_int, parse_bool, parse_email
   from valid8r.core.maybe import Success

   @dataclass
   class AppConfig:
       port: int = 8080
       workers: int = 4
       debug: bool = False
       admin_email: str = None

   # Define schema separately
   schema = EnvSchema(fields={
       'port': EnvField(parser=parse_int, default=8080),
       'workers': EnvField(parser=parse_int, default=4),
       'debug': EnvField(parser=parse_bool, default=False),
       'admin_email': EnvField(parser=parse_email, required=True),
   })

   result = load_env_config(schema, prefix='APP_')

   match result:
       case Success(config_dict):
           config = AppConfig(**config_dict)
           # Now you have type hints and IDE support

**Advantages:**

- Type hints for IDE autocomplete
- Explicit type annotations
- Familiar dataclass syntax

**Trade-offs:**

- Requires maintaining both schema and dataclass
- Less flexible than schema-only approach

Nested Configuration
--------------------

For complex applications, use nested schemas to organize configuration hierarchically:

.. code-block:: python

   from valid8r.integrations.env import EnvSchema, EnvField, load_env_config
   from valid8r.core.parsers import parse_int, parse_str, parse_bool
   from valid8r.core.maybe import Success

   def parse_str(text: str | None) -> Success[str] | Failure[str]:
       """Parse a string value."""
       if text is None or not isinstance(text, str):
           return Failure('Value must be a string')
       return Success(text)

   # Database configuration schema
   database_schema = EnvSchema(fields={
       'host': EnvField(parser=parse_str, default='localhost'),
       'port': EnvField(parser=parse_int, default=5432),
       'name': EnvField(parser=parse_str, required=True),
       'user': EnvField(parser=parse_str, required=True),
       'password': EnvField(parser=parse_str, required=True),
   })

   # Cache configuration schema
   cache_schema = EnvSchema(fields={
       'host': EnvField(parser=parse_str, default='localhost'),
       'port': EnvField(parser=parse_int, default=6379),
       'ttl': EnvField(parser=parse_int, default=3600),
   })

   # Top-level schema with nested schemas
   app_schema = EnvSchema(fields={
       'port': EnvField(parser=parse_int, default=8080),
       'debug': EnvField(parser=parse_bool, default=False),
       'database': EnvField(nested=database_schema),
       'cache': EnvField(nested=cache_schema),
   })

   # Environment variables:
   # APP_PORT=8000
   # APP_DEBUG=true
   # APP_DATABASE_HOST=db.example.com
   # APP_DATABASE_PORT=5432
   # APP_DATABASE_NAME=myapp
   # APP_DATABASE_USER=appuser
   # APP_DATABASE_PASSWORD=secret
   # APP_CACHE_HOST=redis.example.com
   # APP_CACHE_PORT=6379
   # APP_CACHE_TTL=7200

   result = load_env_config(app_schema, prefix='APP_')

   match result:
       case Success(config):
           print(f"App Port: {config['port']}")
           print(f"Database Host: {config['database']['host']}")
           print(f"Database Port: {config['database']['port']}")
           print(f"Cache Host: {config['cache']['host']}")
           print(f"Cache TTL: {config['cache']['ttl']}")

Best Practices
--------------

Naming Conventions
^^^^^^^^^^^^^^^^^^

Follow these conventions for environment variable names:

1. **Use uppercase**: ``DATABASE_URL`` not ``database_url``
2. **Use underscores**: ``MAX_CONNECTIONS`` not ``MaxConnections`` or ``max-connections``
3. **Use prefixes**: ``APP_PORT`` not ``PORT`` (avoids conflicts)
4. **Be descriptive**: ``DATABASE_CONNECTION_TIMEOUT`` not ``DB_TIMEOUT``

.. code-block:: python

   # Good
   schema = EnvSchema(fields={
       'max_connections': EnvField(parser=parse_int, default=100),
       'connection_timeout': EnvField(parser=parse_int, default=30),
       'retry_attempts': EnvField(parser=parse_int, default=3),
   })

   # Environment variables:
   # APP_MAX_CONNECTIONS=200
   # APP_CONNECTION_TIMEOUT=60
   # APP_RETRY_ATTEMPTS=5

   result = load_env_config(schema, prefix='APP_')

Prefixes for Multi-Service Applications
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use prefixes to avoid conflicts when running multiple services:

.. code-block:: python

   # API service
   api_schema = EnvSchema(fields={
       'port': EnvField(parser=parse_int, default=8080),
       'workers': EnvField(parser=parse_int, default=4),
   })
   api_config = load_env_config(api_schema, prefix='API_')

   # Worker service
   worker_schema = EnvSchema(fields={
       'concurrency': EnvField(parser=parse_int, default=10),
       'queue_url': EnvField(parser=parse_str, required=True),
   })
   worker_config = load_env_config(worker_schema, prefix='WORKER_')

   # Environment variables:
   # API_PORT=8080
   # API_WORKERS=4
   # WORKER_CONCURRENCY=20
   # WORKER_QUEUE_URL=redis://localhost/0

Defaults and Required Fields
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use defaults for optional configuration and ``required=True`` for mandatory fields:

.. code-block:: python

   schema = EnvSchema(fields={
       # Optional with sensible default
       'port': EnvField(parser=parse_int, default=8080),

       # Optional without default (will be omitted if not set)
       'log_level': EnvField(parser=parse_str),

       # Required - must be set or error
       'database_url': EnvField(parser=parse_str, required=True),
       'api_key': EnvField(parser=parse_str, required=True),
   })

Validation with Chained Parsers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Combine parsing and validation using ``bind()``:

.. code-block:: python

   from valid8r.core.validators import between, minimum, maximum

   schema = EnvSchema(fields={
       # Port must be valid integer between 1024 and 65535
       'port': EnvField(
           parser=lambda x: parse_int(x).bind(between(1024, 65535)),
           default=8080
       ),

       # Workers must be at least 1
       'workers': EnvField(
           parser=lambda x: parse_int(x).bind(minimum(1)),
           default=4
       ),

       # Timeout must be positive
       'timeout': EnvField(
           parser=lambda x: parse_int(x).bind(minimum(1)),
           default=30
       ),
   })

Example: FastAPI Application
-----------------------------

Here's a complete example of using Valid8r's environment variable integration with FastAPI:

.. code-block:: python

   from fastapi import FastAPI
   from valid8r.integrations.env import EnvSchema, EnvField, load_env_config
   from valid8r.core.parsers import parse_int, parse_bool, parse_str, parse_email
   from valid8r.core.validators import between
   from valid8r.core.maybe import Success, Failure
   import sys

   def parse_str(text: str | None) -> Success[str] | Failure[str]:
       """Parse a string value."""
       if text is None or not isinstance(text, str):
           return Failure('Value must be a string')
       return Success(text)

   # Define configuration schema
   config_schema = EnvSchema(fields={
       'port': EnvField(
           parser=lambda x: parse_int(x).bind(between(1024, 65535)),
           default=8080
       ),
       'workers': EnvField(
           parser=lambda x: parse_int(x).bind(between(1, 32)),
           default=4
       ),
       'debug': EnvField(parser=parse_bool, default=False),
       'database_url': EnvField(parser=parse_str, required=True),
       'redis_url': EnvField(parser=parse_str, default='redis://localhost'),
       'admin_email': EnvField(parser=parse_email, required=True),
       'secret_key': EnvField(parser=parse_str, required=True),
   })

   # Load configuration on startup
   def load_config():
       result = load_env_config(config_schema, prefix='APP_')

       match result:
           case Success(config):
               return config
           case Failure(error):
               print(f"Configuration error: {error}", file=sys.stderr)
               sys.exit(1)

   # Initialize configuration
   config = load_config()

   # Create FastAPI app
   app = FastAPI(
       title="My API",
       debug=config['debug']
   )

   @app.get("/health")
   def health_check():
       return {
           "status": "healthy",
           "debug": config['debug'],
           "admin": f"{config['admin_email'].local}@{config['admin_email'].domain}"
       }

   @app.get("/config")
   def show_config():
       # Don't expose secrets in production!
       if not config['debug']:
           return {"error": "Config endpoint disabled in production"}

       return {
           "port": config['port'],
           "workers": config['workers'],
           "debug": config['debug'],
           "database_url": config['database_url'][:20] + "...",  # Redact
           "redis_url": config['redis_url'],
           "admin_email": f"{config['admin_email'].local}@{config['admin_email'].domain}"
       }

Run with:

.. code-block:: bash

   export APP_PORT=8000
   export APP_WORKERS=8
   export APP_DEBUG=true
   export APP_DATABASE_URL=postgresql://localhost/myapp
   export APP_REDIS_URL=redis://localhost:6379/0
   export APP_ADMIN_EMAIL=admin@example.com
   export APP_SECRET_KEY=supersecret

   uvicorn app:app --host 0.0.0.0 --port $APP_PORT --workers $APP_WORKERS

Example: Docker Deployment
---------------------------

Docker and Docker Compose Integration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use environment variables with Docker for portable deployments:

**Dockerfile:**

.. code-block:: dockerfile

   FROM python:3.11-slim

   WORKDIR /app

   # Install dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   # Copy application code
   COPY . .

   # Environment variables with defaults (can be overridden)
   ENV APP_PORT=8080
   ENV APP_WORKERS=4
   ENV APP_DEBUG=false

   # Required environment variables (must be set at runtime)
   # APP_DATABASE_URL
   # APP_API_KEY
   # APP_ADMIN_EMAIL

   EXPOSE 8080

   CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]

**docker-compose.yml:**

.. code-block:: yaml

   version: '3.8'

   services:
     api:
       build: .
       ports:
         - "8000:8080"
       environment:
         # Override defaults
         APP_PORT: 8080
         APP_WORKERS: 8
         APP_DEBUG: true

         # Required configuration
         APP_DATABASE_URL: postgresql://postgres:password@db:5432/myapp
         APP_REDIS_URL: redis://redis:6379/0
         APP_ADMIN_EMAIL: admin@example.com
         APP_API_KEY: ${API_KEY}  # From .env file or shell
         APP_SECRET_KEY: ${SECRET_KEY}
       depends_on:
         - db
         - redis

     db:
       image: postgres:15-alpine
       environment:
         POSTGRES_DB: myapp
         POSTGRES_PASSWORD: password
       volumes:
         - postgres_data:/var/lib/postgresql/data

     redis:
       image: redis:7-alpine
       volumes:
         - redis_data:/data

   volumes:
     postgres_data:
     redis_data:

**.env file (for secrets, not committed):**

.. code-block:: bash

   API_KEY=your-secret-api-key-here
   SECRET_KEY=your-secret-key-here

Run with Docker Compose:

.. code-block:: bash

   docker-compose up --build

Kubernetes ConfigMap and Secrets
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For Kubernetes deployments, use ConfigMaps and Secrets:

**configmap.yaml:**

.. code-block:: yaml

   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: app-config
   data:
     APP_PORT: "8080"
     APP_WORKERS: "8"
     APP_DEBUG: "false"
     APP_DATABASE_URL: "postgresql://db-service:5432/myapp"
     APP_REDIS_URL: "redis://redis-service:6379/0"
     APP_ADMIN_EMAIL: "admin@example.com"

**secret.yaml:**

.. code-block:: yaml

   apiVersion: v1
   kind: Secret
   metadata:
     name: app-secrets
   type: Opaque
   stringData:
     APP_API_KEY: "your-secret-api-key-here"
     APP_SECRET_KEY: "your-secret-key-here"

**deployment.yaml:**

.. code-block:: yaml

   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: myapp
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: myapp
     template:
       metadata:
         labels:
           app: myapp
       spec:
         containers:
         - name: api
           image: myapp:latest
           ports:
           - containerPort: 8080
           envFrom:
           - configMapRef:
               name: app-config
           - secretRef:
               name: app-secrets
           livenessProbe:
             httpGet:
               path: /health
               port: 8080
             initialDelaySeconds: 10
             periodSeconds: 5

Apply configuration:

.. code-block:: bash

   kubectl apply -f configmap.yaml
   kubectl apply -f secret.yaml
   kubectl apply -f deployment.yaml

Example: .env File Support
---------------------------

Use python-dotenv to load environment variables from .env files during development:

**Install python-dotenv:**

.. code-block:: bash

   pip install python-dotenv

**.env file (not committed to git):**

.. code-block:: bash

   # Application configuration
   APP_PORT=8000
   APP_DEBUG=true

   # Database
   APP_DATABASE_URL=postgresql://localhost:5432/myapp_dev
   APP_DATABASE_USER=dev_user
   APP_DATABASE_PASSWORD=dev_password

   # Redis
   APP_REDIS_URL=redis://localhost:6379/0

   # Email
   APP_ADMIN_EMAIL=dev@localhost

   # Secrets (use real secrets in production!)
   APP_API_KEY=dev-api-key-123
   APP_SECRET_KEY=dev-secret-key-456

**Application code:**

.. code-block:: python

   from dotenv import load_dotenv
   from valid8r.integrations.env import load_env_config, EnvSchema, EnvField
   from valid8r.core.parsers import parse_int, parse_bool, parse_str, parse_email
   from valid8r.core.maybe import Success, Failure
   import sys

   # Load .env file (only in development)
   load_dotenv()

   def parse_str(text: str | None) -> Success[str] | Failure[str]:
       """Parse a string value."""
       if text is None or not isinstance(text, str):
           return Failure('Value must be a string')
       return Success(text)

   # Define schema
   config_schema = EnvSchema(fields={
       'port': EnvField(parser=parse_int, default=8080),
       'debug': EnvField(parser=parse_bool, default=False),
       'database_url': EnvField(parser=parse_str, required=True),
       'admin_email': EnvField(parser=parse_email, required=True),
       'api_key': EnvField(parser=parse_str, required=True),
   })

   # Load configuration (from .env or environment)
   result = load_env_config(config_schema, prefix='APP_')

   match result:
       case Success(config):
           print("Configuration loaded successfully")
           print(f"Port: {config['port']}")
           print(f"Debug: {config['debug']}")
       case Failure(error):
           print(f"Configuration error: {error}", file=sys.stderr)
           sys.exit(1)

**.env.example (committed to git):**

.. code-block:: bash

   # Copy this file to .env and fill in your values

   # Application
   APP_PORT=8080
   APP_DEBUG=false

   # Database
   APP_DATABASE_URL=postgresql://localhost:5432/myapp

   # Email
   APP_ADMIN_EMAIL=admin@example.com

   # Secrets (replace with real values)
   APP_API_KEY=your-api-key-here
   APP_SECRET_KEY=your-secret-key-here

**.gitignore:**

.. code-block:: text

   # Environment variables
   .env
   .env.local
   .env.*.local

Common Patterns and Use Cases
------------------------------

Pattern: Configuration Validation on Startup
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Fail fast if configuration is invalid:

.. code-block:: python

   import sys
   from valid8r.integrations.env import load_env_config
   from valid8r.core.maybe import Success, Failure

   def load_and_validate_config(schema, prefix=''):
       """Load config and exit if invalid."""
       result = load_env_config(schema, prefix=prefix)

       match result:
           case Success(config):
               return config
           case Failure(error):
               print(f"FATAL: Configuration validation failed:", file=sys.stderr)
               print(f"  {error}", file=sys.stderr)
               print("\nPlease set the required environment variables.", file=sys.stderr)
               sys.exit(1)

   # Load config at module level - fails immediately if invalid
   config = load_and_validate_config(my_schema, prefix='APP_')

Pattern: Environment-Specific Defaults
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use different defaults based on environment:

.. code-block:: python

   import os
   from valid8r.integrations.env import EnvSchema, EnvField
   from valid8r.core.parsers import parse_int, parse_bool, parse_str

   # Detect environment
   env = os.getenv('ENVIRONMENT', 'development')

   # Different defaults per environment
   defaults = {
       'development': {
           'port': 8080,
           'debug': True,
           'workers': 1,
           'database_url': 'sqlite:///dev.db',
       },
       'staging': {
           'port': 8080,
           'debug': True,
           'workers': 4,
           'database_url': None,  # Required in staging
       },
       'production': {
           'port': 8080,
           'debug': False,
           'workers': 8,
           'database_url': None,  # Required in production
       },
   }

   config_defaults = defaults[env]

   schema = EnvSchema(fields={
       'port': EnvField(parser=parse_int, default=config_defaults['port']),
       'debug': EnvField(parser=parse_bool, default=config_defaults['debug']),
       'workers': EnvField(parser=parse_int, default=config_defaults['workers']),
       'database_url': EnvField(
           parser=parse_str,
           default=config_defaults['database_url'],
           required=config_defaults['database_url'] is None
       ),
   })

Pattern: Feature Flags
^^^^^^^^^^^^^^^^^^^^^^^

Use environment variables for feature flags:

.. code-block:: python

   schema = EnvSchema(fields={
       'feature_new_api': EnvField(parser=parse_bool, default=False),
       'feature_experimental': EnvField(parser=parse_bool, default=False),
       'feature_beta': EnvField(parser=parse_bool, default=False),
   })

   result = load_env_config(schema, prefix='APP_')

   match result:
       case Success(config):
           if config['feature_new_api']:
               print("New API enabled")

           if config['feature_experimental']:
               print("Experimental features enabled")

Pattern: Complex List Parsing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Parse lists of values from environment variables:

.. code-block:: python

   from valid8r.core.parsers import parse_list, parse_str

   def parse_string_list(text: str | None) -> Success[list[str]] | Failure[str]:
       """Parse comma-separated list of strings."""
       if not text:
           return Success([])
       return parse_list(text, element_parser=parse_str, separator=',')

   schema = EnvSchema(fields={
       'allowed_hosts': EnvField(
           parser=parse_string_list,
           default=[]
       ),
       'cors_origins': EnvField(
           parser=parse_string_list,
           default=[]
       ),
   })

   # Environment:
   # APP_ALLOWED_HOSTS=example.com,api.example.com,www.example.com
   # APP_CORS_ORIGINS=https://app.example.com,https://admin.example.com

Troubleshooting
---------------

Common Error Messages
^^^^^^^^^^^^^^^^^^^^^

**"required field is missing"**

A required field was not set in the environment:

.. code-block:: python

   # Solution: Set the environment variable
   export APP_DATABASE_URL=postgresql://localhost/mydb

**"Value must be a valid integer"**

The value provided is not a valid integer:

.. code-block:: python

   # Bad: APP_PORT=abc
   # Good: APP_PORT=8080

**"Value must be between X and Y"**

The value is outside the allowed range:

.. code-block:: python

   # Bad: APP_PORT=99999
   # Good: APP_PORT=8080

Debugging Configuration
^^^^^^^^^^^^^^^^^^^^^^^

Add debug output to see what's being loaded:

.. code-block:: python

   import os
   from valid8r.integrations.env import load_env_config
   from valid8r.core.maybe import Success, Failure

   # Print all environment variables with prefix
   prefix = 'APP_'
   print(f"Environment variables with prefix '{prefix}':")
   for key, value in os.environ.items():
       if key.startswith(prefix):
           print(f"  {key}={value}")

   # Load configuration
   result = load_env_config(schema, prefix=prefix)

   match result:
       case Success(config):
           print("\nConfiguration loaded successfully:")
           for key, value in config.items():
               # Redact sensitive values
               if 'password' in key.lower() or 'secret' in key.lower() or 'key' in key.lower():
                   print(f"  {key}=***REDACTED***")
               else:
                   print(f"  {key}={value}")
       case Failure(error):
           print(f"\nConfiguration validation failed: {error}")

Testing Configuration Loading
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Test configuration loading with custom environment dictionaries:

.. code-block:: python

   from valid8r.integrations.env import load_env_config, EnvSchema, EnvField
   from valid8r.core.parsers import parse_int, parse_bool
   from valid8r.core.maybe import Success

   def test_config_loading():
       schema = EnvSchema(fields={
           'port': EnvField(parser=parse_int, default=8080),
           'debug': EnvField(parser=parse_bool, default=False),
       })

       # Test with custom environment (doesn't touch os.environ)
       test_env = {
           'APP_PORT': '3000',
           'APP_DEBUG': 'true',
       }

       result = load_env_config(schema, prefix='APP_', environ=test_env)

       match result:
           case Success(config):
               assert config['port'] == 3000
               assert config['debug'] is True
               print("Test passed!")

See Also
--------

* :doc:`../user_guide/parsers` - Available parsers for type conversion
* :doc:`../user_guide/validators` - Validators for value constraints
* :doc:`./fastapi_integration` - FastAPI integration patterns
* :doc:`../security/production-deployment` - Production deployment best practices

Related Examples
----------------

* **FastAPI with Defense-in-Depth**: :doc:`./fastapi_integration`
* **Interactive Prompts**: :doc:`./interactive_prompts`
* **Custom Validators**: :doc:`./custom_validators`
