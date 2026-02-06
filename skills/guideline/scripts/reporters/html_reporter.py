"""
HTML output formatter for validation results.

Generates aggregate HTML reports with code snippets and visual formatting.
"""

from typing import List, Dict, Tuple
from datetime import datetime
import html


def extract_code_snippet(file_path: str, line_num: int, context: int = 5) -> List[Tuple[int, str]]:
    """
    Extract lines around target line with line numbers.

    Args:
        file_path: Path to source file
        line_num: Target line number (1-indexed)
        context: Number of lines before/after to include

    Returns:
        List of (line_number, line_content) tuples
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Calculate range (handle edge cases)
        total_lines = len(lines)
        start_line = max(1, line_num - context)
        end_line = min(total_lines, line_num + context)

        # Extract snippet with line numbers
        snippet = []
        for i in range(start_line - 1, end_line):  # -1 for 0-indexed list
            snippet.append((i + 1, lines[i].rstrip('\n')))

        return snippet

    except (FileNotFoundError, UnicodeDecodeError, IOError):
        # Return empty snippet on error
        return []


def format_code_snippet_html(snippet: List[Tuple[int, str]], error_line: int, severity: str) -> str:
    """
    Format code snippet as HTML with highlighting.

    Args:
        snippet: List of (line_number, line_content) tuples
        error_line: Line number to highlight
        severity: 'error' or 'warning'

    Returns:
        HTML string with formatted code snippet
    """
    if not snippet:
        return ""

    # Choose marker based on severity
    marker = "❌" if severity == "error" else "⚠"

    lines_html = []
    for line_num, line_content in snippet:
        # Escape HTML special characters
        escaped_content = html.escape(line_content)

        # Highlight error line
        if line_num == error_line:
            line_class = f'error-line {severity}-line'
            lines_html.append(
                f'<div class="{line_class}">'
                f'<span class="line-marker">{marker}</span>'
                f'<span class="line-number">{line_num}</span>'
                f'<span class="line-content">{escaped_content}</span>'
                f'</div>'
            )
        else:
            lines_html.append(
                f'<div class="code-line">'
                f'<span class="line-number">{line_num}</span>'
                f'<span class="line-content">{escaped_content}</span>'
                f'</div>'
            )

    return '\n'.join(lines_html)


def group_issues_by_rule(results: List[Dict], all_rules: List[Tuple]) -> Dict[str, Dict]:
    """
    Group validation results by rule for aggregate view.

    Args:
        results: List of validation results from validate_files()
        all_rules: All registered rules from get_all_rules()

    Returns:
        Dictionary mapping rule_id to:
        {
            'description': str,
            'total_files': int,
            'passed_files': int,
            'failed_files': int,
            'failures': [
                {
                    'file_path': str,
                    'issues': [issue_dict, ...]
                },
                ...
            ]
        }
    """
    # Initialize structure for all rules
    grouped = {}
    for rule_id, description, _ in all_rules:
        grouped[rule_id] = {
            'description': description,
            'total_files': len(results),
            'passed_files': 0,
            'failed_files': 0,
            'failures': []
        }

    # Track which files failed which rules
    files_by_rule = {rule_id: set() for rule_id, _, _ in all_rules}

    # Group issues by rule and file
    for result in results:
        if result["status"] == "failed":
            issues = result.get("issues", [])

            # Group issues by rule for this file
            file_issues_by_rule = {}
            for issue in issues:
                rule_id = issue["rule"]
                if rule_id not in file_issues_by_rule:
                    file_issues_by_rule[rule_id] = []
                file_issues_by_rule[rule_id].append(issue)

            # Add to grouped structure
            for rule_id, rule_issues in file_issues_by_rule.items():
                if rule_id in grouped:
                    grouped[rule_id]['failures'].append({
                        'file_path': result["path"],
                        'issues': rule_issues
                    })
                    files_by_rule[rule_id].add(result["path"])

    # Calculate pass/fail counts
    for rule_id in grouped:
        failed_count = len(files_by_rule[rule_id])
        grouped[rule_id]['failed_files'] = failed_count
        grouped[rule_id]['passed_files'] = grouped[rule_id]['total_files'] - failed_count

    return grouped


def format_html_output(results: List[Dict], base_path: str, all_rules: List[Tuple]) -> str:
    """
    Format validation results as HTML report.

    Args:
        results: List of validation results
        base_path: Base path being validated
        all_rules: All registered validation rules

    Returns:
        Complete HTML document as string
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Calculate summary statistics
    total_files = len(results)
    passed_files = sum(1 for r in results if r["status"] == "passed")
    failed_files = total_files - passed_files

    total_errors = 0
    total_warnings = 0
    for result in results:
        if result["status"] == "failed":
            issues = result.get("issues", [])
            total_errors += sum(1 for i in issues if i["severity"] == "error")
            total_warnings += sum(1 for i in issues if i["severity"] == "warning")

    # Group issues by rule
    grouped = group_issues_by_rule(results, all_rules)

    # Count rules passed/failed
    rules_passed = sum(1 for r in grouped.values() if r['failed_files'] == 0)
    rules_failed = len(grouped) - rules_passed

    # Generate HTML
    html_parts = []
    html_parts.append(_generate_html_header())
    html_parts.append(_generate_html_summary(
        timestamp, base_path, total_files, rules_passed, rules_failed, total_errors, total_warnings
    ))
    html_parts.append(_generate_html_rules(grouped))
    html_parts.append(_generate_html_footer())

    return '\n'.join(html_parts)


