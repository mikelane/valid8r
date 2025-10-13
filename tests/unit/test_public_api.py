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

    def it_exposes_prompt_ask_at_top_level(self) -> None:
        # Scenario: Top-level ask function
        from valid8r import prompt

        assert hasattr(prompt, 'ask')
        assert callable(prompt.ask)
