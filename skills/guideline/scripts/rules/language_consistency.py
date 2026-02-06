"""
Language consistency validation rule.

Validates that HTML language attributes match the file path:
- chi/ directory → class="no-js tc" and lang="zh-hant"
- eng/ directory → class="no-js en" and lang="en"
- schi/ directory → class="no-js sc" and lang="zh-hans"
"""

from typing import List, Dict
from bs4 import BeautifulSoup
from . import validator_rule


@validator_rule("language-consistency", "Check language consistency with file path")
def validate_language_consistency(soup: BeautifulSoup, file_path: str, raw_lines: List[str]) -> List[Dict]:
    """
    Validate that HTML language attributes match the file path.

    Expected mappings:
    - chi/ directory → class="no-js tc" and lang="zh-hant"
    - eng/ directory → class="no-js en" and lang="en"
    - schi/ directory → class="no-js sc" and lang="zh-hans"

    Args:
        soup: BeautifulSoup parsed HTML
        file_path: Path to the HTML file
        raw_lines: Raw HTML lines for line number tracking

    Returns:
        List of issue dictionaries
    """
    issues = []

    # Determine expected language based on path
    path_lower = file_path.lower().replace('\\', '/')
    expected_lang_code = None
    expected_lang_attr = None

    if '/chi/' in path_lower:
        expected_lang_code = 'tc'
        expected_lang_attr = 'zh-hant'
    elif '/eng/' in path_lower:
        expected_lang_code = 'en'
        expected_lang_attr = 'en'
    elif '/schi/' in path_lower:
        expected_lang_code = 'sc'
        expected_lang_attr = 'zh-hans'
    else:
        # No language directory found, skip validation
        return issues

    html_tag = soup.find('html')
    if not html_tag:
        # This would be caught by basic-structure rule
        return issues

    html_line = getattr(html_tag, 'sourceline', None)

    # Check class attribute for language code
    html_class = html_tag.get('class', [])
    if isinstance(html_class, list):
        html_class = ' '.join(html_class)

    if expected_lang_code not in html_class:
        issues.append({
            "rule": "language-consistency",
            "severity": "error",
            "message": f"HTML class should contain '{expected_lang_code}' for files in {expected_lang_code.replace('tc', 'chi').replace('en', 'eng').replace('sc', 'schi')}/ directory",
            "line": html_line
        })

    # Check lang attribute
    lang_attr = html_tag.get('lang')
    if lang_attr != expected_lang_attr:
        issues.append({
            "rule": "language-consistency",
            "severity": "error",
            "message": f"HTML lang attribute should be '{expected_lang_attr}' for files in {expected_lang_code.replace('tc', 'chi').replace('en', 'eng').replace('sc', 'schi')}/ directory, found '{lang_attr}'",
            "line": html_line
        })

    return issues
