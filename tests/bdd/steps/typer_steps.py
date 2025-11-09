"""BDD step definitions for Typer integration."""

from __future__ import annotations

import ipaddress
import subprocess
import sys
import tempfile
import textwrap
import uuid
from pathlib import Path
from typing import TYPE_CHECKING

from behave import (  # type: ignore[import-untyped]
    given,
    then,
    when,
)

if TYPE_CHECKING:
    from behave.runner import Context  # type: ignore[import-untyped]


@given('the valid8r.integrations.typer module exists')
def step_typer_module_exists(context: Context) -> None:  # noqa: ARG001
    """Verify that the typer integration module can be imported."""
    try:
        from valid8r.integrations import typer  # noqa: F401
    except ImportError:
        msg = 'valid8r.integrations.typer module does not exist'
        raise ImportError(msg) from None


@given('I have imported TyperParser')
def step_import_typer_parser(context: Context) -> None:
    """Import TyperParser from the typer integration module."""
    from valid8r.integrations.typer import TyperParser

    context.TyperParser = TyperParser


@given('a Typer CLI with option using TyperParser(parse_email)')
def step_typer_cli_email_option(context: Context) -> None:
    """Create a Typer CLI with email validation."""
    # Create a temporary Python script with a Typer CLI
    cli_code = textwrap.dedent("""
        import typer
        from typing_extensions import Annotated
        from valid8r.core.parsers import parse_email
        from valid8r.integrations.typer import TyperParser

        app = typer.Typer()

        @app.command()
        def main(email: Annotated[str, typer.Option(parser=TyperParser(parse_email))]) -> None:
            # Output the parsed email in a format we can verify
            print(f"EMAIL_LOCAL:{email.local}")
            print(f"EMAIL_DOMAIN:{email.domain}")

        if __name__ == "__main__":
            app()
    """)

    # Store the CLI code for execution
    context.cli_code = cli_code
    context.parser_name = 'parse_email'


@given('a Typer CLI with option using TyperParser(parse_phone)')
def step_typer_cli_phone_option(context: Context) -> None:
    """Create a Typer CLI with phone validation."""
    cli_code = textwrap.dedent("""
        import typer
        from typing_extensions import Annotated
        from valid8r.core.parsers import parse_phone
        from valid8r.integrations.typer import TyperParser

        app = typer.Typer()

        @app.command()
        def main(phone: Annotated[str, typer.Option(parser=TyperParser(parse_phone))]) -> None:
            print(f"PHONE_AREA_CODE:{phone.area_code}")
            print(f"PHONE_EXCHANGE:{phone.exchange}")
            print(f"PHONE_SUBSCRIBER:{phone.subscriber}")

        if __name__ == "__main__":
            app()
    """)

    context.cli_code = cli_code
    context.parser_name = 'parse_phone'


@given('a parser with parse_int & minimum({min_val:d}) & maximum({max_val:d})')
def step_parser_with_chained_validators(context: Context, min_val: int, max_val: int) -> None:
    """Create a parser with chained validators."""
    # Store the validator configuration
    context.min_val = min_val
    context.max_val = max_val
    context.parser_name = 'chained_parser'


@given('a Typer CLI with option using TyperParser(parser)')
def step_typer_cli_with_parser(context: Context) -> None:
    """Create a Typer CLI using the stored parser configuration."""
    cli_code = textwrap.dedent(f"""
        import typer
        from typing_extensions import Annotated
        from valid8r.core.parsers import parse_int
        from valid8r.core.validators import minimum, maximum
        from valid8r.integrations.typer import TyperParser

        app = typer.Typer()

        # Create the chained parser
        port_parser = parse_int
        validator = minimum({context.min_val}) & maximum({context.max_val})

        def chained_parser(text: str | None):
            return port_parser(text).bind(validator)

        @app.command()
        def main(port: Annotated[int, typer.Option(parser=TyperParser(chained_parser))]) -> None:
            print(f"PORT:{{port}}")

        if __name__ == "__main__":
            app()
    """)

    context.cli_code = cli_code


