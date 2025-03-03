from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from behave.model import (  # type: ignore[import-untyped]
        Feature,
        Scenario,
    )
    from behave.runner import Context  # type: ignore[import-untyped]


def before_all(context: Context) -> None:
    # Setup code that runs before all features
    pass


def after_all(context: Context) -> None:
    # Cleanup code that runs after all features
    pass


def before_feature(context: Context, feature: Feature) -> None:
    # Setup code that runs before each feature
    pass


def after_feature(context: Context, feature: Feature) -> None:
    # Cleanup code that runs after each feature
    pass


def before_scenario(context: Context, scenario: Scenario) -> None:
    # Setup code that runs before each scenario
    pass


def after_scenario(context: Context, scenario: Scenario) -> None:
    # Cleanup code that runs after each scenario
    pass
