from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from backend.database import Base

class AdView(Base):
    __tablename__ = "ad_views"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    session_id = Column(String(255), index=True)
    action_count = Column(Integer, nullable=False)
    viewed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    skipped = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="ad_views")