@given('a Typer CLI with argument using TyperParser(parse_uuid)')
def step_typer_cli_uuid_argument(context: Context) -> None:
    """Create a Typer CLI with UUID argument validation."""
    cli_code = textwrap.dedent("""
        import typer
        from typing_extensions import Annotated
        from valid8r.core.parsers import parse_uuid
        from valid8r.integrations.typer import TyperParser

        app = typer.Typer()

        @app.command()
        def main(user_id: Annotated[str, typer.Argument(parser=TyperParser(parse_uuid))]) -> None:
            print(f"UUID:{user_id}")

        if __name__ == "__main__":
            app()
    """)

    context.cli_code = cli_code
    context.parser_name = 'parse_uuid'


@given('a Typer CLI with option using TyperParser(parse_ipv4)')
def step_typer_cli_ipv4_option(context: Context) -> None:
    """Create a Typer CLI with IPv4 validation."""
    cli_code = textwrap.dedent("""
        import typer
        from typing_extensions import Annotated
        from valid8r.core.parsers import parse_ipv4
        from valid8r.integrations.typer import TyperParser

        app = typer.Typer()

        @app.command()
        def main(ip: Annotated[str, typer.Option(parser=TyperParser(parse_ipv4))]) -> None:
            print(f"IP:{ip}")

        if __name__ == "__main__":
            app()
    """)

    context.cli_code = cli_code
    context.parser_name = 'parse_ipv4'


@given('a Typer CLI with TyperParser(parse_email, error_prefix="Email address")')
def step_typer_cli_email_with_prefix(context: Context) -> None:
    """Create a Typer CLI with custom error prefix."""
    cli_code = textwrap.dedent("""
        import typer
        from typing_extensions import Annotated
        from valid8r.core.parsers import parse_email
        from valid8r.integrations.typer import TyperParser

        app = typer.Typer()

        @app.command()
        def main(
            email: Annotated[str, typer.Option(parser=TyperParser(parse_email, error_prefix="Email address"))]
        ) -> None:
            print(f"EMAIL:{email.local}@{email.domain}")

        if __name__ == "__main__":
            app()
    """)

    context.cli_code = cli_code
    context.parser_name = 'parse_email'


@given('a Typer CLI with email option using TyperParser(parse_email)')
def step_typer_cli_multiple_options_email(context: Context) -> None:
    """Create a Typer CLI with multiple options - email part."""
    context.multi_option_email = True


@given('the same CLI has phone option using TyperParser(parse_phone)')
def step_typer_cli_multiple_options_phone(context: Context) -> None:
    """Create a Typer CLI with multiple options - phone part."""
    cli_code = textwrap.dedent("""
        import typer
        from typing_extensions import Annotated
        from valid8r.core.parsers import parse_email, parse_phone
        from valid8r.integrations.typer import TyperParser

        app = typer.Typer()

        @app.command()
        def main(
            email: Annotated[str, typer.Option(parser=TyperParser(parse_email))],
            phone: Annotated[str, typer.Option(parser=TyperParser(parse_phone))]
        ) -> None:
            print(f"EMAIL:{email.local}@{email.domain}")
            print(f"PHONE:{phone.area_code}-{phone.exchange}-{phone.subscriber}")

        if __name__ == "__main__":
            app()
    """)

    context.cli_code = cli_code
    context.parser_name = 'multi_option'


@given('a Typer CLI with TyperParser(parse_int, name="port_number")')
def step_typer_cli_with_custom_name(context: Context) -> None:
    """Create a Typer CLI with custom type name."""
    cli_code = textwrap.dedent("""
        import typer
        from typing_extensions import Annotated
        from valid8r.core.parsers import parse_int
        from valid8r.integrations.typer import TyperParser

        app = typer.Typer()

        @app.command()
        def main(port: Annotated[int, typer.Option(parser=TyperParser(parse_int, name="port_number"))]) -> None:
            print(f"PORT:{port}")

        if __name__ == "__main__":
            app()
    """)

    context.cli_code = cli_code
    context.parser_name = 'parse_int'


