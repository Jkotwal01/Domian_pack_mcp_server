"""
Integration test to verify CRUD operations work through the entire backend stack
"""

import pytest
from app.logic.operations import (
    create, read, update, delete,
    apply_operation, apply_batch,
    CRUDError, OperationError
)


def test_backward_compatibility_imports():
    """Verify backward compatibility - operations.py re-exports work"""
    # All functions should be importable
    assert callable(create)
    assert callable(read)
    assert callable(update)
    assert callable(delete)
    assert callable(apply_operation)
    assert callable(apply_batch)
    
    # Exception aliases work
    assert OperationError is CRUDError


def test_operations_via_old_module():
    """Test that operations work when imported from operations.py"""
    # This simulates old code using the operations module
    data = {}
    
    # CREATE
    data = create(data, ["name"], "John")
    assert data == {"name": "John"}
    
    # READ
    value = read(data, ["name"])
    assert value == "John"
    
    # UPDATE
    data = update(data, ["name"], "Jane")
    assert data == {"name": "Jane"}
    
    # CREATE another field
    data = create(data, ["age"], 30)
    assert data == {"name": "Jane", "age": 30}
    
    # DELETE
    data = delete(data, ["age"])
    assert data == {"name": "Jane"}


def test_apply_operation_dispatcher():
    """Test operation dispatcher with new CRUD format"""
    data = {}
    
    # CREATE operation
    result = apply_operation(data, {
        "op": "CREATE",
        "path": ["user"],
        "value": {"name": "John"}
    })
    assert result == {"user": {"name": "John"}}
    
    # UPDATE operation
    result = apply_operation(result, {
        "op": "UPDATE",
        "path": ["user", "name"],
        "value": "Jane"
    })
    assert result == {"user": {"name": "Jane"}}
    
    # READ operation
    value = apply_operation(result, {
        "op": "READ",
        "path": ["user", "name"]
    })
    assert value == "Jane"
    
    # DELETE operation
    result = apply_operation(result, {
        "op": "DELETE",
        "path": ["user", "name"]
    })
    assert result == {"user": {}}


def test_apply_batch_integration():
    """Test batch operations through operations.py"""
    data = {}
    
    operations = [
        {"op": "CREATE", "path": ["entities"], "value": []},
        {"op": "CREATE", "path": ["entities", "-"], "value": {"name": "User", "fields": []}},
        {"op": "CREATE", "path": ["entities", "0", "fields", "-"], "value": "id"},
        {"op": "CREATE", "path": ["entities", "0", "fields", "-"], "value": "name"},
    ]
    
    result = apply_batch(data, operations)
    
    assert result == {
        "entities": [
            {
                "name": "User",
                "fields": ["id", "name"]
            }
        ]
    }


def test_error_handling_backward_compatibility():
    """Test that OperationError alias works for backward compatibility"""
    data = {"name": "John"}
    
    # Old code might catch OperationError
    with pytest.raises(OperationError):
        create(data, ["name"], "Jane")  # Key already exists
    
    # Should be the same as CRUDError
    with pytest.raises(CRUDError):
        create(data, ["name"], "Jane")


def test_domain_pack_scenario():
    """Test a real domain pack editing scenario"""
    # Start with empty domain pack structure
    domain_pack = {
        "version": "1.0.0",
        "entities": [],
        "relationships": []
    }
    
    # Add an entity
    domain_pack = create(domain_pack, ["entities", "-"], {
        "name": "User",
        "fields": [],
        "methods": []
    })
    
    # Add fields to the entity
    domain_pack = create(domain_pack, ["entities", "0", "fields", "-"], {
        "name": "id",
        "type": "string",
        "required": True
    })
    
    domain_pack = create(domain_pack, ["entities", "0", "fields", "-"], {
        "name": "email",
        "type": "string",
        "required": True
    })
    
    # Update a field
    domain_pack = update(domain_pack, ["entities", "0", "fields", "0", "type"], "uuid")
    
    # Verify structure
    assert len(domain_pack["entities"]) == 1
    assert domain_pack["entities"][0]["name"] == "User"
    assert len(domain_pack["entities"][0]["fields"]) == 2
    assert domain_pack["entities"][0]["fields"][0]["type"] == "uuid"
    assert domain_pack["entities"][0]["fields"][1]["name"] == "email"
    
    # Delete a field
    domain_pack = delete(domain_pack, ["entities", "0", "fields", "1"])
    assert len(domain_pack["entities"][0]["fields"]) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
