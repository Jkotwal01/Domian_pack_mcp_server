"""
Comprehensive tests for primitive CRUD operations
"""

import pytest
from app.logic.operations import (
    create, read, update, delete,
    apply_operation, apply_batch,
    CRUDError, PathNotFoundError, PathExistsError, InvalidPathError
)


# ============================================================
# CREATE Tests
# ============================================================

class TestCreate:
    """Test CREATE operation"""
    
    def test_create_top_level_key(self):
        """Create a new top-level key in empty dict"""
        data = {}
        result = create(data, ["name"], "John")
        assert result == {"name": "John"}
        assert data == {}  # Original unchanged
    
    def test_create_nested_key(self):
        """Create a nested key"""
        data = {"user": {}}
        result = create(data, ["user", "age"], 30)
        assert result == {"user": {"age": 30}}
    
    def test_create_deeply_nested(self):
        """Create deeply nested key"""
        data = {"a": {"b": {"c": {}}}}
        result = create(data, ["a", "b", "c", "d"], "value")
        assert result == {"a": {"b": {"c": {"d": "value"}}}}
    
    def test_create_fails_if_exists(self):
        """CREATE fails if key already exists"""
        data = {"name": "John"}
        with pytest.raises(PathExistsError, match="already exists"):
            create(data, ["name"], "Jane")
    
    def test_create_append_to_list(self):
        """Append to list using '-' """
        data = {"items": [1, 2]}
        result = create(data, ["items", "-"], 3)
        assert result == {"items": [1, 2, 3]}
    
    def test_create_insert_into_list(self):
        """Insert into list at specific index"""
        data = {"items": [1, 3]}
        result = create(data, ["items", "1"], 2)
        assert result == {"items": [1, 2, 3]}
    
    def test_create_insert_at_start(self):
        """Insert at start of list"""
        data = {"items": [2, 3]}
        result = create(data, ["items", "0"], 1)
        assert result == {"items": [1, 2, 3]}
    
    def test_create_insert_at_end(self):
        """Insert at end of list (same as append)"""
        data = {"items": [1, 2]}
        result = create(data, ["items", "2"], 3)
        assert result == {"items": [1, 2, 3]}
    
    def test_create_fails_invalid_list_index(self):
        """CREATE fails with invalid list index"""
        data = {"items": [1, 2]}
        with pytest.raises(InvalidPathError, match="out of range"):
            create(data, ["items", "10"], 3)
    
    def test_create_fails_on_nonexistent_path(self):
        """CREATE fails if intermediate path doesn't exist"""
        data = {}
        with pytest.raises(PathNotFoundError):
            create(data, ["user", "age"], 30)
    
    def test_create_complex_value(self):
        """Create with complex nested value"""
        data = {"entities": []}
        value = {"name": "User", "fields": ["id", "name"]}
        result = create(data, ["entities", "-"], value)
        assert result == {"entities": [{"name": "User", "fields": ["id", "name"]}]}
    
    def test_create_fails_empty_path(self):
        """CREATE fails with empty path"""
        with pytest.raises(InvalidPathError, match="empty"):
            create({}, [], "value")
    
    def test_create_fails_non_dict_root(self):
        """CREATE fails if root is not a dict"""
        with pytest.raises(InvalidPathError, match="must be a dict"):
            create([1, 2, 3], ["0"], 99)


# ============================================================
# READ Tests
# ============================================================

class TestRead:
    """Test READ operation"""
    
    def test_read_top_level(self):
        """Read top-level key"""
        data = {"name": "John"}
        assert read(data, ["name"]) == "John"
    
    def test_read_nested(self):
        """Read nested value"""
        data = {"user": {"age": 30}}
        assert read(data, ["user", "age"]) == 30
    
    def test_read_from_list(self):
        """Read from list by index"""
        data = {"items": [1, 2, 3]}
        assert read(data, ["items", "1"]) == 2
    
    def test_read_entire_dict(self):
        """Read entire data with empty path"""
        data = {"name": "John", "age": 30}
        assert read(data, []) == data
    
    def test_read_complex_nested(self):
        """Read complex nested structure"""
        data = {
            "entities": [
                {"name": "User", "fields": ["id", "name"]},
                {"name": "Post", "fields": ["id", "title"]}
            ]
        }
        assert read(data, ["entities", "0", "fields", "1"]) == "name"
    
    def test_read_fails_nonexistent_key(self):
        """READ fails if key doesn't exist"""
        data = {"name": "John"}
        with pytest.raises(PathNotFoundError):
            read(data, ["age"])
    
    def test_read_fails_invalid_list_index(self):
        """READ fails with out of range list index"""
        data = {"items": [1, 2]}
        with pytest.raises(PathNotFoundError, match="out of range"):
            read(data, ["items", "10"])
    
    def test_read_fails_non_dict_root(self):
        """READ fails if root is not a dict"""
        with pytest.raises(InvalidPathError, match="must be a dict"):
            read([1, 2, 3], ["0"])


