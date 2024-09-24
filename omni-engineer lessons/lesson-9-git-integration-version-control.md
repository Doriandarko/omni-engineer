# Lesson 9: Git Integration and Version Control

In this lesson, we'll integrate Git functionality into our AI-assisted CLI tool. We'll implement features for Git commit operations, branch management, and AI-assisted commit messages and code reviews. This will enhance our tool's capabilities in managing code repositories and version control.

## Project Structure

Let's update our project structure to include the new Git-related components:

```
ai_cli_tool/
│
├── main.py
├── cli.py
├── ai_integration.py
├── file_handler.py
├── utils.py
├── models/
│   ├── __init__.py
│   ├── base_model.py
│   ├── gpt3_model.py
│   ├── gpt4_model.py
│   └── codex_model.py
├── services/
│   ├── __init__.py
│   ├── code_completion.py
│   ├── suggestion_service.py
│   ├── vector_db_service.py
│   ├── qa_service.py
│   └── git_service.py
├── knowledge_base/
│   ├── __init__.py
│   ├── document.py
│   └── kb_manager.py
├── .env
├── requirements.txt
└── README.md
```

## 1. Setting up Git Integration

First, let's add the required Git library to our requirements:

```
# requirements.txt
gitpython==3.1.30
```

Now, let's create a GitService to handle Git operations:

```python
# services/git_service.py

import os
from git import Repo, GitCommandError
from models import ModelFactory

class GitService:
    def __init__(self, repo_path: str = '.'):
        self.repo_path = repo_path
        self.repo = Repo(repo_path)
        self.ai_model = ModelFactory.get_model("gpt4")

    def commit(self, message: str = None):
        try:
            self.repo.git.add(A=True)
            if not message:
                message = self.generate_commit_message()
            self.repo.index.commit(message)
            return f"Committed changes with message: {message}"
        except GitCommandError as e:
            return f"Git commit failed: {str(e)}"

    def create_branch(self, branch_name: str):
        try:
            self.repo.git.checkout('-b', branch_name)
            return f"Created and switched to new branch: {branch_name}"
        except GitCommandError as e:
            return f"Failed to create branch: {str(e)}"

    def switch_branch(self, branch_name: str):
        try:
            self.repo.git.checkout(branch_name)
            return f"Switched to branch: {branch_name}"
        except GitCommandError as e:
            return f"Failed to switch branch: {str(e)}"

    def generate_commit_message(self):
        diffs = self.repo.git.diff(cached=True)
        prompt = f"Based on the following Git diff, generate a concise and informative commit message:\n\n{diffs}\n\nCommit message:"
        return self.ai_model.generate_response(prompt)

    def get_current_branch(self):
        return self.repo.active_branch.name

    def list_branches(self):
        return [str(branch) for branch in self.repo.branches]

    def perform_code_review(self):
        diffs = self.repo.git.diff(cached=True)
        prompt = f"Perform a code review on the following Git diff. Provide constructive feedback and suggestions for improvement:\n\n{diffs}\n\nCode review:"
        return self.ai_model.generate_response(prompt)
```

## 2. Implementing CLI Commands for Git Operations

Let's add new commands to our CLI for Git operations:

```python
# cli.py

import click
from services.git_service import GitService

git_service = GitService()

@cli.group()
def git():
    """Git operations"""
    pass

@git.command()
@click.option('--message', '-m', help='Commit message')
def commit(message):
    """Commit changes to the repository"""
    result = git_service.commit(message)
    click.echo(result)

@git.command()
@click.argument('branch_name')
def create_branch(branch_name):
    """Create a new branch"""
    result = git_service.create_branch(branch_name)
    click.echo(result)

@git.command()
@click.argument('branch_name')
def switch_branch(branch_name):
    """Switch to a different branch"""
    result = git_service.switch_branch(branch_name)
    click.echo(result)

@git.command()
def current_branch():
    """Show the current branch"""
    branch = git_service.get_current_branch()
    click.echo(f"Current branch: {branch}")

@git.command()
def list_branches():
    """List all branches"""
    branches = git_service.list_branches()
    click.echo("Branches:")
    for branch in branches:
        click.echo(f"- {branch}")

@git.command()
def review():
    """Perform an AI-assisted code review"""
    review = git_service.perform_code_review()
    click.echo("AI Code Review:")
    click.echo(review)
```

## 3. Enhancing AI-Assisted Commit Messages

Let's improve our commit message generation by providing more context:

```python
# services/git_service.py

class GitService:
    # ... (previous methods)

    def generate_commit_message(self):
        diffs = self.repo.git.diff(cached=True)
        staged_files = self.repo.git.diff('--cached', '--name-only').split('\n')
        
        prompt = f"""Generate a concise and informative commit message based on the following information:

Staged files:
{', '.join(staged_files)}

Git diff:
{diffs}

Consider the following guidelines:
1. Start with a short (50 chars or less) summary of changes
2. Use the imperative mood in the subject line
3. Explain what and why vs. how
4. Include any relevant issue numbers

Commit message:"""

        return self.ai_model.generate_response(prompt)
```

