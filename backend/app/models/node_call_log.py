"""Per-node LLM call log model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class NodeCallLog(Base):
    """Records a single LLM call made within a LangGraph node for a chat session turn."""

    __tablename__ = "node_call_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    turn = Column(Integer, nullable=False, default=0)        # Which user-message turn
    node_name = Column(String, nullable=False)                # e.g. "classify_intent"
    input_tokens = Column(Integer, nullable=False, default=0)
    output_tokens = Column(Integer, nullable=False, default=0)
    response_time_ms = Column(Float, nullable=False, default=0.0)
    intent = Column(String, nullable=True)                   # Only set for classify_intent node
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_node_call_logs_session_turn", "session_id", "turn"),
    )

    def __repr__(self):
        return (
            f"<NodeCallLog(session={self.session_id}, turn={self.turn}, "
            f"node={self.node_name}, in={self.input_tokens}, out={self.output_tokens})>"
        )
