#!/usr/bin/env python3
"""Example: Async API validation with valid8r.

This example demonstrates how to use async validators to validate data
against external APIs, such as verifying API keys, checking payment methods,
and validating geolocation constraints.

Real-world use case: Service configuration validation
- Verify API key with external service (HTTP request)
- Check payment method is valid (Payment API)
- Validate IP address geolocation (GeoIP API)
- All validations run concurrently with proper timeout handling

Requirements:
    pip install valid8r httpx

Run:
    python examples/async_api_validation.py
"""

from __future__ import annotations

import asyncio
from functools import partial
from typing import Any

from valid8r.core import (
    parsers,
    schema,
    validators,
)
from valid8r.core.maybe import (
    Failure,
    Maybe,
    Success,
)

# ============================================================================
# Mock External APIs (For demonstration purposes)
# ============================================================================


class MockAPIService:
    """Mock external API service for demonstration."""

    def __init__(self) -> None:
        """Initialize mock API with sample data."""
        self.valid_api_keys = {
            'sk-test-valid-key-123',
            'sk-prod-valid-key-456',
            'sk-dev-valid-key-789',
        }

        self.valid_payment_methods = {
            'pm_card_visa',
            'pm_card_mastercard',
            'pm_card_amex',
        }

        self.ip_locations = {
            '8.8.8.8': 'US',  # Google DNS
            '1.1.1.1': 'AU',  # Cloudflare DNS
            '208.67.222.222': 'US',  # OpenDNS
            '2001:4860:4860::8888': 'US',  # Google DNS IPv6
        }

    async def verify_api_key(self, api_key: str) -> dict[str, Any]:
        """Simulate API key verification.

        Args:
            api_key: API key to verify

        Returns:
            Response dict with valid flag and details

        """
        # Simulate network delay
        await asyncio.sleep(0.1)

        if api_key in self.valid_api_keys:
            return {'valid': True, 'key': api_key, 'scopes': ['read', 'write']}
        return {'valid': False, 'error': 'Invalid API key'}

    async def verify_payment_method(self, payment_method_id: str) -> dict[str, Any]:
        """Simulate payment method verification.

        Args:
            payment_method_id: Payment method ID to verify

        Returns:
            Response dict with valid flag and details

        """
        # Simulate network delay
        await asyncio.sleep(0.15)

        if payment_method_id in self.valid_payment_methods:
            return {
                'valid': True,
                'id': payment_method_id,
                'type': 'card',
                'status': 'active',
            }
        return {'valid': False, 'error': 'Invalid payment method'}

    async def get_ip_location(self, ip: str) -> dict[str, Any]:
        """Simulate IP geolocation lookup.

        Args:
            ip: IP address to lookup

        Returns:
            Response dict with country code

        """
        # Simulate network delay
        await asyncio.sleep(0.2)

        if ip in self.ip_locations:
            country = self.ip_locations[ip]
            return {'country': country, 'city': 'Unknown', 'region': 'Unknown'}
        return {'error': 'IP not found'}


# ============================================================================
# Async Validators
# ============================================================================


async def verify_api_key(api_key: str, api_service: MockAPIService) -> Maybe[str]:
    """Verify API key with external service.

    Args:
        api_key: API key to verify
        api_service: API service instance

    Returns:
        Success with API key if valid, Failure with error message if invalid

    """
    try:
        response = await api_service.verify_api_key(api_key)

        if response.get('valid'):
            return Maybe.success(api_key)
        return Maybe.failure(response.get('error', 'Invalid API key'))

    except Exception as e:  # noqa: BLE001
        return Maybe.failure(f'API verification failed: {e}')


async def verify_payment_method(payment_method_id: str, api_service: MockAPIService) -> Maybe[str]:
    """Verify payment method with payment API.

    Args:
        payment_method_id: Payment method ID to verify
        api_service: API service instance

    Returns:
        Success with payment method ID if valid, Failure with error if invalid

    """
    try:
        response = await api_service.verify_payment_method(payment_method_id)

        if response.get('valid'):
            if response.get('status') != 'active':
                return Maybe.failure('Payment method is not active')
            return Maybe.success(payment_method_id)
        return Maybe.failure(response.get('error', 'Invalid payment method'))

    except Exception as e:  # noqa: BLE001
        return Maybe.failure(f'Payment verification failed: {e}')