## 4. Implementing AI-Assisted Code Reviews

Let's enhance our code review functionality:

```python
# services/git_service.py

class GitService:
    # ... (previous methods)

    def perform_code_review(self):
        diffs = self.repo.git.diff(cached=True)
        staged_files = self.repo.git.diff('--cached', '--name-only').split('\n')
        
        prompt = f"""Perform a thorough code review on the following Git diff. 

Staged files:
{', '.join(staged_files)}

Git diff:
{diffs}

Please provide feedback on the following aspects:
1. Code quality and best practices
2. Potential bugs or errors
3. Performance considerations
4. Security concerns
5. Readability and maintainability
6. Suggestions for improvement

Format your review as a markdown list with main points and sub-points.

Code review:"""

        return self.ai_model.generate_response(prompt)
```

## 5. Integrating Git Operations with Knowledge Base

Let's update our KnowledgeBaseManager to include Git-related information:

```python
# knowledge_base/kb_manager.py

from .document import Document
from services.vector_db_service import VectorDBService
from services.git_service import GitService

class KnowledgeBaseManager:
    def __init__(self):
        self.vector_db = VectorDBService()
        self.git_service = GitService()

    # ... (previous methods)

    def add_git_commit(self, commit_hash: str):
        commit = self.git_service.repo.commit(commit_hash)
        content = f"""Commit: {commit.hexsha}
Author: {commit.author}
Date: {commit.committed_datetime}
Message: {commit.message}

Diff:
{commit.diff(commit.parents[0] if commit.parents else None)}
"""
        document = Document(id=f"git_commit_{commit.hexsha}", content=content, metadata={"type": "git_commit"})
        self.add_document(document)

    def add_current_branch_info(self):
        branch_name = self.git_service.get_current_branch()
        content = f"""Current Git Branch: {branch_name}

Last 5 commits:
"""
        for commit in self.git_service.repo.iter_commits(max_count=5):
            content += f"- {commit.hexsha[:7]}: {commit.summary}\n"

        document = Document(id=f"git_branch_{branch_name}", content=content, metadata={"type": "git_branch"})
        self.add_document(document)
```

Now, let's add CLI commands to use these new features:

```python
# cli.py

@git.command()
@click.argument('commit_hash')
def add_commit_to_kb(commit_hash):
    """Add a Git commit to the knowledge base"""
    kb_manager.add_git_commit(commit_hash)
    click.echo(f"Added commit {commit_hash} to the knowledge base")

@git.command()
def add_branch_to_kb():
    """Add current branch info to the knowledge base"""
    kb_manager.add_current_branch_info()
    click.echo("Added current branch info to the knowledge base")
```

## 6. Implementing Git-Aware AI Responses

Let's update our AIIntegration class to consider Git context:

```python
# ai_integration.py

from utils import context_manager
from knowledge_base.kb_manager import KnowledgeBaseManager
from services.git_service import GitService

class AIIntegration:
    def __init__(self, model_name: str = "gpt4"):
        self.model = ModelFactory.get_model(model_name)
        self.kb_manager = KnowledgeBaseManager()
        self.git_service = GitService()

    def generate_response(self, prompt: str) -> str:
        coding_context = "You are an expert programmer assisting with coding tasks and Git operations. "
        relevant_context = self.kb_manager.get_relevant_context(prompt)
        git_context = self._get_git_context()
        
        full_prompt = f"""{coding_context}

Relevant context:
{relevant_context}

Git context:
{git_context}

Conversation context:
{context_manager.get_context()}

User: {prompt}
AI:"""

        response = self.model.generate_response(full_prompt)
        context_manager.add_to_context(f"User: {prompt}")
        context_manager.add_to_context(f"AI: {response}")
        return response

    def _get_git_context(self):
        current_branch = self.git_service.get_current_branch()
        staged_files = self.git_service.repo.git.diff('--cached', '--name-only').split('\n')
        
        return f"""Current Git branch: {current_branch}
Staged files: {', '.join(staged_files)}"""
```

## Conclusion

In this lesson, we've integrated Git functionality into our AI-assisted CLI tool. We've implemented features for:

1. Basic Git operations (commit, branch creation, branch switching)
2. AI-assisted commit message generation
3. AI-powered code reviews
4. Integration of Git information with our knowledge base
5. Git-aware AI responses

These enhancements significantly improve our tool's capabilities in managing code repositories and version control. The AI-assisted features provide valuable insights and automate common Git tasks, making the development process more efficient.

To further improve the system, consider the following:

1. Implement support for more advanced Git operations (merge, rebase, etc.)
2. Add conflict resolution assistance using AI
3. Integrate with popular Git hosting platforms (GitHub, GitLab, Bitbucket)
4. Implement AI-assisted code refactoring suggestions based on Git history
5. Add support for Git hooks to automate AI-assisted tasks

In the next lesson, we'll explore building a web API for our AI-assisted tool, allowing for remote access and integration with other services.
