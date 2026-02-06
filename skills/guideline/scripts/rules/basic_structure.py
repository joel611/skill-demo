"""
Basic HTML structure validation rule.

Validates:
- DOCTYPE html declaration
- <html> tag with class and lang attributes
- class contains "no-js" and language code (tc/en/sc)
- lang attribute is valid (zh-hant/en/zh-hans)
"""

from typing import List, Dict
from bs4 import BeautifulSoup
from . import validator_rule


@validator_rule("basic-structure", "Check DOCTYPE and html tag")
def validate_basic_structure(soup: BeautifulSoup, file_path: str, raw_lines: List[str]) -> List[Dict]:
    """
    Validate basic HTML document structure.

    Checks:
    - DOCTYPE html is present
    - <html> tag has class and lang attributes
    - class contains "no-js" and language code (tc/en/sc)
    - lang attribute is valid (zh-hant/en/zh-hans)

    Args:
        soup: BeautifulSoup parsed HTML
        file_path: Path to the HTML file
        raw_lines: Raw HTML lines for line number tracking

    Returns:
        List of issue dictionaries
    """
    issues = []

    # Check DOCTYPE
    doctype_found = False
    for item in soup.contents:
        if hasattr(item, 'name') and item.name is None:
            # This is a DOCTYPE or other declaration
            if 'html' in str(item).lower():
                doctype_found = True
                break

    if not doctype_found:
        issues.append({
            "rule": "basic-structure",
            "severity": "error",
            "message": "Missing DOCTYPE html declaration",
            "line": None
        })

    # Check HTML tag
    html_tag = soup.find('html')
    if not html_tag:
        issues.append({
            "rule": "basic-structure",
            "severity": "error",
            "message": "Missing <html> tag",
            "line": None
        })
        return issues

    # Get line number for html tag
    html_line = getattr(html_tag, 'sourceline', None)

    # Check class attribute
    html_class = html_tag.get('class', [])
    if isinstance(html_class, list):
        html_class = ' '.join(html_class)

    if not html_class:
        issues.append({
            "rule": "basic-structure",
            "severity": "error",
            "message": "HTML tag missing class attribute",
            "line": html_line
        })
    else:
        # Check for "no-js"
        if 'no-js' not in html_class:
            issues.append({
                "rule": "basic-structure",
                "severity": "error",
                "message": "HTML class should contain 'no-js'",
                "line": html_line
            })

        # Check for language code (tc/en/sc)
        has_lang_code = any(lang in html_class for lang in ['tc', 'en', 'sc'])
        if not has_lang_code:
            issues.append({
                "rule": "basic-structure",
                "severity": "error",
                "message": "HTML class should contain language code (tc/en/sc)",
                "line": html_line
            })

    # Check lang attribute
    lang_attr = html_tag.get('lang')
    if not lang_attr:
        issues.append({
            "rule": "basic-structure",
            "severity": "error",
            "message": "HTML tag missing lang attribute",
            "line": html_line
        })
    elif lang_attr not in ['zh-hant', 'en', 'zh-hans']:
        issues.append({
            "rule": "basic-structure",
            "severity": "error",
            "message": f"Invalid lang attribute '{lang_attr}'. Expected: zh-hant, en, or zh-hans",
            "line": html_line
        })

    return issues
