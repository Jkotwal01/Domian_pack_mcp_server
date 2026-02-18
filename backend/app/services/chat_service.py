"""Chat service for managing chat sessions and executing LangGraph."""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Dict, Any
from uuid import UUID
from datetime import datetime
from app.models.chat_session import ChatSession, SessionStatus
from app.models.chat_message import ChatMessage, MessageRole
from app.models.domain_config import DomainConfig
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.dp_chatbot_module.graph import domain_graph
from app.dp_chatbot_module.state import create_initial_state
from app.services.domain_service import DomainService


class ChatService:
    """Service for chat session and message management."""
    
    MAX_MESSAGES_PER_SESSION = 100
    CONTEXT_MESSAGE_COUNT = 4  # Reduced from 10 to minimize token usage
    
    @staticmethod
    def create_or_get_session(
        db: Session,
        domain_config_id: UUID,
        user: User
    ) -> ChatSession:
        """
        Create a new chat session or get existing active session.
        
        Args:
            db: Database session
            domain_config_id: Domain configuration ID
            user: Current user
            
        Returns:
            Chat session
        """
        # Check if active session exists
        active_session = db.query(ChatSession).filter(
            ChatSession.user_id == user.id,
            ChatSession.domain_config_id == domain_config_id,
            ChatSession.status == SessionStatus.ACTIVE
        ).first()
        
        if active_session:
            return active_session
        
        # Verify domain exists and user owns it
        domain = DomainService.get_domain_by_id(db, domain_config_id, user)
        
        # Create new session
        new_session = ChatSession(
            user_id=user.id,
            domain_config_id=domain_config_id,
            status=SessionStatus.ACTIVE
        )
        
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        
        # Add welcome message
        welcome_msg = ChatMessage(
            session_id=new_session.id,
            role=MessageRole.ASSISTANT,
            message="I'm your **Domain Pack AI Assistant**. I specialize in generating and maintaining complex structures like entities, rules, and reasoning templates.\n\nI've loaded your project context and I'm ready to help you enhance this domain pack. What would you like to do?"
        )
        db.add(welcome_msg)
        db.commit()
        
        return new_session
    
    @staticmethod
    def get_session(db: Session, session_id: UUID, user: User) -> ChatSession:
        """
        Get a chat session by ID.
        
        Args:
            db: Database session
            session_id: Session UUID
            user: Current user
            
        Returns:
            Chat session
            
        Raises:
            HTTPException: If session not found or access denied
        """
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        if session.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return session
    
    @staticmethod
    def close_session(db: Session, session_id: UUID, user: User) -> None:
        """
        Close a chat session.
        
        Args:
            db: Database session
            session_id: Session UUID
            user: Current user
        """
        session = ChatService.get_session(db, session_id, user)
        session.status = SessionStatus.CLOSED
        db.commit()

    @staticmethod
    def delete_session(db: Session, session_id: UUID, user: User) -> None:
        """
        Permanently delete a chat session and its messages.
        
        Args:
            db: Database session
            session_id: Session UUID
            user: Current user
        """
        session = ChatService.get_session(db, session_id, user)
        db.delete(session)
        db.commit()
    
    @staticmethod
    def send_message(
        db: Session,
        session_id: UUID,
        message_data: ChatRequest,
        user: User
    ) -> ChatResponse:
        """
        Send a message and get response from LangGraph.
        
        Args:
            db: Database session
            session_id: Session UUID
            message_data: User message
            user: Current user
            
        Returns:
            Chat response with assistant message
        """
        # Get session
        session = ChatService.get_session(db, session_id, user)
        
        # Update last activity
        session.last_activity_at = datetime.utcnow()
        
        # Get domain config
        domain = DomainService.get_domain_by_id(db, session.domain_config_id, user)
        
        # Save user message
        user_message = ChatMessage(
            session_id=session_id,
            role=MessageRole.USER,
            message=message_data.message
        )
        db.add(user_message)
        db.commit()
        
        # Get recent messages for context
        recent_messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(
            ChatMessage.created_at.desc()
        ).limit(ChatService.CONTEXT_MESSAGE_COUNT).all()
        
        # Reverse to chronological order
        recent_messages.reverse()
        
        # Convert to dict format
        chat_history = [
            {"role": msg.role.value, "content": msg.message}
            for msg in recent_messages[:-1]  # Exclude the message we just added
        ]
        
        # Check if this is a confirmation response to a pending patch
        if session.session_metadata and session.session_metadata.get("pending_patch"):
            user_msg_lower = message_data.message.lower().strip()
            
            if user_msg_lower in ["yes", "confirm", "y", "apply", "ok"]:
                # Apply pending patch
                domain.config_json = session.session_metadata["pending_updated_config"]
                domain.update_counts()
                session.session_metadata = {}
                db.commit()
                
                # Save confirmation response
                assistant_message = ChatMessage(
                    session_id=session_id,
                    role=MessageRole.ASSISTANT,
                    message="✅ Changes applied successfully!"
                )
                db.add(assistant_message)
                db.commit()
                
                return ChatResponse(
                    message=f"✅ Changes for the '{domain.name}' domain have been applied successfully!",
                    updated_config=domain.config_json
                )
            
            elif user_msg_lower in ["no", "cancel", "n", "reject", "abort"]:
                # Rollback - clear pending patch
                session.session_metadata = {}
                db.commit()
                
                # Save cancellation response
                assistant_message = ChatMessage(
                    session_id=session_id,
                    role=MessageRole.ASSISTANT,
                    message="❌ Changes cancelled. What would you like to do instead?"
                )
                db.add(assistant_message)
                db.commit()
                
                return ChatResponse(
                    message="❌ Changes cancelled. What would you like to do instead?"
                )
        
        # Create initial state
        initial_state = create_initial_state(
            domain_config=domain.config_json,
            user_message=message_data.message,
            chat_history=chat_history
        )
        
        # Execute graph with monitoring and checkpointer config
        from langchain_community.callbacks import get_openai_callback
        from app.utils.llm_monitor import llm_monitor
        
        # Configure thread for checkpointer
        config = {"configurable": {"thread_id": str(session_id)}}
        
        try:
            with get_openai_callback() as cb:
                # Use thread-aware invocation
                final_state = domain_graph.invoke(initial_state, config=config)
                
                # Update monitoring stats
                llm_monitor.update_tokens(
                    input_tokens=cb.prompt_tokens,
                    output_tokens=cb.completion_tokens,
                    db=db
                )
                
                # Update session stats
                session.total_llm_calls += cb.successful_requests
                session.total_input_tokens += cb.prompt_tokens
                session.total_output_tokens += cb.completion_tokens
                db.commit()
                
                print(f"📊 Session {session_id} Stats Updated: Calls={session.total_llm_calls}, Tokens={session.total_input_tokens + session.total_output_tokens}")
        except Exception as e:
            print(f"Error during graph execution or monitoring: {e}")
            raise e
        
        # Save assistant response
        assistant_message = ChatMessage(
            session_id=session_id,
            role=MessageRole.ASSISTANT,
            message=final_state["assistant_response"]
        )
        db.add(assistant_message)
        
        # If changes need confirmation, store in session metadata
        if final_state.get("needs_confirmation"):
            session.session_metadata = {
                "pending_patch": final_state["proposed_patch"],
                "pending_updated_config": final_state["updated_config"]
            }
        
        db.commit()
        
        # Prepare response
        response = ChatResponse(
            message=final_state["assistant_response"],
            reasoning=final_state.get("reasoning"),
            needs_confirmation=final_state.get("needs_confirmation", False),
            proposed_changes=final_state.get("proposed_patch"),
            proposed_patch=final_state.get("proposed_patch"),
            diff_preview=final_state.get("diff_preview"),
            updated_config=final_state.get("updated_config") if not final_state.get("needs_confirmation") else None
        )
        
        return response
    
    @staticmethod
    def get_messages(
        db: Session,
        session_id: UUID,
        user: User,
        limit: int = 50
    ) -> List[ChatMessage]:
        """
        Get messages for a session.
        
        Args:
            db: Database session
            session_id: Session UUID
            user: Current user
            limit: Maximum number of messages
            
        Returns:
            List of chat messages
        """
        # Verify access
        ChatService.get_session(db, session_id, user)
        
        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(
            ChatMessage.created_at.asc()
        ).limit(limit).all()
        
        return messages
