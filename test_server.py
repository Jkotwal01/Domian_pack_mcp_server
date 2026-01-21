"""
Test Suite for Domain Pack MCP Server

Run with: python test_server.py
"""

import json
from schema import validate_domain_pack, DomainPackValidator
from operations import apply_operation, apply_batch, OperationError
from utils import parse_yaml, parse_json, serialize_yaml, calculate_diff


def test_schema_validation():
    """Test schema validation with valid and invalid data"""
    print("\n=== Testing Schema Validation ===")
    
    validator = DomainPackValidator()
    
    # Valid minimal domain pack
    valid_data = {
        "name": "Legal",
        "description": "Legal and compliance",
        "version": "1.0.0"
    }
    
    try:
        validator.validate(valid_data)
        print("✓ Valid minimal domain pack accepted")
    except Exception as e:
        print(f"✗ Valid data rejected: {e}")
    
    # Invalid: missing required field
    invalid_data = {
        "name": "Test",
        "description": "Test domain"
        # Missing version
    }
    
    try:
        validator.validate(invalid_data)
        print("✗ Invalid data accepted (should have failed)")
    except Exception as e:
        print(f"✓ Invalid data rejected: {e}")
    
    # Invalid: wrong version format
    invalid_version = {
        "name": "Test",
        "description": "Test domain",
        "version": "1.0"  # Should be X.Y.Z
    }
    
    try:
        validator.validate(invalid_version)
        print("✗ Invalid version format accepted")
    except Exception as e:
        print(f"✓ Invalid version format rejected")


def test_operations():
    """Test all operation types"""
    print("\n=== Testing Operations ===")
    
    data = {
        "name": "Test",
        "description": "Test domain",
        "version": "1.0.0",
        "entities": [],
        "key_terms": ["term1", "term2"]
    }
    
    # Test ADD - append to array
    try:
        # For arrays, add operation appends
        test_data = {
            "name": "Test",
            "description": "Test domain",
            "version": "1.0.0",
            "entities": []
        }
        result = apply_operation(test_data, {
            "action": "add",
            "path": ["entities"],
            "value": {"name": "Client", "type": "CLIENT", "attributes": ["name"]}
        })
        assert len(result["entities"]) == 1
        print("✓ ADD operation works")
    except Exception as e:
        print(f"✗ ADD operation failed: {e}")
    
    # Test REPLACE
    try:
        result = apply_operation(data, {
            "action": "replace",
            "path": ["version"],
            "value": "2.0.0"
        })
        assert result["version"] == "2.0.0"
        print("✓ REPLACE operation works")
    except Exception as e:
        print(f"✗ REPLACE operation failed: {e}")
    
    # Test DELETE
    try:
        result = apply_operation(data, {
            "action": "delete",
            "path": ["key_terms", "0"]
        })
        assert len(result["key_terms"]) == 1
        print("✓ DELETE operation works")
    except Exception as e:
        print(f"✗ DELETE operation failed: {e}")
    
    # Test ASSERT
    try:
        result = apply_operation(data, {
            "action": "assert",
            "path": ["version"],
            "equals": "1.0.0"
        })
        print("✓ ASSERT operation works")
    except Exception as e:
        print(f"✗ ASSERT operation failed: {e}")
    
    # Test BATCH
    try:
        # Create data with key_terms for batch test
        batch_data = {
            "name": "Test",
            "description": "Test domain",
            "version": "1.0.0",
            "key_terms": ["term1", "term2"]
        }
        result = apply_batch(batch_data, [
            {"action": "replace", "path": ["version"], "value": "3.0.0"},
            {"action": "merge", "path": ["key_terms"], "value": ["term3"]}
        ])
        assert result["version"] == "3.0.0"
        assert len(result["key_terms"]) == 3
        print("✓ BATCH operation works")
    except Exception as e:
        print(f"✗ BATCH operation failed: {e}")


def test_yaml_parsing():
    """Test YAML parsing and serialization"""
    print("\n=== Testing YAML Parsing ===")
    
    yaml_content = """
name: Legal
description: Legal domain
version: 3.0.0
entities:
  - name: Client
    type: CLIENT
    attributes:
      - name
      - email
"""
    
    try:
        data = parse_yaml(yaml_content)
        assert data["name"] == "Legal"
        assert len(data["entities"]) == 1
        print("✓ YAML parsing works")
        
        # Test serialization
        yaml_out = serialize_yaml(data)
        assert "Legal" in yaml_out
        print("✓ YAML serialization works")
        
    except Exception as e:
        print(f"✗ YAML processing failed: {e}")


def test_diff_calculation():
    """Test diff calculation"""
    print("\n=== Testing Diff Calculation ===")
    
    old_data = {
        "name": "Test",
        "version": "1.0.0",
        "entities": []
    }
    
    new_data = {
        "name": "Test",
        "version": "2.0.0",
        "entities": [{"name": "Client"}]
    }
    
    try:
        diff = calculate_diff(old_data, new_data)
        assert diff["summary"]["has_changes"]
        print(f"✓ Diff calculation works: {diff['summary']['total_changes']} changes detected")
    except Exception as e:
        print(f"✗ Diff calculation failed: {e}")


def test_full_workflow():
    """Test complete workflow"""
    print("\n=== Testing Full Workflow ===")
    
    # Load sample YAML
    try:
        with open("../sample.yaml", "r") as f:
            content = f.read()
        
        # Parse
        data = parse_yaml(content)
        print("✓ Parsed sample.yaml")
        
        # Validate
        validate_domain_pack(data)
        print("✓ Validated schema")
        
        # Apply operation
        result = apply_operation(data, {
            "action": "merge",
            "path": ["key_terms"],
            "value": ["new_term"]
        })
        print("✓ Applied operation")
        
        # Validate result
        validate_domain_pack(result)
        print("✓ Validated result")
        
        # Calculate diff
        diff = calculate_diff(data, result)
        print(f"✓ Calculated diff: {diff['summary']['total_changes']} changes")
        
        # Serialize
        yaml_out = serialize_yaml(result)
        print(f"✓ Serialized result ({len(yaml_out)} bytes)")
        
    except FileNotFoundError:
        print("⚠ sample.yaml not found, skipping full workflow test")
    except Exception as e:
        print(f"✗ Full workflow failed: {e}")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Domain Pack MCP Server - Test Suite")
    print("=" * 60)
    
    test_schema_validation()
    test_operations()
    test_yaml_parsing()
    test_diff_calculation()
    test_full_workflow()
    
    print("\n" + "=" * 60)
    print("Test suite completed")
    print("=" * 60)


if __name__ == "__main__":
    main()
