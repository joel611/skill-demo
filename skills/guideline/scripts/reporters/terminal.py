"""
Terminal (console) output formatter for validation results.

Provides colored output using colorama for cross-platform compatibility.
"""

from typing import List, Dict
from colorama import Fore, Style


def format_console_output(results: List[Dict], base_path: str) -> str:
    """
    Format validation results as colored console output.

    Args:
        results: List of validation results
        base_path: Base path being validated

    Returns:
        Formatted string for console output
    """
    output = []
    output.append(f"\nValidating HTML files in: {base_path}\n")

    total_errors = 0
    total_warnings = 0
    passed_count = 0
    failed_count = 0

    for result in results:
        status = result["status"]
        path = result["path"]
        issues = result.get("issues", [])

        # Count errors and warnings
        file_errors = sum(1 for issue in issues if issue["severity"] == "error")
        file_warnings = sum(1 for issue in issues if issue["severity"] == "warning")
        total_errors += file_errors
        total_warnings += file_warnings

        if status == "passed":
            passed_count += 1
            output.append(f"{Fore.GREEN}✓{Style.RESET_ALL} {path}")
            output.append(f"  {Fore.GREEN}✓{Style.RESET_ALL} All validations passed")
        elif status == "error":
            failed_count += 1
            output.append(f"{Fore.RED}✗{Style.RESET_ALL} {path}")
            error_msg = result.get("error", "Unknown error")
            output.append(f"  {Fore.RED}✗{Style.RESET_ALL} {error_msg}")
        else:  # failed
            failed_count += 1
            output.append(f"{Fore.RED}✗{Style.RESET_ALL} {path}")
            for issue in issues:
                severity = issue["severity"]
                message = issue["message"]
                line = issue.get("line")
                rule = issue["rule"]

                if severity == "error":
                    symbol = f"{Fore.RED}✗{Style.RESET_ALL}"
                else:
                    symbol = f"{Fore.YELLOW}⚠{Style.RESET_ALL}"

                if line:
                    output.append(f"  {symbol} [Line {line}] {message} ({rule})")
                else:
                    output.append(f"  {symbol} {message} ({rule})")

        output.append("")  # Empty line between files

    # Summary
    output.append(f"Summary: {Fore.GREEN}{passed_count} passed{Style.RESET_ALL}, "
                  f"{Fore.RED}{failed_count} failed{Style.RESET_ALL} "
                  f"({Fore.RED}{total_errors} errors{Style.RESET_ALL}, "
                  f"{Fore.YELLOW}{total_warnings} warnings{Style.RESET_ALL})\n")

    return "\n".join(output)
