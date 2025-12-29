from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    feed_id = Column(Integer, ForeignKey("feeds.id"), nullable=False)
    
    title = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False, index=True)
    content = Column(Text, nullable=True)  # 全文
    description = Column(Text, nullable=True)  # RSS 简介/Description
    author = Column(String, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    content_hash = Column(String, index=True) # 用于去重
    is_vectorized = Column(Boolean, default=False) # 是否已向量化
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    feed = relationship("Feed", backref="articles")
