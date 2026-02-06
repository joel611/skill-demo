"""Common utility functions for promo page scripts."""

import os
import re
from typing import Optional


def detect_promo_path(start_path: str = ".") -> Optional[str]:
    """
    Auto-detect directory matching the pattern from the start path.

    Args:
        start_path: Directory to start searching from (default: current directory)

    Returns:
        Path to first matching d##/k## directory, or None if not found
    """
    pattern = re.compile(r'd\d{2}/k\d{2}')

    for root, dirs, files in os.walk(start_path):
        if pattern.search(root):
            match = pattern.search(root)
            if match:
                matched_path = root[:match.end()]
                return matched_path

    return None