# ============================================================
# UPDATE Tests
# ============================================================

class TestUpdate:
    """Test UPDATE operation"""
    
    def test_update_top_level(self):
        """Update top-level key"""
        data = {"name": "John"}
        result = update(data, ["name"], "Jane")
        assert result == {"name": "Jane"}
        assert data == {"name": "John"}  # Original unchanged
    
    def test_update_nested(self):
        """Update nested value"""
        data = {"user": {"age": 30}}
        result = update(data, ["user", "age"], 31)
        assert result == {"user": {"age": 31}}
    
    def test_update_list_item(self):
        """Update list item"""
        data = {"items": [1, 2, 3]}
        result = update(data, ["items", "1"], 99)
        assert result == {"items": [1, 99, 3]}
    
    def test_update_replace_entire_object(self):
        """Replace entire nested object"""
        data = {"user": {"name": "John", "age": 30}}
        result = update(data, ["user"], {"name": "Jane"})
        assert result == {"user": {"name": "Jane"}}
    
    def test_update_fails_nonexistent_key(self):
        """UPDATE fails if key doesn't exist"""
        data = {"name": "John"}
        with pytest.raises(PathNotFoundError):
            update(data, ["age"], 30)
    
    def test_update_fails_empty_path(self):
        """UPDATE fails with empty path (can't update root)"""
        data = {"name": "John"}
        with pytest.raises(InvalidPathError, match="Cannot UPDATE root"):
            update(data, [], {"name": "Jane"})
    
    def test_update_fails_non_dict_root(self):
        """UPDATE fails if root is not a dict"""
        with pytest.raises(InvalidPathError, match="must be a dict"):
            update([1, 2, 3], ["0"], 99)


# ============================================================
# DELETE Tests
# ============================================================

class TestDelete:
    """Test DELETE operation"""
    
    def test_delete_top_level(self):
        """Delete top-level key"""
        data = {"name": "John", "age": 30}
        result = delete(data, ["age"])
        assert result == {"name": "John"}
        assert data == {"name": "John", "age": 30}  # Original unchanged
    
    def test_delete_nested(self):
        """Delete nested key"""
        data = {"user": {"name": "John", "age": 30}}
        result = delete(data, ["user", "age"])
        assert result == {"user": {"name": "John"}}
    
    def test_delete_list_item(self):
        """Delete list item"""
        data = {"items": [1, 2, 3]}
        result = delete(data, ["items", "1"])
        assert result == {"items": [1, 3]}
    
    def test_delete_first_list_item(self):
        """Delete first item in list"""
        data = {"items": [1, 2, 3]}
        result = delete(data, ["items", "0"])
        assert result == {"items": [2, 3]}
    
    def test_delete_last_list_item(self):
        """Delete last item in list"""
        data = {"items": [1, 2, 3]}
        result = delete(data, ["items", "2"])
        assert result == {"items": [1, 2]}
    
    def test_delete_fails_nonexistent_key(self):
        """DELETE fails if key doesn't exist"""
        data = {"name": "John"}
        with pytest.raises(PathNotFoundError):
            delete(data, ["age"])
    
    def test_delete_fails_empty_path(self):
        """DELETE fails with empty path (can't delete root)"""
        data = {"name": "John"}
        with pytest.raises(InvalidPathError, match="Cannot DELETE root"):
            delete(data, [])
    
    def test_delete_fails_non_dict_root(self):
        """DELETE fails if root is not a dict"""
        with pytest.raises(InvalidPathError, match="must be a dict"):
            delete([1, 2, 3], ["0"])


