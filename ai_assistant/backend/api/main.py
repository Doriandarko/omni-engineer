from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import ai_routes, auth_routes, code_routes, file_routes, git_routes, project_routes, search_routes, websocket_routes
from .middleware.auth import auth_middleware
from .middleware.rate_limit import rate_limit_middleware

app = FastAPI(title="AI Assistant API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middlewares
app.middleware("http")(auth_middleware)
app.middleware("http")(rate_limit_middleware)

# Include routers
app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
app.include_router(ai_routes.router, prefix="/ai", tags=["AI"])
app.include_router(code_routes.router, prefix="/code", tags=["Code"])
app.include_router(file_routes.router, prefix="/files", tags=["Files"])
app.include_router(git_routes.router, prefix="/git", tags=["Git"])
app.include_router(project_routes.router, prefix="/project", tags=["Project"])
app.include_router(search_routes.router, prefix="/search", tags=["Search"])
app.include_router(websocket_routes.router, tags=["WebSocket"])

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Assistant API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)