# backend/api/models/file_models.py

from pydantic import BaseModel

class FileContent(BaseModel):
    content: str

class FileInfo(BaseModel):
    id: str
    name: str
    size: int
    last_modified: str