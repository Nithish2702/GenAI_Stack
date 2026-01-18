from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DocumentUpload(BaseModel):
    filename: str
    content_type: str

class DocumentResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_size: int
    content_type: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class DocumentProcessResponse(BaseModel):
    document_id: int
    chunks_created: int
    embeddings_created: int
    processing_time: float