"""Example usage of parse_datetime and parse_timedelta parsers.

This example demonstrates:
- Parsing timezone-aware datetime strings (ISO 8601)
- Parsing duration/timedelta strings in multiple formats
- Error handling with Maybe monad
- Practical use cases
"""

from __future__ import annotations

from datetime import (
    UTC,
    datetime,
)

from valid8r import parsers
from valid8r.core.maybe import (
    Failure,
    Success,
)


def example_datetime_parsing() -> None:
    """Demonstrate datetime parsing with various timezone formats."""
    print('=== DateTime Parsing Examples ===\n')

    # Example 1: Parse UTC datetime with Z suffix
    print('1. Parse UTC datetime with Z suffix:')
    result = parsers.parse_datetime('2024-01-15T10:30:00Z')
    match result:
        case Success(dt):
            print(f'   ✓ Parsed: {dt}')
            print(f'   Timezone: {dt.tzinfo}')
            print(f'   ISO format: {dt.isoformat()}\n')
        case Failure(error):
            print(f'   ✗ Error: {error}\n')

    # Example 2: Parse datetime with positive timezone offset
    print('2. Parse datetime with timezone offset (+05:30):')
    result = parsers.parse_datetime('2024-01-15T10:30:00+05:30')
    match result:
        case Success(dt):
            print(f'   ✓ Parsed: {dt}')
            print(f'   UTC offset: {dt.utcoffset()}')
            # Convert to UTC for comparison
            utc_time = dt.astimezone(UTC)
            print(f'   UTC time: {utc_time}\n')
        case Failure(error):
            print(f'   ✗ Error: {error}\n')

    # Example 3: Parse datetime with fractional seconds
    print('3. Parse datetime with microseconds:')
    result = parsers.parse_datetime('2024-01-15T10:30:00.123456Z')
    match result:
        case Success(dt):
            print(f'   ✓ Parsed: {dt}')
            print(f'   Microseconds: {dt.microsecond}\n')
        case Failure(error):
            print(f'   ✗ Error: {error}\n')

    # Example 4: Reject naive datetime (no timezone)
    print('4. Reject naive datetime (security feature):')
    result = parsers.parse_datetime('2024-01-15T10:30:00')
    match result:
        case Success(dt):
            print(f'   ✓ Parsed: {dt}\n')
        case Failure(error):
            print(f'   ✗ Expected rejection: {error}\n')


def example_timedelta_parsing() -> None:
    """Demonstrate timedelta parsing in various formats."""
    print('=== Timedelta Parsing Examples ===\n')

    examples = [
        ('90m', 'Simple minutes'),
        ('2h', 'Simple hours'),
        ('3d', 'Simple days'),
        ('1h 30m', 'Combined with spaces'),
        ('1h30m', 'Combined without spaces'),
        ('1d 2h 30m 45s', 'Fully combined'),
        ('PT1H30M', 'ISO 8601 duration'),
        ('P1DT2H', 'ISO 8601 with days'),
        ('PT45S', 'ISO 8601 seconds only'),
    ]

    for duration_str, description in examples:
        result = parsers.parse_timedelta(duration_str)
        match result:
            case Success(td):
                hours, remainder = divmod(td.total_seconds(), 3600)
                minutes, seconds = divmod(remainder, 60)
                print(f'{description:25} "{duration_str:15}" → {int(hours)}h {int(minutes)}m {int(seconds)}s')
            case Failure(error):
                print(f'{description:25} "{duration_str:15}" → Error: {error}')

    print()


def example_api_timestamp_parsing() -> None:
    """Practical example: Parse API timestamps and normalize to UTC."""
    print('=== API Timestamp Parsing (Practical Use Case) ===\n')

    def process_api_event(event_data: dict[str, str]) -> dict[str, str | datetime | None]:
        """Process an API event with timestamp normalization."""
        timestamp_str = event_data.get('timestamp', '')
        result = parsers.parse_datetime(timestamp_str)

        match result:
            case Success(dt):
                # Normalize to UTC for storage
                utc_time = dt.astimezone(UTC)
                return {
                    'event': event_data.get('event', 'unknown'),
                    'original_timestamp': timestamp_str,
                    'utc_timestamp': utc_time,
                    'status': 'success',
                }
            case Failure(error):
                return {
                    'event': event_data.get('event', 'unknown'),
                    'original_timestamp': timestamp_str,
                    'utc_timestamp': None,
                    'status': 'error',
                    'error': error,
                }

    # Test with various API events
    events = [
        {'event': 'user_login', 'timestamp': '2024-01-15T10:30:00Z'},
        {'event': 'order_placed', 'timestamp': '2024-01-15T10:30:00+05:30'},
        {'event': 'payment_received', 'timestamp': '2024-01-15T10:30:00-08:00'},
        {'event': 'invalid_event', 'timestamp': 'not-a-datetime'},
    ]

    for event_data in events:
        result = process_api_event(event_data)
        print(f'Event: {result["event"]}')
        print(f'  Original: {result["original_timestamp"]}')
        if result['status'] == 'success':
            print(f'  UTC Time: {result["utc_timestamp"]}')
        else:
            print(f'  Error: {result.get("error")}')
        print()


