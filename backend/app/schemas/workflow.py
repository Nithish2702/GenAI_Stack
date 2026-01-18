from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class ComponentBase(BaseModel):
    id: str
    type: str
    position: Dict[str, float]
    data: Optional[Dict[str, Any]] = {}

class ConnectionBase(BaseModel):
    id: Optional[str] = None
    source: str
    target: str
    sourceHandle: Optional[str] = None
    targetHandle: Optional[str] = None

class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    components: List[ComponentBase]
    connections: List[ConnectionBase]

class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    components: Optional[List[ComponentBase]] = None
    connections: Optional[List[ConnectionBase]] = None
    is_active: Optional[bool] = None

class WorkflowResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    components: List[Dict[str, Any]]
    connections: List[Dict[str, Any]]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class WorkflowExecuteRequest(BaseModel):
    workflow_id: int
    query: str
    session_id: Optional[int] = None

class WorkflowExecuteResponse(BaseModel):
    response: str
    session_id: int
    execution_time: float
    metadata: Optional[Dict[str, Any]] = None