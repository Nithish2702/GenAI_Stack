from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import settings
from app.database.database import engine
from app.database import models

# Create database tables (with error handling)
try:
    models.Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
except Exception as e:
    print(f"⚠️  Database connection failed: {e}")
    print("💡 Make sure PostgreSQL is running or use Docker: docker-compose up -d db")

app = FastAPI(
    title="Workflow Builder API",
    description="No-Code/Low-Code workflow builder backend",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://*.vercel.app",  # Allow all Vercel deployments
        # Add your custom domain here when you have one
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Workflow Builder API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}