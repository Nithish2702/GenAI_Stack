from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.services.workflow_service import WorkflowService
from app.schemas.workflow import (
    WorkflowCreate, 
    WorkflowUpdate, 
    WorkflowResponse, 
    WorkflowExecuteRequest,
    WorkflowExecuteResponse
)

router = APIRouter()
workflow_service = WorkflowService()

@router.post("/", response_model=WorkflowResponse)
async def create_workflow(
    workflow: WorkflowCreate,
    db: Session = Depends(get_db)
):
    """Create a new workflow"""
    created_workflow = workflow_service.create_workflow(workflow, db)
    return created_workflow

@router.get("/", response_model=List[WorkflowResponse])
async def get_workflows(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all workflows"""
    workflows = workflow_service.get_workflows(db, skip=skip, limit=limit)
    return workflows

@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: int,
    db: Session = Depends(get_db)
):
    """Get workflow by ID"""
    workflow = workflow_service.get_workflow(workflow_id, db)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow

@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: int,
    workflow_update: WorkflowUpdate,
    db: Session = Depends(get_db)
):
    """Update workflow"""
    workflow = workflow_service.update_workflow(workflow_id, workflow_update, db)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow

@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: int,
    db: Session = Depends(get_db)
):
    """Delete workflow"""
    success = workflow_service.delete_workflow(workflow_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"message": "Workflow deleted successfully"}

@router.post("/{workflow_id}/validate")
async def validate_workflow(
    workflow_id: int,
    db: Session = Depends(get_db)
):
    """Validate workflow structure"""
    workflow = workflow_service.get_workflow(workflow_id, db)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    validation = workflow_service.validate_workflow(workflow.components, workflow.connections)
    return validation

@router.post("/execute", response_model=WorkflowExecuteResponse)
async def execute_workflow(
    request: WorkflowExecuteRequest,
    db: Session = Depends(get_db)
):
    """Execute workflow with query"""
    try:
        result = await workflow_service.execute_workflow(
            workflow_id=request.workflow_id,
            query=request.query,
            session_id=request.session_id,
            db=db
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution error: {str(e)}")