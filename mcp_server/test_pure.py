"""
Comprehensive Test Suite for Pure MCP Server

Tests all components of the pure transformation engine:
1. Path resolution
2. Safety checks
3. Schema validation
4. Operations
5. Atomic execution
6. Integration tests
"""

import pytest
import copy
from typing import Dict, Any

# Import modules to test
from path_resolver import (
    parse_path,
    resolve_path,
    validate_path_exists,
    get_value_at_path,
    set_value_at_path,
    delete_at_path,
    PathError,
    PathSegment
)

from safety_checks import (
    run_safety_checks,
    check_required_field_deletion,
    check_type_compatibility,
    check_bulk_change_threshold,
    check_key_overwrite,
    ErrorLevel
)

from schema import (
    DOMAIN_PACK_SCHEMA,
    validate_schema,
    ValidationError,
    validate_pre_mutation,
    validate_post_mutation
)

from operations import (
    apply_operation,
    apply_batch,
    OperationError
)

from executor import (
    execute_transformation,
    preview_transformation,
    ExecutionOptions
)

from utils import (
    parse_content,
    serialize_content,
    calculate_diff
)


# Test Data
MINIMAL_DOMAIN_PACK = {
    "name": "Test Domain",
    "description": "Test domain pack",
    "version": "1.0.0"
}

SAMPLE_DOMAIN_PACK = {
    "name": "Legal",
    "description": "Legal domain pack",
    "version": "1.0.0",
    "entities": [
        {
            "name": "Attorney",
            "type": "ATTORNEY",
            "attributes": ["name", "bar_number"]
        }
    ],
    "key_terms": ["legal", "attorney", "bar"]
}


class TestPathResolver:
    """Test path resolution functionality"""
    
    def test_parse_simple_path(self):
        """Test parsing simple dot notation"""
        segments = parse_path("entities.Attorney.name")
        assert len(segments) == 3
        assert segments[0].key == "entities"
        assert segments[1].key == "Attorney"
        assert segments[2].key == "name"
    
    def test_parse_array_path(self):
        """Test parsing array indexing"""
        segments = parse_path("entities[0].name")
        assert len(segments) == 3
        assert segments[0].key == "entities"
        assert segments[1].is_array_access
        assert segments[1].index == 0
        assert segments[2].key == "name"
    
    def test_parse_mixed_path(self):
        """Test parsing mixed paths"""
        segments = parse_path("entities[0].attributes[1]")
        assert len(segments) == 4
        assert segments[0].key == "entities"
        assert segments[1].index == 0
        assert segments[2].key == "attributes"
        assert segments[3].index == 1
    
    def test_parse_invalid_path(self):
        """Test parsing invalid paths"""
        with pytest.raises(PathError):
            parse_path("")
        
        with pytest.raises(PathError):
            parse_path("entities..name")
        
        with pytest.raises(PathError):
            parse_path("entities[abc]")
    
    def test_resolve_simple_path(self):
        """Test resolving simple paths"""
        doc = {"entities": {"Attorney": {"name": "John"}}}
        ref = resolve_path(doc, "entities.Attorney.name")
        assert ref.value == "John"
        assert ref.exists
    
    def test_resolve_array_path(self):
        """Test resolving array paths"""
        doc = {"entities": [{"name": "Attorney"}]}
        ref = resolve_path(doc, "entities[0].name")
        assert ref.value == "Attorney"
        assert ref.exists
    
    def test_resolve_nonexistent_path(self):
        """Test resolving non-existent paths"""
        doc = {"entities": []}
        with pytest.raises(PathError):
            resolve_path(doc, "entities[0].name")
    
    def test_get_value_at_path(self):
        """Test getting values"""
        doc = SAMPLE_DOMAIN_PACK
        value = get_value_at_path(doc, "entities[0].name")
        assert value == "Attorney"
        
        value = get_value_at_path(doc, "nonexistent", default="default")
        assert value == "default"
    
    def test_set_value_at_path(self):
        """Test setting values"""
        doc = copy.deepcopy(SAMPLE_DOMAIN_PACK)
        set_value_at_path(doc, "entities[0].name", "Lawyer")
        assert doc["entities"][0]["name"] == "Lawyer"
    
    def test_delete_at_path(self):
        """Test deleting values"""
        doc = copy.deepcopy(SAMPLE_DOMAIN_PACK)
        deleted = delete_at_path(doc, "key_terms")
        assert "key_terms" not in doc
        assert deleted == ["legal", "attorney", "bar"]


