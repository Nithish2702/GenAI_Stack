from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class ChatMessageCreate(BaseModel):
    content: str
    message_type: str  # 'user' or 'assistant'
    message_metadata: Optional[Dict[str, Any]] = None

class ChatMessageResponse(BaseModel):
    id: int
    content: str
    message_type: str
    message_metadata: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True

class ChatSessionCreate(BaseModel):
    workflow_id: int
    session_name: Optional[str] = None

class ChatSessionResponse(BaseModel):
    id: int
    workflow_id: int
    session_name: Optional[str]
    created_at: datetime
    messages: List[ChatMessageResponse] = []

    class Config:
        from_attributes = True