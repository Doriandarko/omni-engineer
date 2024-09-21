# Lesson 10: Building a Web API for the AI-Assisted Tool

In this lesson, we'll transform our CLI-based AI assistant into a web service by creating a RESTful API. We'll use FastAPI, a modern, fast (high-performance) Python web framework for building APIs. We'll also implement authentication, rate limiting, and ensure our API can handle the core functionalities of our AI assistant.

## Project Structure

Before we begin, let's look at the updated project structure:

```
ai_cli_tool/
│
├── api/
│   ├── __init__.py
│   ├── main.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── ai_routes.py
│   │   ├── file_routes.py
│   │   └── search_routes.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── request_models.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py
│   │   ├── file_service.py
│   │   └── search_service.py
│   └── middleware/
│       ├── __init__.py
│       ├── auth.py
│       └── rate_limit.py
├── cli/
│   ├── __init__.py
│   └── main.py
├── core/
│   ├── __init__.py
│   ├── ai_integration.py
│   ├── file_handler.py
│   └── search_handler.py
├── utils/
│   ├── __init__.py
│   └── helpers.py
├── .env
├── requirements.txt
└── README.md
```

## Step 1: Setting Up FastAPI

First, let's install the necessary packages:

```bash
pip install fastapi uvicorn python-jose[cryptography] passlib[bcrypt]
```

Now, let's create our main FastAPI application in `api/main.py`:

```python
# api/main.py

from fastapi import FastAPI
from api.routes import ai_routes, file_routes, search_routes
from api.middleware.auth import auth_middleware
from api.middleware.rate_limit import rate_limit_middleware

app = FastAPI(title="AI Assistant API")

# Add middlewares
app.middleware("http")(auth_middleware)
app.middleware("http")(rate_limit_middleware)

# Include routers
app.include_router(ai_routes.router, prefix="/ai", tags=["AI"])
app.include_router(file_routes.router, prefix="/files", tags=["Files"])
app.include_router(search_routes.router, prefix="/search", tags=["Search"])

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Assistant API"}
```

## Step 2: Implementing Authentication

Let's implement a simple JWT-based authentication system in `api/middleware/auth.py`:

```python
# api/middleware/auth.py

from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def auth_middleware(request: Request, call_next):
    if request.url.path in ["/", "/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)

    try:
        token = await security(request)
        token_data = decode_token(token.credentials)
        request.state.user = token_data
    except HTTPException:
        return HTTPException(status_code=401, detail="Invalid or missing token")
    
    return await call_next(request)
```

## Step 3: Implementing Rate Limiting

Let's add a simple in-memory rate limiter in `api/middleware/rate_limit.py`:

```python
# api/middleware/rate_limit.py

from fastapi import Request, HTTPException
from collections import defaultdict
import time

RATE_LIMIT = 100  # requests per minute
RATE_LIMIT_PERIOD = 60  # seconds

request_counts = defaultdict(list)

async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()
    
    # Remove old timestamps
    request_counts[client_ip] = [t for t in request_counts[client_ip] if current_time - t < RATE_LIMIT_PERIOD]
    
    if len(request_counts[client_ip]) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    request_counts[client_ip].append(current_time)
    
    return await call_next(request)
```

## Step 4: Implementing API Routes

Now, let's implement the core functionalities as API routes. We'll focus on the AI routes for this example:

```python
# api/routes/ai_routes.py

from fastapi import APIRouter, Depends, HTTPException
from api.models.request_models import AIRequest
from api.services.ai_service import get_ai_response
from api.middleware.auth import security, decode_token

router = APIRouter()

@router.post("/ask")
async def ask_ai(request: AIRequest, token: str = Depends(security)):
    user = decode_token(token.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    response = await get_ai_response(request.prompt, user["sub"])
    return {"response": response}
```

## Step 5: Implementing AI Service

Let's create a service to handle AI interactions:

```python
# api/services/ai_service.py

from core.ai_integration import get_ai_completion

async def get_ai_response(prompt: str, user_id: str):
    # Here you might want to retrieve user context, history, etc.
    context = f"User {user_id} asked: {prompt}"
    response = await get_ai_completion(context)
    # Here you might want to save the interaction to the user's history
    return response
```

## Step 6: Updating Core AI Integration

Let's update our core AI integration to work asynchronously:

```python
# core/ai_integration.py

import openai
from dotenv import load_dotenv
import os

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

async def get_ai_completion(prompt: str):
    try:
        response = await openai.Completion.acreate(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"An error occurred: {e}")
        return "I'm sorry, I couldn't process that request."
```

## Step 7: Running the API

To run our FastAPI application, we can use Uvicorn. Add this to the bottom of `api/main.py`:

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Now you can run your API with:

```bash
python -m api.main
```

Your API will be available at `http://localhost:8000`, and you can access the auto-generated documentation at `http://localhost:8000/docs`.

## Conclusion

In this lesson, we've transformed our CLI-based AI assistant into a web API using FastAPI. We've implemented authentication, rate limiting, and set up the core AI functionality as an API endpoint. This allows our AI assistant to be accessed from various clients, including web applications and mobile apps.

Key takeaways:
1. FastAPI provides a modern, fast framework for building APIs with Python.
2. JWT-based authentication helps secure our API.
3. Rate limiting is crucial for protecting our API from abuse.
4. Organizing our code into routes, services, and models helps maintain a clean and scalable structure.
5. Asynchronous programming in Python allows for efficient handling of I/O-bound operations, such as API calls to the AI service.

In the next lesson, we'll focus on creating a frontend application that consumes this API, providing a web-based interface for our AI assistant.
