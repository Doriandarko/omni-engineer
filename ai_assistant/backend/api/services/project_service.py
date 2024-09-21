# backend/api/services/project_service.py

from ...core.code_analyzer import CodeAnalyzer
from ...core.vector_db import VectorDB

class ProjectService:
    def __init__(self):
        self.code_analyzer = CodeAnalyzer()
        self.vector_db = VectorDB()

    def analyze_project(self, project_path: str, user_id: str):
        return self.code_analyzer.analyze_project(project_path)

    def get_project_summary(self, user_id: str):
        # This would typically involve querying the vector database or other storage
        # for project-related information
        return "Project summary not implemented"

    def add_project_to_context(self, project_path: str, user_id: str):
        project_files = self.code_analyzer.get_project_files(project_path)
        for file_path, content in project_files.items():
            self.vector_db.add_document(file_path, content, {"user_id": user_id})
        return f"Added {len(project_files)} files to the context"