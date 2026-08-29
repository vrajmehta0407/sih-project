import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="inspector")  # 'admin', 'inspector', 'supervisor'
    badge_number = Column(String(100), unique=True, nullable=True)
    phone_number = Column(String(20), nullable=True)
    jurisdiction_district = Column(String(100), nullable=True, index=True)
    jurisdiction_state = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    inspections = relationship("Inspection", back_populates="inspector", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")
