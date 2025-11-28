from __future__ import annotations

from typing import TYPE_CHECKING

import coverage

if TYPE_CHECKING:
    from behave.model import (  # type: ignore[import-untyped]
        Feature,
        Scenario,
    )
    from behave.runner import Context  # type: ignore[import-untyped]


def before_all(context: Context) -> None:
    """Setup code that runs before all features.

    Starts coverage collection for BDD tests. Coverage data is saved to a
    separate file (.coverage.bdd) so it can be combined with pytest coverage.
    """
    context.cov = coverage.Coverage(
        source=['valid8r'],
        data_file='.coverage.bdd',
    )
    context.cov.start()


def after_all(context: Context) -> None:
    """Cleanup code that runs after all features.

    Stops coverage collection and saves the data file for later combination
    with pytest coverage results.
    """
    if hasattr(context, 'cov'):
        context.cov.stop()
        context.cov.save()


def before_feature(context: Context, feature: Feature) -> None:
    # Setup code that runs before each feature
    pass


def after_feature(context: Context, feature: Feature) -> None:
    # Cleanup code that runs after each feature
    pass


def before_scenario(context: Context, scenario: Scenario) -> None:  # noqa: ARG001
    # Setup code that runs before each scenario
    # Reset the Typer integration context for each scenario
    # to prevent state leakage between scenarios
    if hasattr(context, 'typer_integration_context'):
        delattr(context, 'typer_integration_context')


def after_scenario(context: Context, scenario: Scenario) -> None:
    # Cleanup code that runs after each scenario
    pass
