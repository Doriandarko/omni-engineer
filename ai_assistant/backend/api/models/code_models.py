# backend/api/models/code_models.py

from pydantic import BaseModel

class CodeSnippet(BaseModel):
    code: str
    language: str | None = None

class RefactorSuggestion(BaseModel):
    line: int
    message: str
    suggestion: str

class DebugRequest(BaseModel):
    code: str
    error: str

class CommitRequest(BaseModel):
    message: str | None = None

class BranchRequest(BaseModel):
    name: str