class TestSafetyChecks:
    """Test safety check functionality"""
    
    def test_required_field_deletion(self):
        """Test detection of required field deletion"""
        operation = {"action": "delete", "path": ["name"]}
        issue = check_required_field_deletion(operation, DOMAIN_PACK_SCHEMA, MINIMAL_DOMAIN_PACK)
        assert issue is not None
        assert issue.level == ErrorLevel.ERROR
        assert issue.code == "REQUIRED_FIELD_DELETION"
    
    def test_type_compatibility(self):
        """Test type compatibility checking"""
        operation = {
            "action": "update",
            "path": [],
            "updates": {"version": 123}  # Should be string
        }
        issue = check_type_compatibility(operation, MINIMAL_DOMAIN_PACK, DOMAIN_PACK_SCHEMA)
        assert issue is not None
        assert issue.code == "TYPE_MISMATCH"
    
    def test_bulk_change_threshold(self):
        """Test bulk change warnings"""
        operations = [{"action": "add", "path": ["key_terms"], "value": f"term{i}"} for i in range(15)]
        issue = check_bulk_change_threshold(operations, threshold=10)
        assert issue is not None
        assert issue.level == ErrorLevel.WARNING
    
    def test_key_overwrite(self):
        """Test key overwrite detection"""
        doc = {"entities": []}
        operation = {"action": "add", "path": ["entities"], "value": []}
        issue = check_key_overwrite(operation, doc)
        assert issue is not None
        assert issue.code == "KEY_OVERWRITE_WARNING"
    
    def test_run_all_safety_checks(self):
        """Test running all safety checks"""
        operations = [
            {"action": "update", "path": [], "updates": {"version": "2.0.0"}}
        ]
        result = run_safety_checks(operations, MINIMAL_DOMAIN_PACK, DOMAIN_PACK_SCHEMA)
        assert result.passed
        assert len(result.errors) == 0


class TestSchemaValidation:
    """Test schema validation functionality"""
    
    def test_validate_minimal_pack(self):
        """Test validating minimal domain pack"""
        validate_schema(MINIMAL_DOMAIN_PACK, DOMAIN_PACK_SCHEMA)
        # Should not raise
    
    def test_validate_invalid_pack(self):
        """Test validating invalid pack"""
        invalid = {"name": "Test"}  # Missing required fields
        with pytest.raises(ValidationError):
            validate_schema(invalid, DOMAIN_PACK_SCHEMA)
    
    def test_validate_invalid_version(self):
        """Test validating invalid version format"""
        invalid = {
            "name": "Test",
            "description": "Test",
            "version": "1.0"  # Should be X.Y.Z
        }
        with pytest.raises(ValidationError):
            validate_schema(invalid, DOMAIN_PACK_SCHEMA)
    
    def test_pre_mutation_validation(self):
        """Test pre-mutation validation"""
        result = validate_pre_mutation(MINIMAL_DOMAIN_PACK, DOMAIN_PACK_SCHEMA)
        assert result["valid"]
        assert len(result["errors"]) == 0
    
    def test_post_mutation_validation(self):
        """Test post-mutation validation"""
        result = validate_post_mutation(SAMPLE_DOMAIN_PACK, DOMAIN_PACK_SCHEMA)
        assert result["valid"]
        assert len(result["errors"]) == 0


class TestOperations:
    """Test operation execution"""
    
    def test_add_operation(self):
        """Test add operation"""
        doc = copy.deepcopy(MINIMAL_DOMAIN_PACK)
        operation = {"action": "add", "path": ["key_terms"], "value": ["legal"]}
        result = apply_operation(doc, operation)
        assert "key_terms" in result
        assert result["key_terms"] == ["legal"]
    

    
    def test_delete_operation(self):
        """Test delete operation"""
        doc = copy.deepcopy(SAMPLE_DOMAIN_PACK)
        operation = {"action": "delete", "path": ["key_terms"]}
        result = apply_operation(doc, operation)
        assert "key_terms" not in result
    
    def test_update_operation(self):
        """Test update operation"""
        doc = copy.deepcopy(MINIMAL_DOMAIN_PACK)
        operation = {
            "action": "update",
            "path": [],
            "updates": {"version": "2.0.0", "description": "Updated"}
        }
        result = apply_operation(doc, operation)
        assert result["version"] == "2.0.0"
        assert result["description"] == "Updated"
    
    def test_batch_operations(self):
        """Test batch operations"""
        doc = copy.deepcopy(MINIMAL_DOMAIN_PACK)
        operations = [
            {"action": "update", "path": [], "updates": {"version": "2.0.0"}},
            {"action": "add", "path": ["key_terms"], "value": ["legal"]}
        ]
        result = apply_batch(doc, operations)
        assert result["version"] == "2.0.0"
        assert "key_terms" in result
    
    def test_invalid_operation(self):
        """Test invalid operation handling"""
        doc = copy.deepcopy(MINIMAL_DOMAIN_PACK)
        operation = {"action": "invalid", "path": ["test"]}
        with pytest.raises(OperationError):
            apply_operation(doc, operation)


