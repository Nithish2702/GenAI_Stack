from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.services.document_service import DocumentService
from app.schemas.document import DocumentResponse, DocumentProcessResponse

router = APIRouter()
document_service = DocumentService()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    workflow_id: int = None,
    db: Session = Depends(get_db)
):
    """Upload a document and optionally link it to a workflow"""
    document = await document_service.upload_document(file, db, workflow_id=workflow_id)
    return document

@router.post("/{document_id}/process", response_model=DocumentProcessResponse)
async def process_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Process document: extract text and create embeddings"""
    result = await document_service.process_document(document_id, db)
    return DocumentProcessResponse(
        document_id=result["document_id"],
        chunks_created=result["chunks_created"],
        embeddings_created=result["embeddings_created"],
        processing_time=0.0  # You can add timing if needed
    )

@router.get("/", response_model=List[DocumentResponse])
async def get_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all documents"""
    documents = document_service.get_documents(db, skip=skip, limit=limit)
    return documents

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get document by ID"""
    document = document_service.get_document(document_id, db)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Delete document"""
    success = document_service.delete_document(document_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document deleted successfully"}