from fastapi import APIRouter, Depends, HTTPException
from ..services.search_service import SearchService
from ..middleware.auth import get_current_user

router = APIRouter()
search_service = SearchService()

@router.get("/web")
async def web_search(query: str, current_user: dict = Depends(get_current_user)):
    try:
        results = await search_service.web_search(query)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/knowledge-base")
async def knowledge_base_search(query: str, current_user: dict = Depends(get_current_user)):
    try:
        results = search_service.knowledge_base_search(query, current_user["id"])
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))