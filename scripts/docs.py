"""Scripts for building and serving documentation."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

DOCS_DIR = Path(__file__).parent.parent / 'docs'
BUILD_DIR = DOCS_DIR / '_build' / 'html'


def build() -> None:
    """Build the Sphinx documentation."""
    print('Building documentation...')
    os.chdir(DOCS_DIR)
    result = subprocess.run(  # noqa: S603
        [sys.executable, '-m', 'sphinx.cmd.build', '-b', 'html', '.', '_build/html'],
        check=False,
    )
    if result.returncode != 0:
        sys.exit(result.returncode)
    print(f'Documentation built successfully. Files in {BUILD_DIR}')


def serve() -> None:
    """Serve the built documentation using Python's HTTP server."""
    if not BUILD_DIR.exists():
        print("Documentation hasn't been built yet. Building now...")
        build()

    os.chdir(BUILD_DIR)
    print('Starting documentation server...')
    print('Visit http://localhost:8000 to view the documentation')
    print('Press Ctrl+C to stop the server')

    # Run the HTTP server
    subprocess.run([sys.executable, '-m', 'http.server'], check=False)  # noqa: S603


if __name__ == '__main__':
    # If running directly, build and serve
    build()
    serve()
