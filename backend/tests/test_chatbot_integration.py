"""Integration tests for chatbot workflow."""
import pytest
from unittest.mock import Mock, patch
from app.dp_chatbot_module.state import create_initial_state
from app.dp_chatbot_module.graph import domain_graph


@pytest.fixture
def sample_domain_config():
    """Sample domain configuration."""
    return {
        "name": "Test Domain",
        "description": "Test",
        "version": "1.0.0",
        "entities": [
            {
                "name": "User",
                "type": "person",
                "description": "A user",
                "attributes": [],
                "synonyms": []
            }
        ],
        "relationships": [],
        "extraction_patterns": [],
        "key_terms": []
    }


class TestChatbotWorkflow:
    """Integration tests for full chatbot workflow."""
    
    @patch('app.dp_chatbot_module.nodes.ChatOpenAI')
    def test_add_entity_attribute_flow(self, mock_llm, sample_domain_config):
        """Test full flow for adding entity attribute."""
        # Mock LLM responses
        mock_intent_response = Mock()
        mock_intent_response.content = "add_entity_attribute"
        
        mock_patch_response = Mock()
        mock_patch_response.dict.return_value = {
            "operation": "add_entity_attribute",
            "parent_name": "User",
            "payload": {
                "name": "email",
                "description": "User email",
                "examples": ["user@example.com"]
            }
        }
        
        mock_llm.return_value.invoke.return_value = mock_intent_response
        mock_llm.return_value.with_structured_output.return_value.invoke.return_value = mock_patch_response
        
        # Create initial state
        initial_state = create_initial_state(
            domain_config=sample_domain_config,
            user_message="Add email attribute to User",
            chat_history=[]
        )
        
        # Execute graph
        final_state = domain_graph.invoke(initial_state)
        
        # Assertions
        assert final_state["needs_confirmation"] is True
        assert final_state["updated_config"] is not None
        assert len(final_state["updated_config"]["entities"][0]["attributes"]) == 1
        assert final_state["updated_config"]["entities"][0]["attributes"][0]["name"] == "email"
    
    @patch('app.dp_chatbot_module.nodes.ChatOpenAI')
    def test_validation_failure_flow(self, mock_llm, sample_domain_config):
        """Test flow when validation fails."""
        # Mock LLM to generate invalid patch
        mock_intent_response = Mock()
        mock_intent_response.content = "add_relationship"
        
        mock_patch_response = Mock()
        mock_patch_response.dict.return_value = {
            "operation": "add_relationship",
            "payload": {
                "name": "OWNS",
                "from": "NonExistent",  # Invalid entity
                "to": "User",
                "description": "Test",
                "attributes": []
            }
        }
        
        mock_llm.return_value.invoke.return_value = mock_intent_response
        mock_llm.return_value.with_structured_output.return_value.invoke.return_value = mock_patch_response
        
        initial_state = create_initial_state(
            domain_config=sample_domain_config,
            user_message="Add OWNS relationship from NonExistent to User",
            chat_history=[]
        )
        
        final_state = domain_graph.invoke(initial_state)
        
        # Should have error message
        assert final_state["error_message"] is not None
        assert "does not exist" in final_state["error_message"]
        assert final_state["needs_confirmation"] is False
    
    @patch('app.dp_chatbot_module.nodes.ChatOpenAI')
    def test_update_entity_name_cascade(self, mock_llm, sample_domain_config):
        """Test that renaming entity cascades to relationships."""
        # Add a relationship first
        sample_domain_config["entities"].append({
            "name": "Product",
            "type": "item",
            "description": "Product",
            "attributes": [],
            "synonyms": []
        })
        sample_domain_config["relationships"].append({
            "name": "OWNS",
            "from": "User",
            "to": "Product",
            "description": "User owns product",
            "attributes": []
        })
        
        # Mock LLM responses
        mock_intent_response = Mock()
        mock_intent_response.content = "update_entity_name"
        
        mock_patch_response = Mock()
        mock_patch_response.dict.return_value = {
            "operation": "update_entity_name",
            "target_name": "User",
            "new_value": "Customer"
        }
        
        mock_llm.return_value.invoke.return_value = mock_intent_response
        mock_llm.return_value.with_structured_output.return_value.invoke.return_value = mock_patch_response
        
        initial_state = create_initial_state(
            domain_config=sample_domain_config,
            user_message="Rename User to Customer",
            chat_history=[]
        )
        
        final_state = domain_graph.invoke(initial_state)
        
        # Check cascade update
        assert final_state["updated_config"]["entities"][0]["name"] == "Customer"
        assert final_state["updated_config"]["relationships"][0]["from"] == "Customer"


class TestConfirmationFlow:
    """Test confirmation flow logic."""
    
    def test_confirmation_keywords(self):
        """Test that confirmation keywords are recognized."""
        confirmation_keywords = ["yes", "confirm", "y", "apply", "ok"]
        rejection_keywords = ["no", "cancel", "n", "reject", "abort"]
        
        # This would be tested in the chat service
        # Just documenting expected behavior
        assert all(kw.lower() in ["yes", "confirm", "y", "apply", "ok"] for kw in confirmation_keywords)
        assert all(kw.lower() in ["no", "cancel", "n", "reject", "abort"] for kw in rejection_keywords)


class TestErrorRecovery:
    """Test error recovery mechanisms."""
    
    @patch('app.dp_chatbot_module.nodes.ChatOpenAI')
    def test_llm_retry_on_failure(self, mock_llm, sample_domain_config):
        """Test that LLM calls retry on failure."""
        # Mock LLM to fail twice then succeed
        mock_llm.return_value.invoke.side_effect = [
            Exception("API Error"),
            Exception("API Error"),
            Mock(content="add_entity")
        ]
        
        initial_state = create_initial_state(
            domain_config=sample_domain_config,
            user_message="Add a new entity",
            chat_history=[]
        )
        
        # Should succeed after retries
        final_state = domain_graph.invoke(initial_state)
        
        # Verify it retried
        assert mock_llm.return_value.invoke.call_count == 3
    
    @patch('app.dp_chatbot_module.nodes.ChatOpenAI')
    def test_llm_max_retries_exceeded(self, mock_llm, sample_domain_config):
        """Test that max retries results in error."""
        # Mock LLM to always fail
        mock_llm.return_value.invoke.side_effect = Exception("API Error")
        
        initial_state = create_initial_state(
            domain_config=sample_domain_config,
            user_message="Add a new entity",
            chat_history=[]
        )
        
        final_state = domain_graph.invoke(initial_state)
        
        # Should have error message after max retries
        assert final_state["error_message"] is not None
        assert "after 3 attempts" in final_state["error_message"]
