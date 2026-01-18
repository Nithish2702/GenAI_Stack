from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.database.models import ChatSession, ChatMessage
from app.schemas.chat import ChatSessionCreate, ChatSessionResponse, ChatMessageResponse

router = APIRouter()

@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    session_data: ChatSessionCreate,
    db: Session = Depends(get_db)
):
    """Create a new chat session"""
    session = ChatSession(
        workflow_id=session_data.workflow_id,
        session_name=session_data.session_name
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Get chat session with messages"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session

@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_chat_sessions(
    workflow_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get chat sessions, optionally filtered by workflow"""
    query = db.query(ChatSession)
    if workflow_id:
        query = query.filter(ChatSession.workflow_id == workflow_id)
    
    sessions = query.offset(skip).limit(limit).all()
    return sessions

@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_chat_messages(
    session_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get messages for a chat session"""
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).offset(skip).limit(limit).all()
    
    return messages

@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Delete chat session and all its messages"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    # Delete all messages first
    db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
    
    # Delete session
    db.delete(session)
    db.commit()
    
    return {"message": "Chat session deleted successfully"}