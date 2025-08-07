Title: Build parsers/validators from typing annotations (from_type)
Labels: enhancement, typing

Implement `from_type(annotation)` to derive parsers and basic validators for `int`, `float`, `bool`, `str`, `Optional[T]`, `List[T]`, `Set[T]`, `Dict[K,V]`, `Enum`, and `Literal`.

Acceptance Criteria:
```gherkin
Feature: Type-based adapters
  Scenario Outline: Build adapters from annotations
    Given the annotation "<ann>"
    When I call from_type(annotation)
    Then it returns a callable that accepts valid inputs and rejects invalid ones
    Examples:
      | ann            |
      | int            |
      | Optional[int]  |
      | list[int]      |
      | dict[str,int]  |
      | MyEnum         |
      | Literal["a","b"] |
```