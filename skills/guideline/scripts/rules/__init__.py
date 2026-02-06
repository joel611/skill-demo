"""
Validation rules registry and auto-discovery module.

This module provides the decorator for registering validation rules
and automatically imports all rule modules.
"""

from typing import List, Dict, Callable, Tuple
from bs4 import BeautifulSoup

# Global rule registry
_validation_rules: List[Tuple[str, str, Callable]] = []


def validator_rule(rule_id: str, description: str):
    """
    Decorator to register validation rules.

    Args:
        rule_id: Unique identifier for the rule
        description: Human-readable description of what the rule checks

    Returns:
        Decorator function that registers the validation rule
    """
    def decorator(func: Callable):
        _validation_rules.append((rule_id, description, func))
        return func
    return decorator


def get_all_rules() -> List[Tuple[str, str, Callable]]:
    """
    Get all registered validation rules.

    Returns:
        List of (rule_id, description, function) tuples
    """
    return _validation_rules


# Auto-import all rule modules to trigger registration
from . import basic_structure
from . import meta_tags
from . import language_consistency
