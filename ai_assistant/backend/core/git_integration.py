# backend/core/git_integration.py

from git import Repo, GitCommandError
from .ai_integration import AIIntegration

class GitIntegration:
    def __init__(self, repo_path: str = '.'):
        self.repo = Repo(repo_path)
        self.ai_integration = AIIntegration()

    def commit(self, message: str = None, user_id: str = None):
        try:
            self.repo.git.add(A=True)
            if not message:
                message = self.generate_commit_message()
            self.repo.index.commit(message)
            return f"Committed changes with message: {message}"
        except GitCommandError as e:
            return f"Git commit failed: {str(e)}"

    def create_branch(self, branch_name: str, user_id: str = None):
        try:
            self.repo.git.checkout('-b', branch_name)
            return f"Created and switched to new branch: {branch_name}"
        except GitCommandError as e:
            return f"Failed to create branch: {str(e)}"

    def get_current_branch(self, user_id: str = None):
        return self.repo.active_branch.name

    def list_branches(self, user_id: str = None):
        return [str(branch) for branch in self.repo.branches]

    async def perform_code_review(self, user_id: str = None):
        diffs = self.repo.git.diff(cached=True)
        prompt = f"Perform a code review on the following Git diff. Provide constructive feedback and suggestions for improvement:\n\n{diffs}\n\nCode review:"
        return await self.ai_integration.generate_response(prompt)

    async def generate_commit_message(self):
        diffs = self.repo.git.diff(cached=True)
        prompt = f"Based on the following Git diff, generate a concise and informative commit message:\n\n{diffs}\n\nCommit message:"
        return await self.ai_integration.generate_response(prompt)