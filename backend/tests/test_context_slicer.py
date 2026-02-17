"""Unit tests for context slicing utilities."""
import pytest
from app.utils.context_slicer import (
    get_relevant_entities,
    get_relevant_relationships,
    format_minimal_context,
    extract_target_from_message,
    get_context_size_reduction
)
import json


@pytest.fixture
def sample_config():
    """Sample domain configuration for testing."""
    return {
        "name": "E-Commerce",
        "description": "E-commerce domain",
        "version": "1.0.0",
        "entities": [
            {
                "name": "User",
                "type": "person",
                "description": "A user",
                "attributes": [
                    {"name": "email", "description": "Email", "examples": ["user@test.com"]}
                ],
                "synonyms": ["customer"]
            },
            {
                "name": "Product",
                "type": "item",
                "description": "A product",
                "attributes": [],
                "synonyms": []
            },
            {
                "name": "Order",
                "type": "transaction",
                "description": "An order",
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
            },
            {
                "name": "PLACES",
                "from": "User",
                "to": "Order",
                "description": "User places order",
                "attributes": []
            }
        ],
        "extraction_patterns": [],
        "key_terms": ["checkout", "payment"]
    }


class TestGetRelevantEntities:
    """Test get_relevant_entities function."""
    
    def test_get_single_entity(self, sample_config):
        """Test extracting a single entity."""
        result = get_relevant_entities(sample_config, ["User"])
        assert len(result) == 1
        assert result[0]["name"] == "User"
    
    def test_get_multiple_entities(self, sample_config):
        """Test extracting multiple entities."""
        result = get_relevant_entities(sample_config, ["User", "Product"])
        assert len(result) == 2
        names = [e["name"] for e in result]
        assert "User" in names
        assert "Product" in names
    
    def test_get_nonexistent_entity(self, sample_config):
        """Test extracting non-existent entity returns empty."""
        result = get_relevant_entities(sample_config, ["NonExistent"])
        assert len(result) == 0


class TestGetRelevantRelationships:
    """Test get_relevant_relationships function."""
    
    def test_get_by_relationship_name(self, sample_config):
        """Test extracting relationship by name."""
        result = get_relevant_relationships(sample_config, relationship_names=["OWNS"])
        assert len(result) == 1
        assert result[0]["name"] == "OWNS"
    
    def test_get_by_entity_name(self, sample_config):
        """Test extracting relationships connected to entity."""
        result = get_relevant_relationships(sample_config, entity_names=["User"])
        assert len(result) == 2  # Both OWNS and PLACES involve User
    
    def test_get_by_specific_entity(self, sample_config):
        """Test extracting relationships for specific entity."""
        result = get_relevant_relationships(sample_config, entity_names=["Product"])
        assert len(result) == 1
        assert result[0]["name"] == "OWNS"


class TestFormatMinimalContext:
    """Test format_minimal_context function."""
    
    def test_domain_intent(self, sample_config):
        """Test formatting for domain-level intent."""
        result = format_minimal_context(sample_config, "update_domain_name")
        data = json.loads(result)
        assert "name" in data
        assert "description" in data
        assert "version" in data
        assert "entities" not in data  # Should not include entities
    
    def test_entity_intent_with_target(self, sample_config):
        """Test formatting for entity intent with target."""
        result = format_minimal_context(sample_config, "add_entity_attribute", "User")
        data = json.loads(result)
        assert "entity" in data
        assert data["entity"]["name"] == "User"
    
    def test_entity_intent_without_target(self, sample_config):
        """Test formatting for entity intent without target."""
        result = format_minimal_context(sample_config, "add_entity")
        data = json.loads(result)
        assert "entity_names" in data
        assert "User" in data["entity_names"]
    
    def test_relationship_intent_with_target(self, sample_config):
        """Test formatting for relationship intent with target."""
        result = format_minimal_context(sample_config, "update_relationship_from", "OWNS")
        data = json.loads(result)
        assert "relationship" in data
        assert data["relationship"]["name"] == "OWNS"
        assert "available_entities" in data
    
    def test_key_term_intent(self, sample_config):
        """Test formatting for key term intent."""
        result = format_minimal_context(sample_config, "add_key_term")
        data = json.loads(result)
        assert "key_terms" in data
        assert "checkout" in data["key_terms"]


class TestExtractTargetFromMessage:
    """Test extract_target_from_message function."""
    
    def test_extract_entity_name(self, sample_config):
        """Test extracting entity name from message."""
        message = "Add email attribute to User"
        result = extract_target_from_message(message, sample_config)
        assert result == "User"
    
    def test_extract_relationship_name(self, sample_config):
        """Test extracting relationship name from message."""
        message = "Change OWNS from User to Admin"
        result = extract_target_from_message(message, sample_config)
        # Should match either OWNS or User, both are valid
        assert result in ["OWNS", "User"]
    
    def test_no_target_in_message(self, sample_config):
        """Test when no target is in message."""
        message = "Add a new entity"
        result = extract_target_from_message(message, sample_config)
        assert result is None


class TestContextSizeReduction:
    """Test get_context_size_reduction function."""
    
    def test_size_reduction_calculation(self, sample_config):
        """Test that size reduction is calculated correctly."""
        minimal_context = format_minimal_context(sample_config, "add_entity_attribute", "User")
        stats = get_context_size_reduction(sample_config, minimal_context)
        
        assert "full_size_bytes" in stats
        assert "minimal_size_bytes" in stats
        assert "reduction_bytes" in stats
        assert "reduction_percentage" in stats
        
        # Minimal context should be significantly smaller
        assert stats["minimal_size_bytes"] < stats["full_size_bytes"]
        assert stats["reduction_percentage"] > 50  # At least 50% reduction
    
    def test_domain_intent_high_reduction(self, sample_config):
        """Test that domain-level intents have high reduction."""
        minimal_context = format_minimal_context(sample_config, "update_domain_name")
        stats = get_context_size_reduction(sample_config, minimal_context)
        
        # Domain metadata is tiny compared to full config
        assert stats["reduction_percentage"] > 90
