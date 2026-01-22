from __future__ import annotations


class DescribePublicApi:
    def it_imports_core_modules_from_top_level(self) -> None:
        # Feature: Public API re-exports
        # Scenario: Import core modules from top-level
        from valid8r import (
            parsers,
            prompt,
            validators,
        )

        assert parsers is not None
        assert validators is not None
        assert prompt is not None

    def it_imports_maybe_from_top_level(self) -> None:
        # Scenario: Import Maybe types from top-level
        from valid8r import Maybe
        from valid8r.core.maybe import Maybe as CoreMaybe

        assert Maybe is CoreMaybe

    def it_imports_success_from_top_level(self) -> None:
        # Scenario: Import Success from top-level for pattern matching
        from valid8r import Success
        from valid8r.core.maybe import Success as CoreSuccess

        assert Success is CoreSuccess

    def it_imports_failure_from_top_level(self) -> None:
        # Scenario: Import Failure from top-level for pattern matching
        from valid8r import Failure
        from valid8r.core.maybe import Failure as CoreFailure

        assert Failure is CoreFailure

    def it_enables_pattern_matching_with_top_level_imports(self) -> None:
        # Scenario: Pattern matching works with top-level Success/Failure imports
        from valid8r import (
            Failure,
            Maybe,
            Success,
        )

        success_result: Maybe[int] = Success(42)
        failure_result: Maybe[int] = Failure('error')

        # Verify pattern matching works
        match success_result:
            case Success(value):
                assert value == 42
            case Failure(_):
                raise AssertionError('Expected Success')

        match failure_result:
            case Success(_):
                raise AssertionError('Expected Failure')
            case Failure(error):
                assert error == 'error'

    def it_includes_success_and_failure_in_all(self) -> None:
        # Scenario: __all__ includes Success and Failure
        import valid8r

        assert 'Success' in valid8r.__all__
        assert 'Failure' in valid8r.__all__

    def it_exposes_prompt_ask_at_top_level(self) -> None:
        # Scenario: Top-level ask function
        from valid8r import prompt

        assert hasattr(prompt, 'ask')
        assert callable(prompt.ask)
