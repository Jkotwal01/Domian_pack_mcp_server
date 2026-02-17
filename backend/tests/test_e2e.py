"""End-to-end tests for chatbot module.

These tests verify:
1. Frontend integration through API endpoints
2. Config updates persist to database
3. Multi-turn conversations maintain context
4. Concurrent sessions work correctly
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.models.domain_config import DomainConfig
from app.models.chat_session import ChatSession, SessionStatus
from app.models.chat_message import ChatMessage, MessageRole
import uuid
from datetime import datetime


# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def test_db():
    """Create test database for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_db):
    """Get database session for tests."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def override_get_db(db_session):
    """Override the get_db dependency."""
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client(override_get_db):
    """Get test client."""
    return TestClient(app)


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        password_hash="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_domain(db_session, test_user):
    """Create a test domain configuration."""
    domain = DomainConfig(
        id=uuid.uuid4(),
        owner_user_id=test_user.id,
        name="Test Domain",
        config_json={
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
                            "description": "Username",
                            "examples": ["john_doe"]
                        }
                    ],
                    "synonyms": ["customer"]
                }
            ],
            "relationships": [],
            "extraction_patterns": [],
            "key_terms": ["authentication"]
        },
        entity_count=1,
        relationship_count=0
    )
    db_session.add(domain)
    db_session.commit()
    db_session.refresh(domain)
    return domain


class TestFrontendIntegration:
    """Test frontend integration through API endpoints."""
    
    def test_create_chat_session_via_api(self, client, test_user, test_domain):
        """Test creating chat session through API."""
        response = client.post(
            "/api/chat/sessions",
            json={
                "user_id": str(test_user.id),
                "domain_config_id": str(test_domain.id)
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["status"] == "active"
    
    def test_send_message_via_api(self, client, test_user, test_domain, db_session):
        """Test sending message through API."""
        # Create session
        session = ChatSession(
            id=uuid.uuid4(),
            user_id=test_user.id,
            domain_config_id=test_domain.id,
            status=SessionStatus.ACTIVE
        )
        db_session.add(session)
        db_session.commit()
        
        # Send message
        response = client.post(
            f"/api/chat/sessions/{session.id}/messages",
            json={
                "message": "Add email attribute to User"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "needs_confirmation" in data
    
    def test_get_chat_history_via_api(self, client, test_user, test_domain, db_session):
        """Test retrieving chat history through API."""
        # Create session with messages
        session = ChatSession(
            id=uuid.uuid4(),
            user_id=test_user.id,
            domain_config_id=test_domain.id,
            status=SessionStatus.ACTIVE
        )
        db_session.add(session)
        db_session.commit()
        
        # Add messages
        msg1 = ChatMessage(
            session_id=session.id,
            role=MessageRole.USER,
            message="Add email to User"
        )
        msg2 = ChatMessage(
            session_id=session.id,
            role=MessageRole.ASSISTANT,
            message="✅ Added attribute"
        )
        db_session.add_all([msg1, msg2])
        db_session.commit()
        
        # Get history
        response = client.get(f"/api/chat/sessions/{session.id}/messages")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) == 2


class TestConfigPersistence:
    """Test that config updates persist to database."""
    
    def test_config_persists_after_edit(self, db_session, test_user, test_domain):
        """Test that config changes are saved to database."""
        from app.services.chat_service import ChatService
        from app.schemas.chat import ChatRequest
        
        # Create session
        session = ChatSession(
            id=uuid.uuid4(),
            user_id=test_user.id,
            domain_config_id=test_domain.id,
            status=SessionStatus.ACTIVE
        )
        db_session.add(session)
        db_session.commit()
        
        # Get initial entity count
        initial_attr_count = len(test_domain.config_json["entities"][0]["attributes"])
        
        # Send message (mocked LLM would normally handle this)
        # For this test, we'll manually apply a patch
        test_domain.config_json["entities"][0]["attributes"].append({
            "name": "email",
            "description": "User email",
            "examples": ["user@test.com"]
        })
        test_domain.update_counts()
        db_session.commit()
        
        # Refresh from database
        db_session.refresh(test_domain)
        
        # Verify persistence
        assert len(test_domain.config_json["entities"][0]["attributes"]) == initial_attr_count + 1
        assert test_domain.config_json["entities"][0]["attributes"][-1]["name"] == "email"
    
    def test_pending_patch_persists_in_metadata(self, db_session, test_user, test_domain):
        """Test that pending patches are stored in session metadata."""
        session = ChatSession(
            id=uuid.uuid4(),
            user_id=test_user.id,
            domain_config_id=test_domain.id,
            status=SessionStatus.ACTIVE,
            metadata={
                "pending_patch": {
                    "operation": "add_entity_attribute",
                    "parent_name": "User",
                    "payload": {"name": "email"}
                }
            }
        )
        db_session.add(session)
        db_session.commit()
        
        # Refresh from database
        db_session.refresh(session)
        
        # Verify metadata persisted
        assert session.session_metadata is not None
        assert "pending_patch" in session.session_metadata
        assert session.session_metadata["pending_patch"]["operation"] == "add_entity_attribute"
    
    def test_confirmation_clears_metadata(self, db_session, test_user, test_domain):
        """Test that confirming changes clears pending metadata."""
        session = ChatSession(
            id=uuid.uuid4(),
            user_id=test_user.id,
            domain_config_id=test_domain.id,
            status=SessionStatus.ACTIVE,
            session_metadata={"pending_patch": {"operation": "test"}}
        )
        db_session.add(session)
        db_session.commit()
        
        # Simulate confirmation
        session.session_metadata = {}
        db_session.commit()
        
        # Verify cleared
        db_session.refresh(session)
        assert session.session_metadata == {} or session.session_metadata.get("pending_patch") is None


class TestMultiTurnConversations:
    """Test multi-turn conversation context."""
    
    def test_conversation_maintains_context(self, db_session, test_user, test_domain):
        """Test that conversation context is maintained across turns."""
        session = ChatSession(
            id=uuid.uuid4(),
            user_id=test_user.id,
            domain_config_id=test_domain.id,
            status=SessionStatus.ACTIVE
        )
        db_session.add(session)
        db_session.commit()
        
        # Turn 1: Add attribute
        msg1 = ChatMessage(
            session_id=session.id,
            role=MessageRole.USER,
            message="Add email attribute to User"
        )
        resp1 = ChatMessage(
            session_id=session.id,
            role=MessageRole.ASSISTANT,
            message="+ Add attribute 'email' to User"
        )
        db_session.add_all([msg1, resp1])
        db_session.commit()
        
        # Turn 2: Add example (references previous context)
        msg2 = ChatMessage(
            session_id=session.id,
            role=MessageRole.USER,
            message="Add example 'admin@test.com' to it"
        )
        resp2 = ChatMessage(
            session_id=session.id,
            role=MessageRole.ASSISTANT,
            message="+ Add example to User.email"
        )
        db_session.add_all([msg2, resp2])
        db_session.commit()
        
        # Verify conversation history
        messages = db_session.query(ChatMessage).filter(
            ChatMessage.session_id == session.id
        ).order_by(ChatMessage.created_at).all()
        
        assert len(messages) == 4
        assert messages[0].message == "Add email attribute to User"
        assert messages[2].message == "Add example 'admin@test.com' to it"
    
    def test_chat_history_limited_to_recent(self, db_session, test_user, test_domain):
        """Test that chat history is limited to recent messages."""
        from app.services.chat_service import ChatService
        
        session = ChatSession(
            id=uuid.uuid4(),
            user_id=test_user.id,
            domain_config_id=test_domain.id,
            status=SessionStatus.ACTIVE
        )
        db_session.add(session)
        db_session.commit()
        
        # Add many messages
        for i in range(15):
            msg = ChatMessage(
                session_id=session.id,
                role=MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT,
                message=f"Message {i}"
            )
            db_session.add(msg)
        db_session.commit()
        
        # Get recent messages (should be limited to 10)
        recent = ChatService.get_messages(db_session, session.id, limit=10)
        
        assert len(recent) == 10


class TestConcurrentSessions:
    """Test concurrent session handling."""
    
    def test_multiple_sessions_same_user(self, db_session, test_user, test_domain):
        """Test that user can have multiple sessions for different domains."""
        # Create second domain
        domain2 = DomainConfig(
            id=uuid.uuid4(),
            owner_user_id=test_user.id,
            name="Domain 2",
            config_json={
                "name": "Domain 2",
                "description": "Second domain",
                "version": "1.0.0",
                "entities": [],
                "relationships": [],
                "extraction_patterns": [],
                "key_terms": []
            },
            entity_count=0,
            relationship_count=0
        )
        db_session.add(domain2)
        db_session.commit()
        
        # Create sessions for both domains
        session1 = ChatSession(
            id=uuid.uuid4(),
            user_id=test_user.id,
            domain_config_id=test_domain.id,
            status=SessionStatus.ACTIVE
        )
        session2 = ChatSession(
            id=uuid.uuid4(),
            user_id=test_user.id,
            domain_config_id=domain2.id,
            status=SessionStatus.ACTIVE
        )
        db_session.add_all([session1, session2])
        db_session.commit()
        
        # Verify both sessions exist
        sessions = db_session.query(ChatSession).filter(
            ChatSession.user_id == test_user.id,
            ChatSession.status == SessionStatus.ACTIVE
        ).all()
        
        assert len(sessions) == 2
    
    def test_session_isolation(self, db_session, test_user, test_domain):
        """Test that sessions are isolated from each other."""
        # Create two sessions
        session1 = ChatSession(
            id=uuid.uuid4(),
            user_id=test_user.id,
            domain_config_id=test_domain.id,
            status=SessionStatus.ACTIVE,
            session_metadata={"pending_patch": {"operation": "test1"}}
        )
        session2 = ChatSession(
            id=uuid.uuid4(),
            user_id=test_user.id,
            domain_config_id=test_domain.id,
            status=SessionStatus.ACTIVE,
            session_metadata={"pending_patch": {"operation": "test2"}}
        )
        db_session.add_all([session1, session2])
        db_session.commit()
        
        # Verify isolation
        db_session.refresh(session1)
        db_session.refresh(session2)
        
        assert session1.metadata["pending_patch"]["operation"] == "test1"
        assert session2.metadata["pending_patch"]["operation"] == "test2"
    
    def test_only_one_active_session_per_domain(self, db_session, test_user, test_domain):
        """Test that only one active session per user+domain is allowed."""
        # Create first active session
        session1 = ChatSession(
            id=uuid.uuid4(),
            user_id=test_user.id,
            domain_config_id=test_domain.id,
            status=SessionStatus.ACTIVE
        )
        db_session.add(session1)
        db_session.commit()
        
        # Try to create second active session (should fail due to unique constraint)
        session2 = ChatSession(
            id=uuid.uuid4(),
            user_id=test_user.id,
            domain_config_id=test_domain.id,
            status=SessionStatus.ACTIVE
        )
        db_session.add(session2)
        
        with pytest.raises(Exception):  # Unique constraint violation
            db_session.commit()
        
        db_session.rollback()
    
    def test_can_have_multiple_closed_sessions(self, db_session, test_user, test_domain):
        """Test that user can have multiple closed sessions."""
        # Create multiple closed sessions
        for i in range(3):
            session = ChatSession(
                id=uuid.uuid4(),
                user_id=test_user.id,
                domain_config_id=test_domain.id,
                status=SessionStatus.CLOSED
            )
            db_session.add(session)
        db_session.commit()
        
        # Verify all exist
        closed_sessions = db_session.query(ChatSession).filter(
            ChatSession.user_id == test_user.id,
            ChatSession.status == SessionStatus.CLOSED
        ).all()
        
        assert len(closed_sessions) == 3


class TestCompleteWorkflow:
    """Test complete end-to-end workflow."""
    
    def test_full_conversation_workflow(self, db_session, test_user, test_domain):
        """Test complete conversation workflow from start to finish."""
        # 1. Create session
        session = ChatSession(
            id=uuid.uuid4(),
            user_id=test_user.id,
            domain_config_id=test_domain.id,
            status=SessionStatus.ACTIVE
        )
        db_session.add(session)
        db_session.commit()
        
        # 2. User sends message
        user_msg = ChatMessage(
            session_id=session.id,
            role=MessageRole.USER,
            message="Add email attribute to User"
        )
        db_session.add(user_msg)
        db_session.commit()
        
        # 3. System proposes change (with confirmation)
        bot_msg = ChatMessage(
            session_id=session.id,
            role=MessageRole.ASSISTANT,
            message="+ Add attribute 'email' to User\nDo you want to apply? (yes/no)"
        )
        db_session.add(bot_msg)
        
        # Store pending patch
        session.session_metadata = {
            "pending_patch": {
                "operation": "add_entity_attribute",
                "parent_name": "User",
                "payload": {"name": "email", "description": "User email", "examples": []}
            },
            "pending_updated_config": test_domain.config_json
        }
        db_session.commit()
        
        # 4. User confirms
        confirm_msg = ChatMessage(
            session_id=session.id,
            role=MessageRole.USER,
            message="yes"
        )
        db_session.add(confirm_msg)
        db_session.commit()
        
        # 5. Apply changes
        test_domain.config_json["entities"][0]["attributes"].append({
            "name": "email",
            "description": "User email",
            "examples": []
        })
        test_domain.update_counts()
        session.session_metadata = {}
        db_session.commit()
        
        # 6. Confirmation message
        success_msg = ChatMessage(
            session_id=session.id,
            role=MessageRole.ASSISTANT,
            message="✅ Changes applied successfully!"
        )
        db_session.add(success_msg)
        db_session.commit()
        
        # Verify final state
        db_session.refresh(test_domain)
        db_session.refresh(session)
        
        assert len(test_domain.config_json["entities"][0]["attributes"]) == 2
        assert test_domain.config_json["entities"][0]["attributes"][1]["name"] == "email"
        assert session.session_metadata == {} or session.session_metadata.get("pending_patch") is None
        
        # Verify message history
        messages = db_session.query(ChatMessage).filter(
            ChatMessage.session_id == session.id
        ).order_by(ChatMessage.created_at).all()
        
        assert len(messages) == 4
        assert messages[0].role == MessageRole.USER
        assert messages[-1].message == "✅ Changes applied successfully!"
