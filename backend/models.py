"""SQLAlchemy models for VocalMetric."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime

from .database import Base


class VoiceCheck(Base):
    """Database table capturing each voice analysis."""

    __tablename__ = "voice_checks"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    state = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    duration_seconds = Column(Float, nullable=False)
    file_path = Column(String, nullable=False)
