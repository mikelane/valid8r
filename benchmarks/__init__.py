"""Performance benchmarks for valid8r compared to competitor libraries.

This package contains benchmark scenarios comparing valid8r against:
- Pydantic (Rust-powered validation)
- marshmallow (schema-based validation)
- cerberus (lightweight validation)

All benchmarks use pytest-benchmark for consistent, reproducible measurements.
"""

from __future__ import annotations

__all__ = ['scenarios']
