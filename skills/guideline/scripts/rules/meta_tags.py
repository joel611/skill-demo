"""
Required meta tags validation rule.

Validates:
- charset="utf-8"
- http-equiv="x-ua-compatible" content="ie=edge"
- name="viewport" content="width=device-width"
- Cache control meta tags (3 tags)
- Content meta tags: title, keywords, description, summary
"""

from typing import List, Dict
from bs4 import BeautifulSoup
from . import validator_rule


@validator_rule("required-meta-tags", "Check required meta tags")
def validate_meta_tags(soup: BeautifulSoup, file_path: str, raw_lines: List[str]) -> List[Dict]:
    """
    Validate required meta tags.

    Checks:
    - charset="utf-8"
    - http-equiv="x-ua-compatible" content="ie=edge"
    - name="viewport" content="width=device-width"
    - Cache control meta tags (3 tags)
    - Content meta tags: title, keywords, description, summary

    Args:
        soup: BeautifulSoup parsed HTML
        file_path: Path to the HTML file
        raw_lines: Raw HTML lines for line number tracking

    Returns:
        List of issue dictionaries
    """
    issues = []
    head = soup.find('head')

    if not head:
        issues.append({
            "rule": "required-meta-tags",
            "severity": "error",
            "message": "Missing <head> tag",
            "line": None
        })
        return issues

    head_line = getattr(head, 'sourceline', None)

    # Check charset
    charset_meta = soup.find('meta', charset=True)
    if not charset_meta:
        issues.append({
            "rule": "required-meta-tags",
            "severity": "error",
            "message": "Missing required meta tag: charset",
            "line": head_line
        })
    elif charset_meta.get('charset', '').lower() != 'utf-8':
        issues.append({
            "rule": "required-meta-tags",
            "severity": "error",
            "message": f"Charset should be 'utf-8', found '{charset_meta.get('charset')}'",
            "line": getattr(charset_meta, 'sourceline', head_line)
        })

    # Check x-ua-compatible
    ua_meta = soup.find('meta', attrs={'http-equiv': lambda x: x and x.lower() == 'x-ua-compatible'})
    if not ua_meta:
        issues.append({
            "rule": "required-meta-tags",
            "severity": "error",
            "message": "Missing required meta tag: http-equiv='x-ua-compatible'",
            "line": head_line
        })
    elif 'ie=edge' not in ua_meta.get('content', '').lower():
        issues.append({
            "rule": "required-meta-tags",
            "severity": "warning",
            "message": "x-ua-compatible content should contain 'ie=edge'",
            "line": getattr(ua_meta, 'sourceline', head_line)
        })

    # Check viewport
    viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
    if not viewport_meta:
        issues.append({
            "rule": "required-meta-tags",
            "severity": "error",
            "message": "Missing required meta tag: viewport",
            "line": head_line
        })
    elif 'width=device-width' not in viewport_meta.get('content', '').lower():
        issues.append({
            "rule": "required-meta-tags",
            "severity": "warning",
            "message": "Viewport content should contain 'width=device-width'",
            "line": getattr(viewport_meta, 'sourceline', head_line)
        })

    # Check cache control meta tags
    cache_control_meta = soup.find('meta', attrs={'http-equiv': lambda x: x and x.lower() == 'cache-control'})
    if not cache_control_meta:
        issues.append({
            "rule": "required-meta-tags",
            "severity": "error",
            "message": "Missing cache control meta tag: Cache-Control",
            "line": head_line
        })

    pragma_meta = soup.find('meta', attrs={'http-equiv': lambda x: x and x.lower() == 'pragma'})
    if not pragma_meta:
        issues.append({
            "rule": "required-meta-tags",
            "severity": "error",
            "message": "Missing cache control meta tag: Pragma",
            "line": head_line
        })

    expires_meta = soup.find('meta', attrs={'http-equiv': lambda x: x and x.lower() == 'expires'})
    if not expires_meta:
        issues.append({
            "rule": "required-meta-tags",
            "severity": "error",
            "message": "Missing cache control meta tag: Expires",
            "line": head_line
        })

    # Check content meta tags
    content_meta_tags = ['title', 'keywords', 'description', 'summary']
    for tag_name in content_meta_tags:
        if tag_name == 'title':
            tag = soup.find('title')
            if not tag or not tag.string or not tag.string.strip():
                issues.append({
                    "rule": "required-meta-tags",
                    "severity": "error",
                    "message": "Missing or empty <title> tag",
                    "line": head_line
                })
        else:
            tag = soup.find('meta', attrs={'name': tag_name})
            if not tag:
                issues.append({
                    "rule": "required-meta-tags",
                    "severity": "error",
                    "message": f"Missing required meta tag: {tag_name}",
                    "line": head_line
                })

    return issues
