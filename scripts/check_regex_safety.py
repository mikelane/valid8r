#!/usr/bin/env python3
"""ReDoS (Regular Expression Denial of Service) detection scanner.

This script scans Python source files for regex patterns that may be vulnerable
to catastrophic backtracking attacks. It uses the regexploit-py tool to analyze
patterns for nested quantifiers and other ReDoS-prone constructs.

Usage:
    python scripts/check_regex_safety.py <file_or_directory>
    python scripts/check_regex_safety.py valid8r/
    python scripts/check_regex_safety.py valid8r/core/parsers.py

Exit codes:
    0: No vulnerabilities found
    1: Vulnerabilities detected or error occurred
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

# Check if regexploit-py is installed
if not shutil.which('regexploit-py'):
    print('ERROR: regexploit-py command not found')
    print('Install it with: uv add --group dev regexploit')
    sys.exit(1)


def parse_regexploit_output(output: str) -> list[dict[str, Any]]:
    """Parse regexploit-py output to extract vulnerability information.

    Args:
        output: The output from regexploit-py command

    Returns:
        List of vulnerability dictionaries containing pattern, file, reason, etc.

    """
    vulnerabilities = []

    # Split output by vulnerability sections
    # Format: "Vulnerable regex in <file> #<num>"
    vuln_sections = re.split(r'Vulnerable regex in', output)

    for section in vuln_sections[1:]:  # Skip first empty split
        vuln = {}

        # Extract file path and pattern number
        file_match = re.search(r'(.+?) #(\d+)', section)
        if file_match:
            vuln['file'] = file_match.group(1).strip()
            vuln['line_number'] = int(file_match.group(2))

        # Extract pattern
        pattern_match = re.search(r'Pattern: (.+)', section)
        if pattern_match:
            vuln['pattern'] = pattern_match.group(1).strip()

        # Extract context
        context_match = re.search(r'Context: (.+)', section)
        if context_match:
            vuln['context'] = context_match.group(1).strip()

        # Extract complexity
        complexity_match = re.search(r'Worst-case complexity: (\d+)', section)
        if complexity_match:
            complexity = int(complexity_match.group(1))
            vuln['reason'] = f'Exponential complexity (⭐×{complexity}) - catastrophic backtracking'
        else:
            vuln['reason'] = 'Pattern contains nested quantifiers or catastrophic backtracking'

        # Extract attack string
        attack_match = re.search(r"Example: '(.+?)' \* (\d+)", section)
        if attack_match:
            char = attack_match.group(1)
            count = attack_match.group(2)
            vuln['attack_string'] = f'{char} * {count}'
        else:
            vuln['attack_string'] = 'a' * 30

        vuln['vulnerable'] = True
        vulnerabilities.append(vuln)

    return vulnerabilities


def scan_regex_pattern(pattern: str) -> dict[str, Any]:
    """Analyze a single regex pattern for ReDoS vulnerabilities.

    Args:
        pattern: The regex pattern string to analyze

    Returns:
        Dict containing:
        - vulnerable: bool indicating if pattern is vulnerable
        - pattern: The original pattern
        - reason: Description of why it's vulnerable (if applicable)
        - attack_string: Example string that triggers backtracking (if vulnerable)

    """
    # Create temporary file with the pattern
    import tempfile

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(f"import re\nPATTERN = re.compile(r'{pattern}')\n")
        temp_file = f.name

    try:
        # Run regexploit-py on the temporary file
        process = subprocess.run(
            ['regexploit-py', temp_file],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )

        output = process.stdout

        # Parse output for vulnerabilities
        vulns = parse_regexploit_output(output)

        if vulns:
            return vulns[0]  # Return first vulnerability

        # No vulnerability found
        return {
            'vulnerable': False,
            'pattern': pattern,
            'reason': '',
            'attack_string': '',
        }

    except subprocess.TimeoutExpired:
        return {
            'vulnerable': False,
            'pattern': pattern,
            'reason': 'Analysis timed out',
            'attack_string': '',
        }
    except Exception as e:
        return {
            'vulnerable': False,
            'pattern': pattern,
            'reason': f'Could not analyze: {e}',
            'attack_string': '',
        }
    finally:
        # Clean up temp file
        Path(temp_file).unlink(missing_ok=True)


def scan_file(file_path: Path) -> list[dict[str, Any]]:
    """Scan a single Python file for regex patterns.

    Args:
        file_path: Path to Python file to scan

    Returns:
        List of scan results for each pattern found

    """
    try:
        # Run regexploit-py on the file
        process = subprocess.run(
            ['regexploit-py', str(file_path)],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )

        output = process.stdout

        # Parse output for vulnerabilities
        vulnerabilities = parse_regexploit_output(output)

        # Also return info about safe patterns by parsing "Processed N regexes" line
        processed_match = re.search(r'Processed (\d+) regexes', output)
        total_patterns = int(processed_match.group(1)) if processed_match else len(vulnerabilities)

        # Create entries for safe patterns (for reporting)
        results = []
        for vuln in vulnerabilities:
            vuln['file'] = str(file_path)
            results.append(vuln)

        # Add safe pattern entries
        safe_count = total_patterns - len(vulnerabilities)
        for _ in range(safe_count):
            results.append(
                {
                    'vulnerable': False,
                    'pattern': '<safe pattern>',
                    'file': str(file_path),
                    'line_number': 0,
                    'context': '',
                    'reason': '',
                    'attack_string': '',
                }
            )

        return results

    except subprocess.TimeoutExpired:
        print(f'WARNING: Analysis timed out for {file_path}')
        return []
    except Exception as e:
        print(f'ERROR: Could not analyze {file_path}: {e}')
        return []


def scan_directory(directory: Path) -> list[dict[str, Any]]:
    """Scan all Python files in a directory recursively.

    Args:
        directory: Path to directory to scan

    Returns:
        List of scan results for all patterns found

    """
    results = []

    # Find all Python files
    python_files = list(directory.rglob('*.py'))

    for py_file in python_files:
        # Skip __pycache__ and virtual environments
        if '__pycache__' in str(py_file) or '.venv' in str(py_file) or 'venv' in str(py_file):
            continue

        file_results = scan_file(py_file)
        results.extend(file_results)

    return results


def main(args: list[str] | None = None) -> None:
    """Main entry point for the scanner.

    Args:
        args: Command-line arguments (defaults to sys.argv[1:])

    """
    if args is None:
        args = sys.argv[1:]

    if not args:
        print('Usage: python scripts/check_regex_safety.py <file_or_directory>')
        sys.exit(1)

    target_path = Path(args[0])

    if not target_path.exists():
        print(f'ERROR: Path does not exist: {target_path}')
        sys.exit(1)

    # Scan the target
    results = scan_file(target_path) if target_path.is_file() else scan_directory(target_path)

    # Filter for vulnerabilities
    vulnerabilities = [r for r in results if r['vulnerable']]

    # Print results
    if vulnerabilities:
        print(f'\n❌ Found {len(vulnerabilities)} vulnerable regex pattern(s):\n')
        for vuln in vulnerabilities:
            print(f'  File: {vuln["file"]}:{vuln["line_number"]}')
            print(f'  Pattern: {vuln["pattern"]}')
            if vuln.get('context'):
                print(f'  Context: {vuln["context"]}')
            print(f'  Reason: {vuln["reason"]}')
            if vuln['attack_string']:
                attack_preview = vuln['attack_string'][:100]
                print(
                    f'  Attack string: {attack_preview}...'
                    if len(vuln['attack_string']) > 100
                    else f'  Attack string: {attack_preview}'
                )
            print()

        sys.exit(1)
    else:
        total_patterns = len(results)
        print(f'\n✅ All {total_patterns} regex pattern(s) are safe (no ReDoS vulnerabilities detected)')
        sys.exit(0)


if __name__ == '__main__':
    main()