@when('the user provides valid email "{email}"')
@when('the user provides invalid email "{email}"')
def step_user_provides_email(context: Context, email: str) -> None:
    """Run the CLI with an email."""
    _run_cli(context, ['--email', email])


@when('the user provides valid phone "{phone}"')
@when('the user provides invalid phone "{phone}"')
def step_user_provides_phone(context: Context, phone: str) -> None:
    """Run the CLI with a phone."""
    _run_cli(context, ['--phone', phone])


@when('the user provides port "{port}"')
def step_user_provides_port(context: Context, port: str) -> None:
    """Run the CLI with a port number."""
    _run_cli(context, ['--port', port])


@when('the user provides valid UUID "{uuid_str}"')
@when('the user provides invalid UUID "{uuid_str}"')
def step_user_provides_uuid(context: Context, uuid_str: str) -> None:
    """Run the CLI with a UUID."""
    _run_cli(context, [uuid_str])  # Argument, not option


@when('the user provides valid IP "{ip}"')
def step_user_provides_valid_ip(context: Context, ip: str) -> None:
    """Run the CLI with a valid IP address."""
    _run_cli(context, ['--ip', ip])


@when('the user provides both email "{email}" and phone "{phone}"')
def step_user_provides_email_and_phone(context: Context, email: str, phone: str) -> None:
    """Run the CLI with both email and phone."""
    _run_cli(context, ['--email', email, '--phone', phone])


@when('the user requests help for the CLI')
def step_user_requests_help(context: Context) -> None:
    """Run the CLI with --help."""
    _run_cli(context, ['--help'])


@then('the CLI accepts the input')
def step_cli_accepts_input(context: Context) -> None:
    """Verify that the CLI accepted the input (exit code 0)."""
    assert context.cli_exit_code == 0, (
        f'Expected exit code 0 but got {context.cli_exit_code}\n'
        f'stdout: {context.cli_stdout}\n'
        f'stderr: {context.cli_stderr}'
    )


@then('the CLI rejects the input')
def step_cli_rejects_input(context: Context) -> None:
    """Verify that the CLI rejected the input (non-zero exit code)."""
    assert context.cli_exit_code != 0, (
        f'Expected non-zero exit code but got {context.cli_exit_code}\n'
        f'stdout: {context.cli_stdout}\n'
        f'stderr: {context.cli_stderr}'
    )


@then('the parsed value is an EmailAddress with local "{local}" and domain "{domain}"')
def step_parsed_email_value(context: Context, local: str, domain: str) -> None:
    """Verify the parsed email address components."""
    assert f'EMAIL_LOCAL:{local}' in context.cli_stdout, (
        f'Expected EMAIL_LOCAL:{local} in output\nstdout: {context.cli_stdout}'
    )
    assert f'EMAIL_DOMAIN:{domain}' in context.cli_stdout, (
        f'Expected EMAIL_DOMAIN:{domain} in output\nstdout: {context.cli_stdout}'
    )


@then('the parsed value is a PhoneNumber with area code "{area_code}"')
def step_parsed_phone_value(context: Context, area_code: str) -> None:
    """Verify the parsed phone number components."""
    assert f'PHONE_AREA_CODE:{area_code}' in context.cli_stdout, (
        f'Expected PHONE_AREA_CODE:{area_code} in output\nstdout: {context.cli_stdout}'
    )


@then('the error message mentions "{substring}"')
def step_error_message_mentions(context: Context, substring: str) -> None:
    """Verify the error message contains a specific substring."""
    import re

    # Strip ANSI color codes
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    error_text = ansi_escape.sub('', context.cli_stderr).lower()
    assert substring.lower() in error_text, f'Expected "{substring}" in error message\nstderr: {context.cli_stderr}'