def _generate_html_header() -> str:
    """Generate HTML document header with CSS."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Validation Report</title>
    <style>
        :root {
            --color-success: #34A344;
            --color-error: #DC3545;
            --color-warning: #FFC107;
            --color-bg: #F8F9FA;
            --color-border: #DEE2E6;
            --color-code-bg: #F5F5F5;
            --color-text: #212529;
            --color-muted: #6C757D;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--color-bg);
            color: var(--color-text);
            line-height: 1.6;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 30px;
            margin-bottom: 20px;
        }

        /* Header */
        .report-header {
            border-bottom: 2px solid var(--color-border);
            padding-bottom: 20px;
            margin-bottom: 30px;
        }

        .report-header h1 {
            font-size: 28px;
            margin-bottom: 10px;
        }

        .timestamp, .path {
            color: var(--color-muted);
            font-size: 14px;
        }

        /* Summary Grid */
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .summary-card {
            background: var(--color-bg);
            border-left: 4px solid var(--color-muted);
            padding: 20px;
            border-radius: 4px;
        }

        .summary-card.success {
            border-left-color: var(--color-success);
        }

        .summary-card.error {
            border-left-color: var(--color-error);
        }

        .summary-card.warning {
            border-left-color: var(--color-warning);
        }

        .summary-value {
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .summary-label {
            color: var(--color-muted);
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* Rules Section */
        h2 {
            font-size: 24px;
            margin-bottom: 20px;
        }

        .rule-section {
            margin-bottom: 15px;
            border: 1px solid var(--color-border);
            border-radius: 4px;
            overflow: hidden;
        }

        .rule-header {
            padding: 15px 20px;
            background: var(--color-bg);
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 10px;
            transition: background 0.2s;
        }

        .rule-header:hover {
            background: #E9ECEF;
        }

        .rule-section.passed .rule-header {
            background: #E8F5E9;
        }

        .rule-section.failed .rule-header {
            background: #FFEBEE;
        }

        .rule-status {
            font-size: 20px;
            min-width: 24px;
        }

        .rule-section.passed .rule-status {
            color: var(--color-success);
        }

        .rule-section.failed .rule-status {
            color: var(--color-error);
        }

        .rule-title {
            font-weight: 600;
            font-family: monospace;
        }

        .rule-description {
            flex: 1;
            color: var(--color-muted);
        }

        .rule-stats {
            font-size: 14px;
            color: var(--color-muted);
        }

        .rule-details {
            padding: 20px;
            background: white;
        }

        .rule-section.passed .rule-details {
            display: none;
        }

        /* File Failures */
        .file-failures {
            margin-bottom: 25px;
        }

        .file-failures h4 {
            font-size: 16px;
            margin-bottom: 15px;
            color: var(--color-muted);
            font-family: monospace;
        }

        /* Issue Blocks */
        .issue-block {
            margin-bottom: 20px;
            border: 1px solid var(--color-border);
            border-radius: 4px;
            overflow: hidden;
        }

        .issue-block.error {
            border-left: 4px solid var(--color-error);
        }

        .issue-block.warning {
            border-left: 4px solid var(--color-warning);
        }

        .issue-header {
            padding: 12px 15px;
            background: var(--color-bg);
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .issue-severity {
            font-weight: 600;
            font-size: 12px;
            padding: 4px 8px;
            border-radius: 3px;
        }

        .issue-block.error .issue-severity {
            background: var(--color-error);
            color: white;
        }

        .issue-block.warning .issue-severity {
            background: var(--color-warning);
            color: #333;
        }

        .issue-message {
            flex: 1;
        }

        .issue-line {
            font-size: 14px;
            color: var(--color-muted);
            font-family: monospace;
        }

        /* Code Snippets */
        .code-snippet {
            background: var(--color-code-bg);
            padding: 15px;
            overflow-x: auto;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.5;
        }

        .code-line, .error-line, .warning-line {
            display: flex;
            align-items: center;
            padding: 2px 0;
        }

        .error-line {
            background: #FFEBEE;
        }

        .warning-line {
            background: #FFF9E6;
        }

        .line-marker {
            width: 24px;
            text-align: center;
            font-size: 14px;
        }

        .line-number {
            min-width: 50px;
            text-align: right;
            color: var(--color-muted);
            padding-right: 15px;
            user-select: none;
        }

        .line-content {
            flex: 1;
            white-space: pre;
        }

        /* Responsive */
        @media (max-width: 768px) {
            body {
                padding: 10px;
            }

            .container {
                padding: 20px;
            }

            .summary-grid {
                grid-template-columns: 1fr;
            }

            .rule-header {
                flex-wrap: wrap;
            }

            .code-snippet {
                font-size: 12px;
            }
        }
    </style>
</head>
<body>
"""