async def verify_ip_location(ip: str, allowed_countries: set[str], api_service: MockAPIService) -> Maybe[str]:
    """Verify IP address is from allowed country.

    Args:
        ip: IP address to verify
        allowed_countries: Set of allowed country codes
        api_service: API service instance

    Returns:
        Success with IP if from allowed country, Failure with error if not

    """
    try:
        response = await api_service.get_ip_location(ip)

        if 'error' in response:
            return Maybe.failure(response['error'])

        country = response.get('country')
        if country in allowed_countries:
            return Maybe.success(ip)
        return Maybe.failure(f'IP from {country}, must be from {", ".join(sorted(allowed_countries))}')

    except Exception as e:  # noqa: BLE001
        return Maybe.failure(f'Geolocation check failed: {e}')


# ============================================================================
# Schema Definition
# ============================================================================


def create_service_config_schema(api_service: MockAPIService, allowed_countries: set[str]) -> schema.Schema:
    """Create service configuration schema with async validators.

    Args:
        api_service: API service for async validation
        allowed_countries: Allowed country codes for IP geolocation

    Returns:
        Schema for validating service configuration

    """
    return schema.Schema(
        fields={
            'api_key': schema.Field(
                parser=parsers.parse_str,
                validators=[
                    # Sync validator (format check)
                    validators.matches_regex(r'^sk-[a-z]+-[a-z0-9-]+$'),
                    # Async validator (API verification)
                    partial(verify_api_key, api_service=api_service),
                ],
                required=True,
            ),
            'payment_method': schema.Field(
                parser=parsers.parse_str,
                validators=[
                    # Sync validator (format check)
                    validators.matches_regex(r'^pm_[a-z_]+$'),
                    # Async validator (payment API verification)
                    partial(verify_payment_method, api_service=api_service),
                ],
                required=True,
            ),
            'allowed_ip': schema.Field(
                parser=parsers.parse_ip,
                validators=[
                    # Async validator (geolocation check)
                    partial(
                        verify_ip_location,
                        allowed_countries=allowed_countries,
                        api_service=api_service,
                    ),
                ],
                required=True,
            ),
            'webhook_url': schema.Field(
                parser=parsers.parse_url,
                required=True,
            ),
        },
        strict=True,
    )


# ============================================================================
# Example Usage
# ============================================================================


async def example_valid_configuration(api_service: MockAPIService) -> None:
    """Example: Valid service configuration."""
    print('\n=== Example 1: Valid Configuration ===')

    allowed_countries = {'US', 'CA'}
    config_schema = create_service_config_schema(api_service, allowed_countries)

    data = {
        'api_key': 'sk-test-valid-key-123',
        'payment_method': 'pm_card_visa',
        'allowed_ip': '8.8.8.8',  # US IP
        'webhook_url': 'https://example.com/webhook',
    }

    import time

    start_time = time.perf_counter()
    result = await config_schema.validate_async(data, timeout=5.0)
    elapsed_ms = (time.perf_counter() - start_time) * 1000

    match result:
        case Success(validated_data):
            print('✓ Configuration valid:')
            print(f'  API Key: {validated_data["api_key"]}')
            print(f'  Payment: {validated_data["payment_method"]}')
            print(f'  Allowed IP: {validated_data["allowed_ip"]}')
            print(f'  Webhook: {validated_data["webhook_url"]}')
            print(f'\n  Validation completed in {elapsed_ms:.2f}ms')
            print('  Note: All async validators ran concurrently')
        case Failure(errors):
            print(f'✗ Configuration failed with {len(errors)} errors:')
            for error in errors:
                print(f'  {error.path}: {error.message}')


