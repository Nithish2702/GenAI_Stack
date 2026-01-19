"""
Supabase Storage Service

Handles file uploads to Supabase Storage for persistent file storage using REST API.
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

import httpx
from app.core.config import settings
import uuid
from typing import Optional

class StorageService:
    def __init__(self):
        """Initialize Supabase client using REST API"""
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY are required. Please check your .env file.")
        
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_KEY
        self.bucket_name = settings.SUPABASE_BUCKET
        
        # HTTP headers for Supabase API
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
        }
        
        print(f"✅ Supabase Storage initialized with bucket: {self.bucket_name}")
    
    async def upload_file(self, file_content: bytes, original_filename: str) -> tuple[str, str]:
        """
        Upload file to Supabase Storage using REST API
        
        Args:
            file_content: File bytes
            original_filename: Original filename with extension
        
        Returns:
            tuple: (unique_filename, file_path)
        """
        # Generate unique filename
        file_extension = original_filename.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Upload to Supabase using REST API
        try:
            url = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{unique_filename}"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers={
                        **self.headers,
                        "Content-Type": self._get_content_type(file_extension)
                    },
                    content=file_content,
                    timeout=30.0
                )
                
                if response.status_code not in [200, 201]:
                    raise Exception(f"Upload failed: {response.status_code} - {response.text}")
            
            # Get file path
            file_path = f"{self.bucket_name}/{unique_filename}"
            
            print(f"✅ Uploaded file to Supabase: {unique_filename}")
            return unique_filename, file_path
            
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            raise Exception(f"Failed to upload file to Supabase: {str(e)}")
    
    async def download_file(self, filename: str) -> bytes:
        """
        Download file from Supabase Storage using REST API
        
        Args:
            filename: Filename in storage
        
        Returns:
            bytes: File content
        """
        try:
            url = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{filename}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    raise Exception(f"Download failed: {response.status_code} - {response.text}")
                
                print(f"✅ Downloaded file from Supabase: {filename}")
                return response.content
                
        except Exception as e:
            print(f"❌ Download failed: {e}")
            raise Exception(f"Failed to download file from Supabase: {str(e)}")
    
    async def delete_file(self, filename: str):
        """
        Delete file from Supabase Storage using REST API
        
        Args:
            filename: Filename in storage
        """
        try:
            url = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{filename}"
            
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    url,
                    headers=self.headers,
                    timeout=30.0
                )
                
                if response.status_code not in [200, 204]:
                    print(f"⚠️  Delete warning: {response.status_code} - {response.text}")
                else:
                    print(f"✅ Deleted file from Supabase: {filename}")
                    
        except Exception as e:
            print(f"⚠️  Delete failed: {e}")
    
    def get_public_url(self, filename: str) -> str:
        """
        Get public URL for a file
        
        Args:
            filename: Filename in storage
        
        Returns:
            str: Public URL
        """
        return f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{filename}"
    
    def _get_content_type(self, extension: str) -> str:
        """Get content type from file extension"""
        content_types = {
            'pdf': 'application/pdf',
            'txt': 'text/plain',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        return content_types.get(extension.lower(), 'application/octet-stream')
