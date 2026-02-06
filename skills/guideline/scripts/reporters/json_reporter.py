"""
JSON output formatter for validation results.

Provides structured JSON output for programmatic processing.
"""

import json
from typing import List, Dict


def format_json_output(results: List[Dict]) -> str:
    """
    Format validation results as JSON.

    Args:
        results: List of validation results

    Returns:
        JSON string with summary and file details
    """
    total_files = len(results)
    passed = sum(1 for r in results if r["status"] == "passed")
    failed = total_files - passed

    total_errors = 0
    total_warnings = 0

    # Prepare file results (only include failed/error files)
    files = []
    for result in results:
        if result["status"] in ["failed", "error"]:
            issues = result.get("issues", [])
            total_errors += sum(1 for issue in issues if issue["severity"] == "error")
            total_warnings += sum(1 for issue in issues if issue["severity"] == "warning")

            file_data = {
                "path": result["path"],
                "status": result["status"]
            }

            if result["status"] == "error":
                file_data["error"] = result.get("error", "Unknown error")
            else:
                file_data["issues"] = issues

            files.append(file_data)

    output = {
        "summary": {
            "total_files": total_files,
            "passed": passed,
            "failed": failed,
            "total_errors": total_errors,
            "total_warnings": total_warnings
        },
        "files": files
    }

    return json.dumps(output, indent=2)
