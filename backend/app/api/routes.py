from fastapi import APIRouter
from app.api.endpoints import documents, workflows, chat

router = APIRouter()

router.include_router(documents.router, prefix="/documents", tags=["documents"])
router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
router.include_router(chat.router, prefix="/chat", tags=["chat"])