async def example_invalid_api_key(api_service: MockAPIService) -> None:
    """Example: Invalid API key."""
    print('\n=== Example 2: Invalid API Key ===')

    allowed_countries = {'US'}
    config_schema = create_service_config_schema(api_service, allowed_countries)

    data = {
        'api_key': 'sk-test-invalid-key',  # Invalid
        'payment_method': 'pm_card_visa',
        'allowed_ip': '8.8.8.8',
        'webhook_url': 'https://example.com/webhook',
    }

    result = await config_schema.validate_async(data, timeout=5.0)

    match result:
        case Success(validated_data):
            print(f'✓ Configuration valid: {validated_data}')
        case Failure(errors):
            print(f'✗ Configuration failed with {len(errors)} errors:')
            for error in errors:
                print(f'  {error.path}: {error.message}')


async def example_geolocation_restriction(api_service: MockAPIService) -> None:
    """Example: IP from disallowed country."""
    print('\n=== Example 3: Geolocation Restriction ===')

    allowed_countries = {'US'}  # Only allow US
    config_schema = create_service_config_schema(api_service, allowed_countries)

    data = {
        'api_key': 'sk-test-valid-key-123',
        'payment_method': 'pm_card_visa',
        'allowed_ip': '1.1.1.1',  # Australia IP (not allowed)
        'webhook_url': 'https://example.com/webhook',
    }

    result = await config_schema.validate_async(data, timeout=5.0)

    match result:
        case Success(validated_data):
            print(f'✓ Configuration valid: {validated_data}')
        case Failure(errors):
            print(f'✗ Configuration failed with {len(errors)} errors:')
            for error in errors:
                print(f'  {error.path}: {error.message}')


async def example_multiple_api_failures(api_service: MockAPIService) -> None:
    """Example: Multiple API validation failures."""
    print('\n=== Example 4: Multiple API Failures ===')

    allowed_countries = {'US'}
    config_schema = create_service_config_schema(api_service, allowed_countries)

    data = {
        'api_key': 'sk-test-invalid-key',  # Invalid
        'payment_method': 'pm_card_invalid',  # Invalid
        'allowed_ip': '1.1.1.1',  # Wrong country
        'webhook_url': 'https://example.com/webhook',
    }

    result = await config_schema.validate_async(data, timeout=5.0)

    match result:
        case Success(validated_data):
            print(f'✓ Configuration valid: {validated_data}')
        case Failure(errors):
            print(f'✗ Configuration failed with {len(errors)} errors:')
            for error in errors:
                print(f'  {error.path}: {error.message}')
            print('\n  Note: All errors collected from concurrent validations')


async def example_timeout_handling(_api_service: MockAPIService) -> None:
    """Example: Timeout handling for slow APIs."""
    print('\n=== Example 5: Timeout Handling ===')

    # Create a slow async validator for demonstration
    async def slow_validator(value: str) -> Maybe[str]:
        await asyncio.sleep(2.0)  # Intentionally slow
        return Maybe.success(value)

    slow_schema = schema.Schema(
        fields={
            'api_key': schema.Field(
                parser=parsers.parse_str,
                validators=[slow_validator],
                required=True,
            ),
        }
    )

    data = {'api_key': 'sk-test-valid-key-123'}

    try:
        print('Validating with 0.5s timeout (will timeout)...')
        _result = await slow_schema.validate_async(data, timeout=0.5)
        print('Unexpected success!')
    except TimeoutError:
        print('✗ Validation timed out after 0.5s (expected)')
        print('  Tip: Increase timeout or optimize async validators')


async def main() -> None:
    """Run all examples."""
    print('Valid8r Async API Validation Examples')
    print('=' * 50)

    # Initialize mock API service
    api_service = MockAPIService()

    # Run examples
    await example_valid_configuration(api_service)
    await example_invalid_api_key(api_service)
    await example_geolocation_restriction(api_service)
    await example_multiple_api_failures(api_service)
    await example_timeout_handling(api_service)

    print('\n' + '=' * 50)
    print('All examples completed!')


if __name__ == '__main__':
    asyncio.run(main())
