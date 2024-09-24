from fastapi import APIRouter, Depends, HTTPException
from ..models.ai_models import AIRequest, AIResponse
from ..services.ai_service import AIService
from ..middleware.auth import get_current_user

router = APIRouter()
ai_service = AIService()

@router.post("/ask", response_model=AIResponse)
async def ask_ai(request: AIRequest, current_user: dict = Depends(get_current_user)):
    try:
        response = await ai_service.generate_response(request.prompt, current_user["id"])
        return AIResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def stream_ai_response(request: AIRequest, current_user: dict = Depends(get_current_user)):
    try:
        return ai_service.stream_response(request.prompt, current_user["id"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/switch-model")
async def switch_ai_model(model: str, current_user: dict = Depends(get_current_user)):
    try:
        new_model = ai_service.switch_model(model)
        return {"message": f"Switched to model: {new_model}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))