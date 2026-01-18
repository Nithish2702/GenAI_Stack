from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String, nullable=False)
    extracted_text = Column(Text)
    is_processed = Column(Boolean, default=False)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=True)  # Link document to workflow
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    workflow = relationship("Workflow", back_populates="documents")

class Workflow(Base):
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    components = Column(JSON, nullable=False)  # Store workflow structure
    connections = Column(JSON, nullable=False)  # Store component connections
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    chat_sessions = relationship("ChatSession", back_populates="workflow", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="workflow", cascade="all, delete-orphan")

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    session_name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    workflow = relationship("Workflow", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    message_type = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    message_metadata = Column(JSON)  # Store additional info like execution time, tokens used, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    session = relationship("ChatSession", back_populates="messages")