class TestExecutor:
    """Test atomic execution controller"""
    
    def test_successful_transformation(self):
        """Test successful transformation"""
        operations = [
            {"action": "update", "path": [], "updates": {"version": "2.0.0"}}
        ]
        result = execute_transformation(
            document=MINIMAL_DOMAIN_PACK,
            schema=DOMAIN_PACK_SCHEMA,
            operations=operations
        )
        assert result.success
        assert result.document["version"] == "2.0.0"
        assert len(result.errors) == 0
    
    def test_failed_transformation(self):
        """Test failed transformation (invalid operation)"""
        operations = [
            {"action": "delete", "path": ["name"]}  # Required field
        ]
        result = execute_transformation(
            document=MINIMAL_DOMAIN_PACK,
            schema=DOMAIN_PACK_SCHEMA,
            operations=operations
        )
        assert not result.success
        assert len(result.errors) > 0
    
    def test_strict_mode(self):
        """Test strict mode with warnings"""
        doc = {"name": "Test", "description": "Test", "version": "1.0.0", "entities": []}
        operations = [
            {"action": "add", "path": ["entities"], "value": []}  # Overwrite warning
        ]
        options = ExecutionOptions(strict_mode=True)
        result = execute_transformation(doc, DOMAIN_PACK_SCHEMA, operations, options)
        assert not result.success  # Should fail in strict mode
    
    def test_preview_transformation(self):
        """Test preview mode"""
        operations = [
            {"action": "update", "path": [], "updates": {"version": "2.0.0"}}
        ]
        preview = preview_transformation(
            document=MINIMAL_DOMAIN_PACK,
            schema=DOMAIN_PACK_SCHEMA,
            operations=operations
        )
        assert preview["would_succeed"]
        assert preview["diff"] is not None
        assert preview["operations_count"] == 1


class TestUtils:
    """Test utility functions"""
    
    def test_parse_yaml(self):
        """Test YAML parsing"""
        yaml_str = """
name: Test
description: Test domain
version: 1.0.0
"""
        doc = parse_content(yaml_str, "yaml")
        assert doc["name"] == "Test"
        assert doc["version"] == "1.0.0"
    
    def test_parse_json(self):
        """Test JSON parsing"""
        json_str = '{"name": "Test", "description": "Test", "version": "1.0.0"}'
        doc = parse_content(json_str, "json")
        assert doc["name"] == "Test"
    
    def test_serialize_yaml(self):
        """Test YAML serialization"""
        serialized = serialize_content(MINIMAL_DOMAIN_PACK, "yaml")
        assert "name: Test Domain" in serialized
        assert "version: 1.0.0" in serialized
    
    def test_serialize_json(self):
        """Test JSON serialization"""
        serialized = serialize_content(MINIMAL_DOMAIN_PACK, "json")
        assert '"name"' in serialized
        assert '"version"' in serialized
    
    def test_calculate_diff(self):
        """Test diff calculation"""
        old_doc = copy.deepcopy(MINIMAL_DOMAIN_PACK)
        new_doc = copy.deepcopy(MINIMAL_DOMAIN_PACK)
        new_doc["version"] = "2.0.0"
        
        diff = calculate_diff(old_doc, new_doc)
        assert diff is not None


class TestIntegration:
    """Integration tests for full workflow"""
    
    def test_full_transformation_workflow(self):
        """Test complete transformation workflow"""
        # Start with minimal pack
        doc = copy.deepcopy(MINIMAL_DOMAIN_PACK)
        
        # Apply multiple operations
        operations = [
            {"action": "update", "path": [], "updates": {"version": "2.0.0"}},
            {"action": "add", "path": ["entities"], "value": []},
            {"action": "add", "path": ["key_terms"], "value": ["test"]}
        ]
        
        result = execute_transformation(doc, DOMAIN_PACK_SCHEMA, operations)
        
        assert result.success
        assert result.document["version"] == "2.0.0"
        assert "entities" in result.document
        assert "key_terms" in result.document
        assert len(result.affected_paths) > 0
    
    def test_idempotency(self):
        """Test that same operations produce same results"""
        operations = [
            {"action": "update", "path": [], "updates": {"version": "2.0.0"}}
        ]
        
        result1 = execute_transformation(
            copy.deepcopy(MINIMAL_DOMAIN_PACK),
            DOMAIN_PACK_SCHEMA,
            operations
        )
        
        result2 = execute_transformation(
            copy.deepcopy(MINIMAL_DOMAIN_PACK),
            DOMAIN_PACK_SCHEMA,
            operations
        )
        
        assert result1.success == result2.success
        assert result1.document == result2.document


def run_tests():
    """Run all tests"""
    print("=" * 60)
    print("Running Pure MCP Server Test Suite")
    print("=" * 60)
    
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_tests()
