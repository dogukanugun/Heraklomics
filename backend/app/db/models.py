from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from app.core.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    uploads = relationship("UploadRecord", back_populates="user")

class UploadRecord(Base):
    __tablename__ = "upload_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    analysis_type = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    saved_path = Column(String, nullable=False)
    status = Column(String, default="uploaded")  # uploaded / queued / processing / done / failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="uploads")