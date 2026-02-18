"""Global LLM usage statistics model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class LLMUsage(Base):
    """Global LLM usage tracking."""
    
    __tablename__ = "llm_usage_stats"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    total_calls = Column(Integer, default=0, nullable=False)
    total_input_tokens = Column(Integer, default=0, nullable=False)
    total_output_tokens = Column(Integer, default=0, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<LLMUsage(calls={self.total_calls}, input={self.total_input_tokens}, output={self.total_output_tokens})>"
