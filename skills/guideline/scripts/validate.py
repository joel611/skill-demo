# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "beautifulsoup4",
#     "colorama",
# ]
# ///

#!/usr/bin/env python3
"""
Recursively finds HTML files and validates them against required patterns.
Supports multiple output formats: terminal (default), JSON, and HTML.
"""

import os
import sys
import json
import re
import argparse
from typing import List, Dict, Callable, Tuple, Optional
from bs4 import BeautifulSoup
from colorama import Fore, Style, init
from common.utils import detect_promo_path
from rules import get_all_rules
from reporters import format_console_output, format_json_output

# Initialize colorama for cross-platform colored output
init(autoreset=True)


def find_html_files(base_path: str) -> List[str]:
    """
    Find all HTML files recursively in base_path.

    Args:
        base_path: Directory to search for HTML files

    Returns:
        List of absolute paths to HTML files
    """
    html_files = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    return html_files

def validate_file(file_path: str) -> Dict:
    """
    Validate a single HTML file against all registered rules.

    Args:
        file_path: Path to the HTML file

    Returns:
        Dictionary with validation results:
        {
            "path": str,
            "status": "passed" | "failed" | "error",
            "issues": List[Dict],
            "error": str (only if parsing failed)
        }
    """
    result = {
        "path": file_path,
        "status": "passed",
        "issues": []
    }

    try:
        # Read raw HTML lines for line number tracking
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_html = f.read()
            raw_lines = raw_html.split('\n')

        # Parse with html.parser to preserve line numbers for all elements
        soup = BeautifulSoup(raw_html, 'html.parser')

        # Run all validation rules
        for rule_id, description, rule_func in get_all_rules():
            issues = rule_func(soup, file_path, raw_lines)
            result["issues"].extend(issues)

        # Determine status
        if result["issues"]:
            result["status"] = "failed"

    except FileNotFoundError:
        result["status"] = "error"
        result["error"] = f"File not found: {file_path}"
    except UnicodeDecodeError as e:
        result["status"] = "error"
        result["error"] = f"Encoding error: {str(e)}"
    except Exception as e:
        result["status"] = "error"
        result["error"] = f"Parsing error: {str(e)}"

    return result


def validate_files(file_paths: List[str]) -> List[Dict]:
    """
    Validate multiple HTML files.

    Args:
        file_paths: List of paths to HTML files

    Returns:
        List of validation results for each file
    """
    results = []
    for file_path in file_paths:
        result = validate_file(file_path)
        results.append(result)
    return results





def main():
    """
    Main entry point for the HTML validator.
    """
    parser = argparse.ArgumentParser(
        description="HTML Validator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/validate.py                              # Auto-detect d##/k##, terminal output
  python scripts/validate.py --format json                # JSON output
  python scripts/validate.py --format html                # HTML report
  python scripts/validate.py --json                       # JSON (deprecated, use --format json)
        """
    )

    parser.add_argument(
        '--path',
        type=str,
        default=None,
        help='Path to search for d##/k## pattern (default: current directory)'
    )

    parser.add_argument(
        '--format',
        type=str,
        choices=['terminal', 'json', 'html'],
        default='terminal',
        help='Output format (default: terminal)'
    )

    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON (deprecated: use --format json)'
    )

    args = parser.parse_args()

    # Determine search path
    search_path = args.path if args.path is not None else "."

    # Check if search path exists
    if not os.path.exists(search_path):
        print(f"Error: Path does not exist: {search_path}", file=sys.stderr)
        sys.exit(1)

    # Try to auto-detect pattern within the search path
    detected_path = detect_promo_path(search_path)

    if detected_path is None:
        # If no pattern found and user didn't specify a path, show error
        if args.path is None:
            print("Error: Could not find directory matching pattern.", file=sys.stderr)
            print("Please specify a path using --path argument.", file=sys.stderr)
            sys.exit(1)
        # If user specified a path but no pattern found, use their path as-is
        # (backward compatibility for explicit full paths)
        args.path = search_path
    else:
        # Use the detected path
        args.path = detected_path

    # Find HTML files
    html_files = find_html_files(args.path)

    if not html_files:
        print(f"No HTML files found in: {args.path}", file=sys.stderr)
        sys.exit(0)

    # Validate files
    results = validate_files(html_files)

    # Determine output format (handle deprecated --json flag)
    output_format = 'json' if args.json else args.format

    # Output results
    if output_format == 'json':
        print(format_json_output(results))
    elif output_format == 'html':
        from reporters import format_html_output, save_html_report
        from rules import get_all_rules
        html_content = format_html_output(results, args.path, get_all_rules())
        filename = save_html_report(html_content)
        print(f"Report saved to: {filename}")
    else:  # terminal
        print(format_console_output(results, args.path))

    # Determine exit code
    has_failures = any(r["status"] in ["failed", "error"] for r in results)
    sys.exit(1 if has_failures else 0)


if __name__ == "__main__":
    main()