# ============================================================
# Dispatcher Tests
# ============================================================

class TestApplyOperation:
    """Test operation dispatcher"""
    
    def test_apply_create(self):
        """Apply CREATE via dispatcher"""
        data = {}
        op = {"op": "CREATE", "path": ["name"], "value": "John"}
        result = apply_operation(data, op)
        assert result == {"name": "John"}
    
    def test_apply_read(self):
        """Apply READ via dispatcher"""
        data = {"name": "John"}
        op = {"op": "READ", "path": ["name"]}
        result = apply_operation(data, op)
        assert result == "John"
    
    def test_apply_update(self):
        """Apply UPDATE via dispatcher"""
        data = {"name": "John"}
        op = {"op": "UPDATE", "path": ["name"], "value": "Jane"}
        result = apply_operation(data, op)
        assert result == {"name": "Jane"}
    
    def test_apply_delete(self):
        """Apply DELETE via dispatcher"""
        data = {"name": "John", "age": 30}
        op = {"op": "DELETE", "path": ["age"]}
        result = apply_operation(data, op)
        assert result == {"name": "John"}
    
    def test_apply_fails_missing_op(self):
        """Dispatcher fails if 'op' missing"""
        with pytest.raises(InvalidPathError, match="must have 'op'"):
            apply_operation({}, {"path": []})
    
    def test_apply_fails_invalid_op(self):
        """Dispatcher fails with unknown operation"""
        with pytest.raises(InvalidPathError, match="Unknown operation"):
            apply_operation({}, {"op": "INVALID", "path": []})
    
    def test_apply_fails_missing_value_for_create(self):
        """CREATE via dispatcher fails without value"""
        with pytest.raises(InvalidPathError, match="requires 'value'"):
            apply_operation({}, {"op": "CREATE", "path": ["name"]})
    
    def test_apply_fails_missing_value_for_update(self):
        """UPDATE via dispatcher fails without value"""
        with pytest.raises(InvalidPathError, match="requires 'value'"):
            apply_operation({"name": "John"}, {"op": "UPDATE", "path": ["name"]})


# ============================================================
# Batch Tests
# ============================================================

class TestBatch:
    """Test batch operations"""
    
    def test_batch_multiple_creates(self):
        """Batch multiple CREATE operations"""
        data = {}
        ops = [
            {"op": "CREATE", "path": ["name"], "value": "John"},
            {"op": "CREATE", "path": ["age"], "value": 30},
            {"op": "CREATE", "path": ["email"], "value": "john@example.com"}
        ]
        result = apply_batch(data, ops)
        assert result == {
            "name": "John",
            "age": 30,
            "email": "john@example.com"
        }
    
    def test_batch_mixed_operations(self):
        """Batch mixed CRUD operations"""
        data = {"name": "John", "age": 30}
        ops = [
            {"op": "UPDATE", "path": ["name"], "value": "Jane"},
            {"op": "DELETE", "path": ["age"]},
            {"op": "CREATE", "path": ["email"], "value": "jane@example.com"}
        ]
        result = apply_batch(data, ops)
        assert result == {
            "name": "Jane",
            "email": "jane@example.com"
        }
    
    def test_batch_sequential_dependency(self):
        """Batch operations with sequential dependencies"""
        data = {}
        ops = [
            {"op": "CREATE", "path": ["user"], "value": {}},
            {"op": "CREATE", "path": ["user", "name"], "value": "John"},
            {"op": "CREATE", "path": ["user", "age"], "value": 30}
        ]
        result = apply_batch(data, ops)
        assert result == {"user": {"name": "John", "age": 30}}
    
    def test_batch_fails_on_error(self):
        """Batch fails and reports index on error"""
        data = {"name": "John"}
        ops = [
            {"op": "UPDATE", "path": ["name"], "value": "Jane"},
            {"op": "DELETE", "path": ["nonexistent"]},  # This will fail
            {"op": "CREATE", "path": ["age"], "value": 30}
        ]
        with pytest.raises(CRUDError, match="index 1"):
            apply_batch(data, ops)
    
    def test_batch_empty_operations(self):
        """Batch with empty operations list returns original"""
        data = {"name": "John"}
        result = apply_batch(data, [])
        assert result == data


