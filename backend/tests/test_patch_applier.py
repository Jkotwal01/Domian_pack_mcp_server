"""Unit tests for patch applier utilities."""
import pytest
from app.utils.patch_applier import (
    apply_patch,
    add_entity,
    update_entity_name,
    add_entity_attribute,
    add_entity_attribute_example,
    add_entity_synonym,
    add_relationship,
    update_relationship_from,
    delete_entity
)
from app.schemas.patch import PatchOperation


@pytest.fixture
def sample_config():
    """Sample domain configuration for testing."""
    return {
        "name": "Test Domain",
        "description": "Test description",
        "version": "1.0.0",
        "entities": [
            {
                "name": "User",
                "type": "person",
                "description": "A user entity",
                "attributes": [
                    {
                        "name": "username",
                        "description": "User's username",
                        "examples": ["john_doe"]
                    }
                ],
                "synonyms": ["customer"]
            },
            {
                "name": "Product",
                "type": "item",
                "description": "A product entity",
                "attributes": [],
                "synonyms": []
            }
        ],
        "relationships": [
            {
                "name": "OWNS",
                "from": "User",
                "to": "Product",
                "description": "User owns product",
                "attributes": []
            }
        ],
        "extraction_patterns": [],
        "key_terms": ["authentication", "authorization"]
    }


class TestEntityOperations:
    """Test entity-level operations."""
    
    def test_add_entity(self, sample_config):
        """Test adding a new entity."""
        patch = PatchOperation(
            operation="add_entity",
            payload={
                "name": "Order",
                "type": "transaction",
                "description": "An order entity",
                "attributes": [],
                "synonyms": []
            }
        )
        
        result = apply_patch(sample_config, patch)
        assert len(result["entities"]) == 3
        assert result["entities"][2]["name"] == "Order"
    
    def test_add_duplicate_entity_fails(self, sample_config):
        """Test that adding duplicate entity raises error."""
        patch = PatchOperation(
            operation="add_entity",
            payload={
                "name": "User",
                "type": "person",
                "description": "Duplicate",
                "attributes": [],
                "synonyms": []
            }
        )
        
        with pytest.raises(ValueError, match="already exists"):
            apply_patch(sample_config, patch)
    
    def test_update_entity_name(self, sample_config):
        """Test renaming an entity."""
        patch = PatchOperation(
            operation="update_entity_name",
            target_name="User",
            new_value="Customer"
        )
        
        result = apply_patch(sample_config, patch)
        assert result["entities"][0]["name"] == "Customer"
        # Check cascade update in relationships
        assert result["relationships"][0]["from"] == "Customer"
    
    def test_delete_entity_with_relationship_fails(self, sample_config):
        """Test that deleting entity referenced in relationship fails."""
        patch = PatchOperation(
            operation="delete_entity",
            target_name="User"
        )
        
        with pytest.raises(ValueError, match="referenced in relationship"):
            apply_patch(sample_config, patch)


class TestEntityAttributeOperations:
    """Test entity attribute operations."""
    
    def test_add_entity_attribute(self, sample_config):
        """Test adding attribute to entity."""
        patch = PatchOperation(
            operation="add_entity_attribute",
            parent_name="User",
            payload={
                "name": "email",
                "description": "User email",
                "examples": ["user@example.com"]
            }
        )
        
        result = apply_patch(sample_config, patch)
        user_attrs = result["entities"][0]["attributes"]
        assert len(user_attrs) == 2
        assert user_attrs[1]["name"] == "email"
    
    def test_add_duplicate_attribute_fails(self, sample_config):
        """Test that adding duplicate attribute fails."""
        patch = PatchOperation(
            operation="add_entity_attribute",
            parent_name="User",
            payload={
                "name": "username",
                "description": "Duplicate",
                "examples": []
            }
        )
        
        with pytest.raises(ValueError, match="already exists"):
            apply_patch(sample_config, patch)
    
    def test_add_entity_attribute_example(self, sample_config):
        """Test adding example to attribute."""
        patch = PatchOperation(
            operation="add_entity_attribute_example",
            parent_name="User",
            attribute_name="username",
            new_value="jane_doe"
        )
        
        result = apply_patch(sample_config, patch)
        examples = result["entities"][0]["attributes"][0]["examples"]
        assert "jane_doe" in examples
        assert len(examples) == 2


