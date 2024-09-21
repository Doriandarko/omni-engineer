from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from ..models.file_models import FileContent
from ..services.file_service import FileService
from ..middleware.auth import get_current_user

router = APIRouter()
file_service = FileService()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    try:
        file_info = await file_service.save_file(file, current_user["id"])
        return {"message": "File uploaded successfully", "file_info": file_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_files(current_user: dict = Depends(get_current_user)):
    try:
        files = file_service.list_files(current_user["id"])
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{file_id}")
async def get_file(file_id: str, current_user: dict = Depends(get_current_user)):
    try:
        file_content = file_service.get_file_content(file_id, current_user["id"])
        return FileContent(content=file_content)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{file_id}")
async def delete_file(file_id: str, current_user: dict = Depends(get_current_user)):
    try:
        file_service.delete_file(file_id, current_user["id"])
        return {"message": "File deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))