def _generate_html_summary(timestamp: str, base_path: str, total_files: int,
                          rules_passed: int, rules_failed: int,
                          total_errors: int, total_warnings: int) -> str:
    """Generate HTML summary section."""
    return f"""
    <div class="container">
        <header class="report-header">
            <h1>Validation Report</h1>
            <p class="timestamp">Generated: {html.escape(timestamp)}</p>
            <p class="path">Path: {html.escape(base_path)}</p>
        </header>

        <div class="summary-grid">
            <div class="summary-card">
                <div class="summary-value">{total_files}</div>
                <div class="summary-label">Files Validated</div>
            </div>
            <div class="summary-card {'success' if rules_failed == 0 else 'error'}">
                <div class="summary-value">{rules_passed}/{rules_passed + rules_failed}</div>
                <div class="summary-label">Rules Passed</div>
            </div>
            <div class="summary-card error">
                <div class="summary-value">{total_errors}</div>
                <div class="summary-label">Errors</div>
            </div>
            <div class="summary-card warning">
                <div class="summary-value">{total_warnings}</div>
                <div class="summary-label">Warnings</div>
            </div>
        </div>
    </div>
"""


def _generate_html_rules(grouped: Dict[str, Dict]) -> str:
    """Generate HTML rules detail section."""
    rules_html = ['<div class="container"><h2>Rules Detail</h2>']

    # Sort rules: failed first, then by rule ID
    sorted_rules = sorted(
        grouped.items(),
        key=lambda x: (x[1]['failed_files'] == 0, x[0])
    )

    for rule_id, data in sorted_rules:
        passed = data['passed_files']
        total = data['total_files']
        failed = data['failed_files']
        description = data['description']

        # Determine status
        is_passed = failed == 0
        status_class = 'passed' if is_passed else 'failed'
        status_icon = '✓' if is_passed else '✗'

        # Rule header
        rules_html.append(f"""
        <div class="rule-section {status_class}">
            <div class="rule-header" onclick="toggleRule(this)">
                <span class="rule-status">{status_icon}</span>
                <span class="rule-title">{html.escape(rule_id)}</span>
                <span class="rule-description">{html.escape(description)}</span>
                <span class="rule-stats">({passed}/{total} files passed)</span>
            </div>
        """)

        # Rule details (only for failed rules)
        if not is_passed:
            rules_html.append('<div class="rule-details">')

            for failure in data['failures']:
                file_path = failure['file_path']
                issues = failure['issues']

                rules_html.append(f'<div class="file-failures">')
                rules_html.append(f'<h4>{html.escape(file_path)}</h4>')

                for issue in issues:
                    severity = issue['severity']
                    message = issue['message']
                    line = issue.get('line')

                    # Issue header
                    severity_class = 'error' if severity == 'error' else 'warning'
                    severity_label = severity.upper()

                    rules_html.append(f"""
                    <div class="issue-block {severity_class}">
                        <div class="issue-header">
                            <span class="issue-severity">{severity_label}</span>
                            <span class="issue-message">{html.escape(message)}</span>
                            {f'<span class="issue-line">Line {line}</span>' if line else ''}
                        </div>
                    """)

                    # Code snippet (if line number available)
                    if line:
                        snippet = extract_code_snippet(file_path, line, context=5)
                        if snippet:
                            snippet_html = format_code_snippet_html(snippet, line, severity)
                            rules_html.append(f'<div class="code-snippet">{snippet_html}</div>')

                    rules_html.append('</div>')  # issue-block

                rules_html.append('</div>')  # file-failures

            rules_html.append('</div>')  # rule-details

        rules_html.append('</div>')  # rule-section

    rules_html.append('</div>')  # container
    return '\n'.join(rules_html)


def _generate_html_footer() -> str:
    """Generate HTML document footer with JavaScript."""
    return """
    <script>
        function toggleRule(header) {
            const section = header.parentElement;
            const details = section.querySelector('.rule-details');

            if (details) {
                const isHidden = details.style.display === 'none';
                details.style.display = isHidden ? 'block' : 'none';
            }
        }

        // Initialize: collapse passed rules, expand failed rules
        document.addEventListener('DOMContentLoaded', function() {
            const passedRules = document.querySelectorAll('.rule-section.passed');
            passedRules.forEach(function(section) {
                const details = section.querySelector('.rule-details');
                if (details) {
                    details.style.display = 'none';
                }
            });
        });
    </script>
</body>
</html>
"""


def save_html_report(html_content: str) -> str:
    """
    Save HTML report to file.

    Args:
        html_content: HTML content to save

    Returns:
        Filename of saved report
    """
    import os

    filename = "validation-report.html"

    # Remove old file if it exists
    if os.path.exists(filename):
        os.remove(filename)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    return filename
