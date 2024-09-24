from fastapi import APIRouter, Depends, HTTPException
from ..models.code_models import CommitRequest, BranchRequest
from ..services.git_service import GitService
from ..middleware.auth import get_current_user

router = APIRouter()
git_service = GitService()

@router.post("/commit")
async def commit_changes(commit_request: CommitRequest, current_user: dict = Depends(get_current_user)):
    try:
        result = git_service.commit(commit_request.message, current_user["id"])
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-branch")
async def create_branch(branch_request: BranchRequest, current_user: dict = Depends(get_current_user)):
    try:
        result = git_service.create_branch(branch_request.name, current_user["id"])
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/current-branch")
async def get_current_branch(current_user: dict = Depends(get_current_user)):
    try:
        branch = git_service.get_current_branch(current_user["id"])
        return {"branch": branch}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/branches")
async def list_branches(current_user: dict = Depends(get_current_user)):
    try:
        branches = git_service.list_branches(current_user["id"])
        return {"branches": branches}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/review")
async def review_changes(current_user: dict = Depends(get_current_user)):
    try:
        review = git_service.perform_code_review(current_user["id"])
        return {"review": review}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))