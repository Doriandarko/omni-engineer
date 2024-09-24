# backend/api/services/file_service.py

import os
import uuid
from fastapi import UploadFile
from ...core.file_handler import FileHandler

class FileService:
    def __init__(self):
        self.file_handler = FileHandler()

    async def save_file(self, file: UploadFile, user_id: str):
        file_id = str(uuid.uuid4())
        file_path = os.path.join("user_files", user_id, file_id)
        await self.file_handler.save_file(file_path, file)
        return {
            "id": file_id,
            "name": file.filename,
            "size": file.size,
            "content_type": file.content_type
        }

    def list_files(self, user_id: str):
        user_directory = os.path.join("user_files", user_id)
        return self.file_handler.list_files(user_directory)

    def get_file_content(self, file_id: str, user_id: str):
        file_path = os.path.join("user_files", user_id, file_id)
        return self.file_handler.read_file(file_path)

    def delete_file(self, file_id: str, user_id: str):
        file_path = os.path.join("user_files", user_id, file_id)
        self.file_handler.delete_file(file_path)