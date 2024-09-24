from fastapi import APIRouter, Depends, HTTPException
from ..models.code_models import CodeSnippet, RefactorSuggestion, DebugRequest
from ..services.code_service import CodeService
from ..middleware.auth import get_current_user

router = APIRouter()
code_service = CodeService()

@router.post("/refactor", response_model=list[RefactorSuggestion])
async def refactor_code(code_snippet: CodeSnippet, current_user: dict = Depends(get_current_user)):
    try:
        suggestions = code_service.get_refactoring_suggestions(code_snippet.code)
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/debug")
async def debug_code(debug_request: DebugRequest, current_user: dict = Depends(get_current_user)):
    try:
        debug_assistance = code_service.get_debug_assistance(debug_request.code, debug_request.error)
        return {"assistance": debug_assistance}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/complete")
async def complete_code(code_snippet: CodeSnippet, current_user: dict = Depends(get_current_user)):
    try:
        completion = code_service.get_code_completion(code_snippet.code)
        return {"completion": completion}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))