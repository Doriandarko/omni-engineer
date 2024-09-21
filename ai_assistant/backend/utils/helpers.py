# backend/utils/helpers.py

import re
from typing import List, Dict, Any

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing or replacing invalid characters.
    """
    # Remove any non-alphanumeric characters except for dots, dashes, and underscores
    sanitized = re.sub(r'[^\w\-\.]', '_', filename)
    # Remove any leading or trailing dots or spaces
    sanitized = sanitized.strip('. ')
    return sanitized

def truncate_string(s: str, max_length: int = 100) -> str:
    """
    Truncate a string to a maximum length, adding an ellipsis if truncated.
    """
    return (s[:max_length-3] + '...') if len(s) > max_length else s

def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
    """
    Flatten a nested dictionary.
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of a specified size.
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def remove_duplicates(lst: List[Any]) -> List[Any]:
    """
    Remove duplicates from a list while preserving order.
    """
    seen = set()
    return [x for x in lst if not (x in seen or seen.add(x))]

def is_valid_email(email: str) -> bool:
    """
    Check if a string is a valid email address.
    """
    email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
    return bool(email_regex.match(email))

def camel_to_snake(name: str) -> str:
    """
    Convert a camelCase string to snake_case.
    """
    pattern = re.compile(r'(?<!^)(?=[A-Z])')
    return pattern.sub('_', name).lower()

def snake_to_camel(name: str) -> str:
    """
    Convert a snake_case string to camelCase.
    """
    components = name.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])