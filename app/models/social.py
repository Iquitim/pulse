from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.base import Base

class SocialAccount(Base):
    __tablename__ = "social_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform = Column(String, nullable=False)  # "bluesky", "twitter", "threads"
    account_handle = Column(String, nullable=False)  # e.g. @silvano.bsky.social
    encrypted_credentials = Column(Text, nullable=False)  # encrypted credentials
    is_connected = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="social_accounts")
    posts_history = relationship("PostHistory", back_populates="social_account")
