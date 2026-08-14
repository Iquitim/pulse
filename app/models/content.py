from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.base import Base

class MediaAsset(Base):
    __tablename__ = "media_assets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    original_name = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    storage_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="media_assets")

class PostHistory(Base):
    __tablename__ = "posts_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    social_account_id = Column(Integer, ForeignKey("social_accounts.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String, nullable=False)  # "success", "failed", "draft"
    theme = Column(String, nullable=False)
    tone = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    uri = Column(String, nullable=True)
    cid = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    media_id = Column(Integer, ForeignKey("media_assets.id"), nullable=True)
    
    likes = Column(Integer, default=0)
    reposts = Column(Integer, default=0)
    replies = Column(Integer, default=0)
    quality_score = Column(Integer, nullable=True)
    
    user = relationship("User", back_populates="posts_history")
    social_account = relationship("SocialAccount", back_populates="posts_history")
    media = relationship("MediaAsset")

class EditorialItem(Base):
    __tablename__ = "editorial_calendar"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_history_id = Column(Integer, ForeignKey("posts_history.id"), nullable=True)
    media_id = Column(Integer, ForeignKey("media_assets.id"), nullable=True)
    theme = Column(String, nullable=False)
    scheduled_date = Column(DateTime, nullable=False)
    status = Column(String, default="planejado")  # "planejado", "publicado", "falhou"
    objective = Column(Text, nullable=True)
    cta = Column(String, nullable=True)
    channel = Column(String, default="bluesky")  # "bluesky", "twitter", "threads"
    is_manual = Column(Boolean, default=False)
    manual_content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="editorial_items")
    post_history = relationship("PostHistory", backref="editorial_item", uselist=False)
    media = relationship("MediaAsset")

class Idea(Base):
    __tablename__ = "ideas"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")  # "pending", "converted"
    channel = Column(String, default="bluesky")
    
    user = relationship("User", back_populates="ideas")
