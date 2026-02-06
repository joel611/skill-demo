"""
Output formatters for validation results.

This module provides different output formats for validation reports:
- terminal: Colored console output (default)
- json: JSON format for programmatic processing
- html: HTML report with code snippets and visual formatting
"""

from .terminal import format_console_output
from .json_reporter import format_json_output
from .html_reporter import format_html_output, save_html_report

__all__ = [
    'format_console_output',
    'format_json_output',
    'format_html_output',
    'save_html_report'
]