# ============================================================
# Edge Cases
# ============================================================

class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_path_with_special_characters(self):
        """Handle paths with special characters"""
        data = {}
        result = create(data, ["user-name"], "John")
        assert result == {"user-name": "John"}
        assert read(result, ["user-name"]) == "John"
    
    def test_numeric_string_keys(self):
        """Handle numeric string keys in dicts"""
        data = {}
        result = create(data, ["123"], "value")
        assert result == {"123": "value"}
        assert read(result, ["123"]) == "value"
    
    def test_nested_lists(self):
        """Handle nested lists"""
        data = {"matrix": [[1, 2], [3, 4]]}
        assert read(data, ["matrix", "0", "1"]) == 2
        result = update(data, ["matrix", "1", "0"], 99)
        assert result == {"matrix": [[1, 2], [99, 4]]}
    
    def test_mixed_nesting(self):
        """Handle mixed dict/list nesting"""
        data = {
            "users": [
                {"name": "John", "tags": ["admin", "user"]},
                {"name": "Jane", "tags": ["user"]}
            ]
        }
        assert read(data, ["users", "0", "tags", "1"]) == "user"
        result = create(data, ["users", "1", "tags", "-"], "premium")
        assert result["users"][1]["tags"] == ["user", "premium"]
    
    def test_none_values(self):
        """Handle None values"""
        data = {}
        result = create(data, ["value"], None)
        assert result == {"value": None}
        assert read(result, ["value"]) is None
    
    def test_boolean_values(self):
        """Handle boolean values"""
        data = {}
        result = create(data, ["active"], True)
        assert result == {"active": True}
        result = update(result, ["active"], False)
        assert result == {"active": False}
    
    def test_empty_string_key(self):
        """Handle empty string as key"""
        data = {}
        result = create(data, [""], "value")
        assert result == {"": "value"}
    
    def test_deeply_nested_path(self):
        """Handle very deep nesting"""
        data = {"a": {"b": {"c": {"d": {"e": {}}}}}}
        result = create(data, ["a", "b", "c", "d", "e", "f"], "deep")
        assert read(result, ["a", "b", "c", "d", "e", "f"]) == "deep"


# ============================================================
# Real-World Scenarios
# ============================================================

class TestRealWorldScenarios:
    """Test real-world usage scenarios"""
    
    def test_domain_pack_entity_creation(self):
        """Simulate creating a domain pack entity"""
        data = {"entities": []}
        
        # Add entity
        entity = {
            "name": "User",
            "fields": [],
            "relationships": []
        }
        data = create(data, ["entities", "-"], entity)
        
        # Add fields
        data = create(data, ["entities", "0", "fields", "-"], {"name": "id", "type": "string"})
        data = create(data, ["entities", "0", "fields", "-"], {"name": "email", "type": "string"})
        
        assert len(data["entities"]) == 1
        assert len(data["entities"][0]["fields"]) == 2
    
    def test_config_management(self):
        """Simulate config file management"""
        config = {
            "database": {
                "host": "localhost",
                "port": 5432
            },
            "features": {
                "auth": True
            }
        }
        
        # Update config
        config = update(config, ["database", "host"], "prod.example.com")
        config = create(config, ["database", "ssl"], True)
        config = delete(config, ["features", "auth"])
        config = create(config, ["features", "logging"], {"level": "info"})
        
        assert config["database"]["host"] == "prod.example.com"
        assert config["database"]["ssl"] is True
        assert "auth" not in config["features"]
        assert config["features"]["logging"]["level"] == "info"
    
    def test_list_reordering_via_operations(self):
        """Reorder list items using CRUD operations"""
        data = {"items": ["a", "b", "c", "d"]}
        
        # Move "d" to position 1 (after "a")
        # 1. Read the value
        value = read(data, ["items", "3"])
        # 2. Delete from old position
        data = delete(data, ["items", "3"])
        # 3. Insert at new position
        data = create(data, ["items", "1"], value)
        
        assert data["items"] == ["a", "d", "b", "c"]
