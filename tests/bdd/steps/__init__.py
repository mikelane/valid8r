from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from behave.runner import Context  # type: ignore[import-untyped]

    from valid8r.core.maybe import Maybe


class CustomContext:
    def __init__(self) -> None:
        """Initialize the context."""
        self.result: Maybe[Any] | None = None
        self.parsers: dict[type, Callable[[str], Maybe[Any]]] | None = None
        self.custom_parser: Callable[[str], Maybe[Any]] | None = None
        self.custom_enum: Any = None


def get_custom_context(context: Context) -> Context:
    custom_context = getattr(context, 'custom_context', None)
    if custom_context is None:
        custom_context = CustomContext()
        context.custom_context = custom_context
    return context
