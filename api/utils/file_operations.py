# utils/file_operations.py
"""Helper functions for file operations."""

import os
import json
from fastapi import HTTPException
from typing import Any, Dict

def read_json_file(file_path: str) -> dict:
    """Read and parse a JSON file."""
    try:
        if not os.path.exists(file_path):
            return {}
            
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Invalid JSON in file: {file_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

def write_json_file(file_path: str, data: dict) -> None:
    """Write data to a JSON file."""
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error writing file: {str(e)}")

def get_nested_value(data: dict, path: str):
    """Get a value from a nested dictionary using a path like 'key1/key2'."""
    keys = path.strip('/').split('/')
    current = data
    for key in keys:
        if key not in current:
            return None
        current = current[key]
    return current

def set_nested_value(data: dict, path: str, value: Any) -> dict:
    """Set a value in a nested dictionary using a path like 'key1/key2'."""
    keys = path.strip('/').split('/')
    if not keys:
        return data
    
    current = data
    for i, key in enumerate(keys[:-1]):
        if key not in current:
            current[key] = {}
        elif not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value
    return data

def remove_nested_value(data: dict, path: str) -> dict:
    """Remove a value from a nested dictionary using a path like 'key1/key2'."""
    keys = path.strip('/').split('/')
    if not keys:
        return data
    
    current = data
    for i, key in enumerate(keys[:-1]):
        if key not in current:
            return data
        current = current[key]
    
    if keys[-1] in current:
        del current[keys[-1]]
    
    return data