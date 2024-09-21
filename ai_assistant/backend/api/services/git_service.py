# backend/api/services/git_service.py

from ...core.git_integration import GitIntegration

class GitService:
    def __init__(self):
        self.git_integration = GitIntegration()

    def commit(self, message: str | None, user_id: str):
        return self.git_integration.commit(message, user_id)

    def create_branch(self, name: str, user_id: str):
        return self.git_integration.create_branch(name, user_id)

    def get_current_branch(self, user_id: str):
        return self.git_integration.get_current_branch(user_id)

    def list_branches(self, user_id: str):
        return self.git_integration.list_branches(user_id)

    def perform_code_review(self, user_id: str):
        return self.git_integration.perform_code_review(user_id)