class TestEntitySynonymOperations:
    """Test entity synonym operations."""
    
    def test_add_entity_synonym(self, sample_config):
        """Test adding synonym to entity."""
        patch = PatchOperation(
            operation="add_entity_synonym",
            parent_name="User",
            new_value="client"
        )
        
        result = apply_patch(sample_config, patch)
        synonyms = result["entities"][0]["synonyms"]
        assert "client" in synonyms
        assert len(synonyms) == 2
    
    def test_update_entity_synonym(self, sample_config):
        """Test updating entity synonym."""
        patch = PatchOperation(
            operation="update_entity_synonym",
            parent_name="User",
            old_value="customer",
            new_value="client"
        )
        
        result = apply_patch(sample_config, patch)
        synonyms = result["entities"][0]["synonyms"]
        assert "client" in synonyms
        assert "customer" not in synonyms
    
    def test_delete_entity_synonym(self, sample_config):
        """Test deleting entity synonym."""
        patch = PatchOperation(
            operation="delete_entity_synonym",
            parent_name="User",
            old_value="customer"
        )
        
        result = apply_patch(sample_config, patch)
        synonyms = result["entities"][0]["synonyms"]
        assert "customer" not in synonyms


class TestRelationshipOperations:
    """Test relationship operations."""
    
    def test_add_relationship(self, sample_config):
        """Test adding a new relationship."""
        patch = PatchOperation(
            operation="add_relationship",
            payload={
                "name": "PURCHASES",
                "from": "User",
                "to": "Product",
                "description": "User purchases product",
                "attributes": []
            }
        )
        
        result = apply_patch(sample_config, patch)
        assert len(result["relationships"]) == 2
        assert result["relationships"][1]["name"] == "PURCHASES"
    
    def test_add_relationship_invalid_entity_fails(self, sample_config):
        """Test that adding relationship with invalid entity fails."""
        patch = PatchOperation(
            operation="add_relationship",
            payload={
                "name": "INVALID",
                "from": "NonExistent",
                "to": "Product",
                "description": "Invalid",
                "attributes": []
            }
        )
        
        with pytest.raises(ValueError, match="does not exist"):
            apply_patch(sample_config, patch)
    
    def test_update_relationship_from(self, sample_config):
        """Test updating relationship source entity."""
        # First add another entity
        sample_config["entities"].append({
            "name": "Admin",
            "type": "person",
            "description": "Admin user",
            "attributes": [],
            "synonyms": []
        })
        
        patch = PatchOperation(
            operation="update_relationship_from",
            target_name="OWNS",
            new_value="Admin"
        )
        
        result = apply_patch(sample_config, patch)
        assert result["relationships"][0]["from"] == "Admin"


class TestKeyTermOperations:
    """Test key term operations."""
    
    def test_add_key_term(self, sample_config):
        """Test adding a key term."""
        patch = PatchOperation(
            operation="add_key_term",
            new_value="encryption"
        )
        
        result = apply_patch(sample_config, patch)
        assert "encryption" in result["key_terms"]
        assert len(result["key_terms"]) == 3
    
    def test_update_key_term(self, sample_config):
        """Test updating a key term."""
        patch = PatchOperation(
            operation="update_key_term",
            old_value="authentication",
            new_value="auth"
        )
        
        result = apply_patch(sample_config, patch)
        assert "auth" in result["key_terms"]
        assert "authentication" not in result["key_terms"]
    
    def test_delete_key_term(self, sample_config):
        """Test deleting a key term."""
        patch = PatchOperation(
            operation="delete_key_term",
            old_value="authentication"
        )
        
        result = apply_patch(sample_config, patch)
        assert "authentication" not in result["key_terms"]
        assert len(result["key_terms"]) == 1


class TestDomainOperations:
    """Test domain-level operations."""
    
    def test_update_domain_name(self, sample_config):
        """Test updating domain name."""
        patch = PatchOperation(
            operation="update_domain_name",
            new_value="New Domain Name"
        )
        
        result = apply_patch(sample_config, patch)
        assert result["name"] == "New Domain Name"
    
    def test_update_domain_description(self, sample_config):
        """Test updating domain description."""
        patch = PatchOperation(
            operation="update_domain_description",
            new_value="New description"
        )
        
        result = apply_patch(sample_config, patch)
        assert result["description"] == "New description"
    
    def test_update_domain_version(self, sample_config):
        """Test updating domain version."""
        patch = PatchOperation(
            operation="update_domain_version",
            new_value="2.0.0"
        )
        
        result = apply_patch(sample_config, patch)
        assert result["version"] == "2.0.0"
