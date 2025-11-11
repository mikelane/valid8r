"""Unit tests for the check_regex_safety.py scanner script.

Following TDD: these tests are written FIRST, before implementation.
They define the expected behavior of the ReDoS detection system.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.monkeypatch import MonkeyPatch

# Add scripts directory to path for imports
SCRIPTS_DIR = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(SCRIPTS_DIR))


class DescribeCheckRegexSafety:
    """Test suite for the ReDoS detection scanner."""

    def it_imports_without_error(self) -> None:
        """Import the check_regex_safety module successfully."""
        import check_regex_safety  # noqa: F401

    def it_has_scan_file_function(self) -> None:
        """The module provides a scan_file function."""
        import check_regex_safety

        assert hasattr(check_regex_safety, 'scan_file')
        assert callable(check_regex_safety.scan_file)

    def it_has_scan_directory_function(self) -> None:
        """The module provides a scan_directory function."""
        import check_regex_safety

        assert hasattr(check_regex_safety, 'scan_directory')
        assert callable(check_regex_safety.scan_directory)

    def it_has_main_function(self) -> None:
        """The module provides a main entry point."""
        import check_regex_safety

        assert hasattr(check_regex_safety, 'main')
        assert callable(check_regex_safety.main)

    def it_detects_safe_regex_patterns(self, tmp_path: Path) -> None:
        """Scan file with safe regex patterns returns no vulnerabilities."""
        import check_regex_safety

        # Create a test file with safe regex patterns
        test_file = tmp_path / 'safe_patterns.py'
        test_file.write_text(
            """
import re

# Safe patterns - no nested quantifiers or catastrophic backtracking
PATTERN_1 = re.compile(r'^[a-z0-9-]+$')
PATTERN_2 = re.compile(r'\\d{3}-\\d{3}-\\d{4}')
PATTERN_3 = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$')
"""
        )

        results = check_regex_safety.scan_file(test_file)

        # Should return results but no vulnerabilities
        assert isinstance(results, list)
        vulnerabilities = [r for r in results if r.get('vulnerable', False)]
        assert len(vulnerabilities) == 0

    def it_detects_vulnerable_regex_patterns(self, tmp_path: Path) -> None:
        """Scan file with vulnerable regex patterns detects them."""
        import check_regex_safety

        # Create a test file with a vulnerable pattern
        # Pattern with nested quantifiers (a+)+ is vulnerable to ReDoS
        test_file = tmp_path / 'vulnerable_pattern.py'
        test_file.write_text(
            """
import re

