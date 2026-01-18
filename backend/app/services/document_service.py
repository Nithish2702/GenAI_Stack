"""
Document Service Module

This module handles document upload, processing, and text extraction.
It supports PDF files and integrates with Supabase Storage and vector service.

Key Features:
- File upload to Supabase Storage (persistent cloud storage)
- PDF text extraction using PyMuPDF
- Text chunking for embeddings
- Document metadata management
- Integration with vector database

Usage:
    doc_service = DocumentService()
    document = doc_service.upload_document(file, db)
    await doc_service.process_document(document.id, db)
"""

import os
import io
import fitz  # PyMuPDF
from typing import List, Optional
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.database.models import Document
from app.core.config import settings
from app.services.vector_service import VectorService
from app.services.storage_service import StorageService

class DocumentService:
    def __init__(self):
        self.vector_service = VectorService()
        self.storage_service = StorageService()
        print("✅ DocumentService initialized with Supabase Storage")

    async def upload_document(self, file: UploadFile, db: Session, workflow_id: int = None) -> Document:
        # Validate file type
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in settings.ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_extension} not allowed. Allowed types: {settings.ALLOWED_FILE_TYPES}"
            )

        # Read file content
        content = await file.read()
        if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
            )

        # Upload to Supabase Storage
        try:
            unique_filename, file_path = await self.storage_service.upload_file(
                content, 
                file.filename
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload file to storage: {str(e)}"
            )

        # Create database record with workflow_id
        document = Document(
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,  # Supabase path
            file_size=len(content),
            content_type=file.content_type,
            workflow_id=workflow_id  # Link to workflow
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)

        print(f"✅ Document uploaded: {file.filename} → {unique_filename} (workflow_id: {workflow_id})")
        return document

    async def extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF using PyMuPDF"""
        try:
            # Open PDF from bytes
            doc = fitz.open(stream=file_content, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error extracting text from PDF: {str(e)}")

    async def extract_text_from_txt(self, file_content: bytes) -> str:
        """Extract text from TXT file"""
        try:
            return file_content.decode('utf-8')
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading text file: {str(e)}")

    async def process_document(self, document_id: int, db: Session) -> dict:
        """Process document: extract text and create embeddings"""
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Download file from Supabase
        try:
            file_content = await self.storage_service.download_file(document.filename)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to download file from storage: {str(e)}"
            )

        # Extract text based on file type
        file_extension = os.path.splitext(document.filename)[1].lower()
        
        if file_extension == ".pdf":
            extracted_text = await self.extract_text_from_pdf(file_content)
        elif file_extension == ".txt":
            extracted_text = await self.extract_text_from_txt(file_content)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_extension}")

        # Update document with extracted text
        document.extracted_text = extracted_text
        document.is_processed = True
        db.commit()

        # Create embeddings and store in vector database
        chunks = self._chunk_text(extracted_text)
        embeddings_created = await self.vector_service.add_document_chunks(
            document_id=document_id,
            chunks=chunks,
            metadata={"filename": document.original_filename}
        )

        print(f"✅ Document processed: {document.original_filename} ({len(chunks)} chunks)")
        
        return {
            "document_id": document_id,
            "chunks_created": len(chunks),
            "embeddings_created": embeddings_created,
            "text_length": len(extracted_text)
        }

    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
            
        return chunks

    def get_document(self, document_id: int, db: Session) -> Optional[Document]:
        return db.query(Document).filter(Document.id == document_id).first()

    def get_documents(self, db: Session, skip: int = 0, limit: int = 100) -> List[Document]:
        return db.query(Document).offset(skip).limit(limit).all()

    async def delete_document(self, document_id: int, db: Session) -> bool:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return False

        # Delete file from Supabase Storage
        try:
            await self.storage_service.delete_file(document.filename)
        except Exception as e:
            print(f"⚠️  Failed to delete file from storage: {e}")

        # Delete from vector store
        self.vector_service.delete_document(document_id)

        # Delete from database
        db.delete(document)
        db.commit()
        
        print(f"✅ Document deleted: {document.original_filename}")
        return True