def example_cache_ttl_parsing() -> None:
    """Practical example: Parse cache TTL from configuration."""
    print('=== Cache TTL Parsing (Practical Use Case) ===\n')

    def configure_cache(cache_name: str, ttl_str: str, default_ttl: int = 3600) -> dict[str, str | int]:
        """Configure cache with parsed TTL or default."""
        result = parsers.parse_timedelta(ttl_str)

        match result:
            case Success(td):
                ttl_seconds = int(td.total_seconds())
                return {'cache': cache_name, 'ttl': ttl_seconds, 'status': 'configured'}
            case Failure(error):
                return {
                    'cache': cache_name,
                    'ttl': default_ttl,
                    'status': 'using_default',
                    'error': error,
                }

    # Configure various caches
    cache_configs = [
        ('user_sessions', '15m'),
        ('api_responses', '5m'),
        ('static_content', '1d'),
        ('temporary_data', 'PT30M'),  # ISO 8601
        ('invalid_config', 'forever'),  # Will use default
    ]

    for cache_name, ttl_str in cache_configs:
        config = configure_cache(cache_name, ttl_str)
        print(f'Cache: {config["cache"]:20} TTL: {config["ttl"]:>6}s ({ttl_str:10})', end='')
        if config['status'] == 'using_default':
            print(f' [DEFAULT - {config.get("error")}]')
        else:
            print()

    print()


def example_deadline_calculation() -> None:
    """Practical example: Calculate deadline from current time plus duration."""
    print('=== Deadline Calculation (Practical Use Case) ===\n')

    def calculate_deadline(task_name: str, duration_str: str) -> dict[str, str | datetime | None]:
        """Calculate task deadline from duration."""
        result = parsers.parse_timedelta(duration_str)

        match result:
            case Success(td):
                now = datetime.now(UTC)
                deadline = now + td
                return {
                    'task': task_name,
                    'duration': duration_str,
                    'deadline': deadline,
                    'status': 'scheduled',
                }
            case Failure(error):
                return {
                    'task': task_name,
                    'duration': duration_str,
                    'deadline': None,
                    'status': 'error',
                    'error': error,
                }

    # Calculate deadlines for various tasks
    tasks = [
        ('code_review', '2h'),
        ('ci_pipeline', '15m'),
        ('deployment', '1d'),
        ('rollback_window', 'PT30M'),
    ]

    for task_name, duration in tasks:
        result = calculate_deadline(task_name, duration)
        print(f'Task: {result["task"]:20} Duration: {result["duration"]:10}', end='')
        if result['status'] == 'scheduled':
            deadline = result['deadline']
            if isinstance(deadline, datetime):
                print(f' Deadline: {deadline.isoformat()}')
        else:
            print(f' Error: {result.get("error")}')

    print()


def example_error_handling() -> None:
    """Demonstrate comprehensive error handling."""
    print('=== Error Handling Examples ===\n')

    error_cases = [
        ('Empty datetime', '', 'datetime'),
        ('Invalid format', 'not-a-datetime', 'datetime'),
        ('Naive datetime', '2024-01-15T10:30:00', 'datetime'),
        ('Oversized input', '2024-01-15T10:30:00Z' * 10, 'datetime'),
        ('Empty duration', '', 'timedelta'),
        ('Invalid duration', 'forever', 'timedelta'),
        ('Negative duration', '-90m', 'timedelta'),
        ('Oversized duration', '1h30m' * 50, 'timedelta'),
    ]

    for description, input_str, parser_type in error_cases:
        result = parsers.parse_datetime(input_str) if parser_type == 'datetime' else parsers.parse_timedelta(input_str)

        match result:
            case Success(value):
                print(f'{description:25} → Unexpected success: {value}')
            case Failure(error):
                print(f'{description:25} → {error}')

    print()


def main() -> None:
    """Run all datetime/timedelta examples."""
    example_datetime_parsing()
    example_timedelta_parsing()
    example_api_timestamp_parsing()
    example_cache_ttl_parsing()
    example_deadline_calculation()
    example_error_handling()


if __name__ == '__main__':
    main()
