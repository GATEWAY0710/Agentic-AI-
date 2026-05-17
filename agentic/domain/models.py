from datetime import datetime
from sqlalchemy import Column, Integer, Text, String, DateTime, ForeignKey
from sqlalchemy.orm import  relationship, declarative_base
Base = declarative_base()

class SessionEntity(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), default="New Conversation")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    messages = relationship("MessageEntity", back_populates="session", cascade="all, delete-orphan")

class MessageEntity(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), index=True) # Added index
    role = Column(String(50)) 
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("SessionEntity", back_populates="messages")