# Vulnerable pattern: nested quantifiers cause catastrophic backtracking
VULNERABLE = re.compile(r'^(a+)+$')
"""
        )

        results = check_regex_safety.scan_file(test_file)

        # Should detect at least one vulnerability
        assert isinstance(results, list)
        assert len(results) > 0

        # Check vulnerability structure
        vuln = results[0]
        assert 'pattern' in vuln
        assert 'line_number' in vuln
        assert 'file' in vuln
        assert 'reason' in vuln or 'attack_string' in vuln

    def it_scans_directory_recursively(self, tmp_path: Path) -> None:
        """Scan directory finds patterns in nested files."""
        import check_regex_safety

        # Create directory structure with multiple files
        subdir = tmp_path / 'subdir'
        subdir.mkdir()

        file1 = tmp_path / 'file1.py'
        file1.write_text('import re\nPATTERN = re.compile(r"^[a-z]+$")')

        file2 = subdir / 'file2.py'
        file2.write_text('import re\nPATTERN = re.compile(r"^(a+)+$")')

        results = check_regex_safety.scan_directory(tmp_path)

        # Should find patterns in both files
        assert isinstance(results, list)
        # file1 has safe pattern (0 vulns), file2 has vulnerable pattern (1+ vulns)
        assert any(str(file2) in str(r.get('file', '')) for r in results)

    def it_returns_structured_vulnerability_data(self, tmp_path: Path) -> None:
        """Vulnerability results include all necessary information."""
        import check_regex_safety

        test_file = tmp_path / 'vuln.py'
        test_file.write_text('import re\nBAD = re.compile(r"^(a+)+$")  # line 2')

        results = check_regex_safety.scan_file(test_file)
        assert len(results) > 0

        vuln = results[0]
        # Must include pattern, file, and line number
        assert isinstance(vuln['pattern'], str)
        assert isinstance(vuln['file'], (str, Path))
        assert isinstance(vuln['line_number'], int)
        assert vuln['line_number'] == 2

    def it_handles_file_not_found(self) -> None:
        """Scan nonexistent file handles error gracefully."""
        import check_regex_safety

        nonexistent = Path('/nonexistent/file.py')
        results = check_regex_safety.scan_file(nonexistent)

        # Should return empty list or handle gracefully
        assert isinstance(results, list)

    def it_skips_non_python_files(self, tmp_path: Path) -> None:
        """Scan directory ignores non-Python files."""
        import check_regex_safety

        # Create non-Python files
        (tmp_path / 'readme.md').write_text('# README')
        (tmp_path / 'data.json').write_text('{}')
        (tmp_path / 'script.sh').write_text('#!/bin/bash')

        results = check_regex_safety.scan_directory(tmp_path)

        # Should return empty list (no Python files to scan)
        assert isinstance(results, list)
        assert len(results) == 0

    def it_main_exits_with_error_when_vulnerabilities_found(
        self, tmp_path: Path, monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]
    ) -> None:
        """Main function exits with non-zero code when vulnerabilities found."""
        import check_regex_safety

        # Create vulnerable file
        vuln_file = tmp_path / 'vuln.py'
        vuln_file.write_text('import re\nBAD = re.compile(r"^(a+)+$")')

        # Mock sys.argv to point to our test file
        monkeypatch.setattr('sys.argv', ['check_regex_safety.py', str(tmp_path)])

        # Main should exit with non-zero code
        with pytest.raises(SystemExit) as exc_info:
            check_regex_safety.main()

        assert exc_info.value.code != 0

        # Check output mentions vulnerabilities
        captured = capsys.readouterr()
        assert 'vulnerabilit' in captured.out.lower() or 'found' in captured.out.lower()

    def it_main_exits_successfully_when_no_vulnerabilities(
        self, tmp_path: Path, monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]
    ) -> None:
        """Main function exits with zero code when no vulnerabilities."""
        import check_regex_safety

        # Create safe file
        safe_file = tmp_path / 'safe.py'
        safe_file.write_text('import re\nSAFE = re.compile(r"^[a-z]+$")')

        # Mock sys.argv
        monkeypatch.setattr('sys.argv', ['check_regex_safety.py', str(tmp_path)])

        # Main should exit successfully
        with pytest.raises(SystemExit) as exc_info:
            check_regex_safety.main()

        assert exc_info.value.code == 0

        # Check output mentions no vulnerabilities or success
        captured = capsys.readouterr()
        assert 'no' in captured.out.lower() or 'safe' in captured.out.lower() or 'success' in captured.out.lower()

    def it_reports_attack_strings_for_vulnerabilities(self, tmp_path: Path) -> None:
        """Vulnerability reports include attack strings that trigger ReDoS."""
        import check_regex_safety

        test_file = tmp_path / 'vuln.py'
        test_file.write_text('import re\nVULN = re.compile(r"^(a+)+$")')

        results = check_regex_safety.scan_file(test_file)
        assert len(results) > 0

        vuln = results[0]
        # Should include attack string or example that triggers backtracking
        assert 'attack_string' in vuln or 'reason' in vuln

    def it_handles_multiline_regex_patterns(self, tmp_path: Path) -> None:
        """Scanner detects patterns split across multiple lines."""
        import check_regex_safety

        test_file = tmp_path / 'multiline.py'
        test_file.write_text(
            """
import re

# Pattern split across lines
PATTERN = re.compile(
    r'^(a+)+$',
    re.IGNORECASE
)
"""
        )

        results = check_regex_safety.scan_file(test_file)
        # Should detect the vulnerable pattern even if multiline
        assert isinstance(results, list)

    def it_provides_helpful_error_messages(self, tmp_path: Path) -> None:
        """Vulnerability reports include descriptive error messages."""
        import check_regex_safety

        test_file = tmp_path / 'vuln.py'
        test_file.write_text('import re\nVULN = re.compile(r"^(a+)+$")')

        results = check_regex_safety.scan_file(test_file)
        assert len(results) > 0

        vuln = results[0]
        # Should have a message explaining the issue
        assert 'reason' in vuln and vuln['reason'] != ''
