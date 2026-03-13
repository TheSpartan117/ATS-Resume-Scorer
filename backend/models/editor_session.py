from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from backend.database import Base
import uuid


class EditorSession(Base):
    __tablename__ = "editor_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    resume_id = Column(String, nullable=True)
    role = Column(String, nullable=True)
    level = Column(String, nullable=True)
    score_data = Column(JSON, nullable=True)
    suggestions_data = Column(JSON, nullable=True)
    sections_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
