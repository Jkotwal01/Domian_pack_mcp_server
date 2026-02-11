"""YAML conversion utilities."""
import yaml
import json
from typing import Dict, Any


def json_to_yaml(config_json: Dict[str, Any]) -> str:
    """
    Convert domain config JSON to YAML format.
    
    Args:
        config_json: Domain configuration as dictionary
        
    Returns:
        YAML string representation
    """
    return yaml.dump(config_json, default_flow_style=False, sort_keys=False, allow_unicode=True)


def yaml_to_json(yaml_str: str) -> Dict[str, Any]:
    """
    Convert YAML string to domain config JSON.
    
    Args:
        yaml_str: YAML string
        
    Returns:
        Domain configuration dictionary
        
    Raises:
        yaml.YAMLError: If YAML is invalid
    """
    return yaml.safe_load(yaml_str)


def validate_yaml(yaml_str: str) -> bool:
    """
    Validate YAML syntax.
    
    Args:
        yaml_str: YAML string to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        yaml.safe_load(yaml_str)
        return True
    except yaml.YAMLError:
        return False
