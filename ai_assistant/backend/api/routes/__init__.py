from .ai_routes import router as ai_router
from .auth_routes import router as auth_router
from .code_routes import router as code_router
from .file_routes import router as file_router
from .git_routes import router as git_router
from .project_routes import router as project_router
from .search_routes import router as search_router
from .websocket_routes import router as websocket_router

__all__ = [
    "ai_router",
    "auth_router",
    "code_router",
    "file_router",
    "git_router",
    "project_router",
    "search_router",
    "websocket_router"
]