@then('the error message starts with "{prefix}"')
def step_error_message_starts_with(context: Context, prefix: str) -> None:
    """Verify the error message starts with a specific prefix."""
    # Typer outputs errors to stderr
    error_lines = [line.strip() for line in context.cli_stderr.split('\n') if line.strip()]

    # Find the error message line (usually contains "Error:")
    error_msg = None
    for line in error_lines:
        if 'error' in line.lower():
            error_msg = line
            break

    assert error_msg is not None, f'No error message found in stderr:\n{context.cli_stderr}'
    assert prefix in error_msg, f'Expected error to start with "{prefix}"\nGot: {error_msg}'


@then('the parsed value equals {expected_value:d}')
def step_parsed_value_equals_int(context: Context, expected_value: int) -> None:
    """Verify the parsed integer value."""
    assert f'PORT:{expected_value}' in context.cli_stdout, (
        f'Expected PORT:{expected_value} in output\nstdout: {context.cli_stdout}'
    )


@then('the parsed value is a UUID')
def step_parsed_value_is_uuid(context: Context) -> None:
    """Verify the parsed value is a valid UUID."""
    # Extract UUID from output
    for line in context.cli_stdout.split('\n'):
        if line.startswith('UUID:'):
            uuid_str = line.split(':', 1)[1].strip()
            # Verify it's a valid UUID
            try:
                uuid.UUID(uuid_str)
            except ValueError:
                msg = f'Invalid UUID in output: {uuid_str}'
                raise AssertionError(msg) from None
            return

    msg = f'No UUID found in output:\n{context.cli_stdout}'
    raise AssertionError(msg)


@then('the parsed value is an IPv4Address')
def step_parsed_value_is_ipv4(context: Context) -> None:
    """Verify the parsed value is a valid IPv4 address."""
    for line in context.cli_stdout.split('\n'):
        if line.startswith('IP:'):
            ip_str = line.split(':', 1)[1].strip()
            # Verify it's a valid IPv4 address
            try:
                ipaddress.IPv4Address(ip_str)
            except ValueError:
                msg = f'Invalid IPv4 address in output: {ip_str}'
                raise AssertionError(msg) from None
            return

    msg = f'No IP address found in output:\n{context.cli_stdout}'
    raise AssertionError(msg)


@then('the CLI accepts both inputs')
def step_cli_accepts_both_inputs(context: Context) -> None:
    """Verify that the CLI accepted both inputs (exit code 0)."""
    assert context.cli_exit_code == 0, (
        f'Expected exit code 0 but got {context.cli_exit_code}\n'
        f'stdout: {context.cli_stdout}\n'
        f'stderr: {context.cli_stderr}'
    )


@then('both values are correctly parsed')
def step_both_values_parsed(context: Context) -> None:
    """Verify both email and phone values were parsed."""
    assert 'EMAIL:' in context.cli_stdout, f'No email found in output:\n{context.cli_stdout}'
    assert 'PHONE:' in context.cli_stdout, f'No phone found in output:\n{context.cli_stdout}'


@then('the help text shows type "{type_name}"')
def step_help_shows_type(context: Context, type_name: str) -> None:
    """Verify the help text includes the custom type name."""
    # Typer help output goes to stdout
    assert type_name in context.cli_stdout, (
        f'Expected type name "{type_name}" in help text\nstdout: {context.cli_stdout}'
    )


def _run_cli(context: Context, args: list[str]) -> None:
    """Run the CLI code in a subprocess and capture output.

    Args:
        context: The Behave context
        args: Command-line arguments to pass to the CLI

    """
    # Create a temporary Python file with the CLI code
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(context.cli_code)
        cli_file = f.name

    try:
        # Run the CLI as a subprocess
        result = subprocess.run(  # noqa: S603
            [sys.executable, cli_file, *args],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )

        # Store the results
        context.cli_exit_code = result.returncode
        context.cli_stdout = result.stdout
        context.cli_stderr = result.stderr

    finally:
        # Clean up the temporary file
        Path(cli_file).unlink(missing_ok=True)
