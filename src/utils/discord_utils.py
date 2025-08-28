# src/utils/discord_utils.py

import os
import re
from urllib.parse import urlparse

def is_valid_url(url: str) -> bool:
    """Check if a string is a valid HTTP/S URL."""
    try:
        result = urlparse(str(url))
        return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
    except (ValueError, AttributeError):
        return False

def is_local_file(path: str) -> bool:
    """Check if a string represents an existing local file path."""
    try:
        path_str = str(path).strip()
        return not path_str.startswith(('http://', 'https://')) and os.path.exists(path_str)
    except (ValueError, AttributeError):
        return False
    
def extract_valid_urls(text: str) -> list[str]:
    """Extract all valid HTTP/S URLs from a given string."""
    # Regex to find potential URLs
    url_pattern = re.compile(r'(https?://[^\s]+)')
    possible_urls = url_pattern.findall(text)

    # Filter only valid URLs
    valid_urls = [url for url in possible_urls if is_valid_url(url)]
    return valid_urls