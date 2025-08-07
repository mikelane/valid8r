from __future__ import annotations


def test_import_core_modules_from_top_level() -> None:
    # Feature: Public API re-exports
    # Scenario: Import core modules from top-level
    from valid8r import parsers, validators, prompt

    assert parsers is not None
    assert validators is not None
    assert prompt is not None


def test_import_maybe_from_top_level() -> None:
    # Scenario: Import Maybe types from top-level
    from valid8r import Maybe
    from valid8r.core.maybe import Maybe as CoreMaybe

    assert Maybe is CoreMaybe


def test_top_level_prompt_ask_callable() -> None:
    # Scenario: Top-level ask function
    from valid8r import prompt

    assert hasattr(prompt, 'ask')
    assert callable(prompt.ask)