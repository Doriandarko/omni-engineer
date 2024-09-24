from fastapi import APIRouter, Depends, HTTPException
from ..services.project_service import ProjectService
from ..middleware.auth import get_current_user

router = APIRouter()
project_service = ProjectService()

@router.post("/analyze")
async def analyze_project(project_path: str, current_user: dict = Depends(get_current_user)):
    try:
        analysis = project_service.analyze_project(project_path, current_user["id"])
        return {"project_analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary")
async def get_project_summary(current_user: dict = Depends(get_current_user)):
    try:
        summary = project_service.get_project_summary(current_user["id"])
        return {"project_summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add-to-context")
async def add_project_to_context(project_path: str, current_user: dict = Depends(get_current_user)):
    try:
        result = project_service.add_project_to_context(project_path, current_user["id"])
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))