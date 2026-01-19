"""
Supabase Storage Service

Handles file uploads to Supabase Storage for persistent file storage.
Files are stored in the cloud and accessible via public URLs.

Features:
- Upload files to Supabase Storage
- Download files from Supabase Storage
- Delete files from Supabase Storage
- Generate public URLs for files
- Persistent storage (files never deleted)

Usage:
    storage = StorageService()
    file_url = await storage.upload_file(file_content, filename)
    content = await storage.download_file(filename)
"""

from supabase import create_client, Client
from app.core.config import settings
import uuid
from typing import Optional

class StorageService:
    def __init__(self):
        """Initialize Supabase client"""
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY are required. Please check your .env file.")
        
        try:
            # Create Supabase client
            self.supabase: Client = create_client(
                supabase_url=settings.SUPABASE_URL,
                supabase_key=settings.SUPABASE_KEY
            )
            self.bucket_name = settings.SUPABASE_BUCKET
            
            # Ensure bucket exists
            self._ensure_bucket_exists()
            
            print(f"✅ Supabase Storage initialized with bucket: {self.bucket_name}")
        except Exception as e:
            print(f"❌ Failed to initialize Supabase: {e}")
            raise ValueError(f"Supabase initialization failed. Please check your credentials: {str(e)}")
    
    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        try:
            # Try to get bucket
            buckets = self.supabase.storage.list_buckets()
            bucket_names = [b.name for b in buckets]
            
            if self.bucket_name in bucket_names:
                print(f"✅ Using existing bucket: {self.bucket_name}")
            else:
                # Create bucket if it doesn't exist
                self.supabase.storage.create_bucket(
                    self.bucket_name,
                    options={"public": False}  # Private bucket
                )
                print(f"✅ Created new bucket: {self.bucket_name}")
        except Exception as e:
            print(f"⚠️  Bucket check/creation note: {e}")
            # Don't fail if bucket already exists or we can't check
    
    async def upload_file(self, file_content: bytes, original_filename: str) -> tuple[str, str]:
        """
        Upload file to Supabase Storage
        
        Args:
            file_content: File bytes
            original_filename: Original filename with extension
        
        Returns:
            tuple: (unique_filename, file_path)
        """
        # Generate unique filename
        file_extension = original_filename.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Upload to Supabase
        try:
            self.supabase.storage.from_(self.bucket_name).upload(
                path=unique_filename,
                file=file_content,
                file_options={"content-type": self._get_content_type(file_extension)}
            )
            
            # Get file path
            file_path = f"{self.bucket_name}/{unique_filename}"
            
            print(f"✅ Uploaded file to Supabase: {unique_filename}")
            return unique_filename, file_path
            
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            raise Exception(f"Failed to upload file to Supabase: {str(e)}")
    
    async def download_file(self, filename: str) -> bytes:
        """
        Download file from Supabase Storage
        
        Args:
            filename: Filename in storage
        
        Returns:
            bytes: File content
        """
        try:
            response = self.supabase.storage.from_(self.bucket_name).download(filename)
            print(f"✅ Downloaded file from Supabase: {filename}")
            return response
        except Exception as e:
            print(f"❌ Download failed: {e}")
            raise Exception(f"Failed to download file from Supabase: {str(e)}")
    
    async def delete_file(self, filename: str):
        """
        Delete file from Supabase Storage
        
        Args:
            filename: Filename in storage
        """
        try:
            self.supabase.storage.from_(self.bucket_name).remove([filename])
            print(f"✅ Deleted file from Supabase: {filename}")
        except Exception as e:
            print(f"⚠️  Delete failed: {e}")
    
    def get_public_url(self, filename: str) -> str:
        """
        Get public URL for a file (requires public bucket)
        
        Args:
            filename: Filename in storage
        
        Returns:
            str: Public URL
        """
        try:
            response = self.supabase.storage.from_(self.bucket_name).get_public_url(filename)
            return response
        except Exception as e:
            print(f"⚠️  Failed to get public URL: {e}")
            return ""
    
    def _get_content_type(self, extension: str) -> str:
        """Get content type from file extension"""
        content_types = {
            'pdf': 'application/pdf',
            'txt': 'text/plain',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        return content_types.get(extension.lower(), 'application/octet-stream')
