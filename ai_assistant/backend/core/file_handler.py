# backend/core/file_handler.py

import os
from fastapi import UploadFile

class FileHandler:
    def __init__(self, base_path: str = "."):
        self.base_path = base_path

    async def save_file(self, file_path: str, file: UploadFile):
        full_path = os.path.join(self.base_path, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

    def read_file(self, file_path: str) -> str:
        full_path = os.path.join(self.base_path, file_path)
        try:
            with open(full_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            return f"Error: File not found: {file_path}"
        except IOError as e:
            return f"Error reading {file_path}: {e}"

    def delete_file(self, file_path: str) -> bool:
        full_path = os.path.join(self.base_path, file_path)
        try:
            os.remove(full_path)
            return True
        except FileNotFoundError:
            return False
        except IOError:
            return False

    def list_files(self, directory: str = "") -> List[str]:
        full_path = os.path.join(self.base_path, directory)
        try:
            return os.listdir(full_path)
        except FileNotFoundError:
            return []