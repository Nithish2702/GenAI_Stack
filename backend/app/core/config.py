import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/workflow_db")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    
    # Supabase Storage for file uploads
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_BUCKET: str = os.getenv("SUPABASE_BUCKET", "documents")
    
    # SERPAPI_KEY: str = os.getenv("SERPAPI_KEY", "")  # Optional: Uncomment to enable web search
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    
    # File upload settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: list = [".pdf", ".txt", ".docx"]

settings = Settings()