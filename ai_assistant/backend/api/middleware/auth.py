# backend/api/middleware/auth.py

from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from ...utils.config import SECRET_KEY, ALGORITHM

security = HTTPBearer()

async def auth_middleware(request: Request, call_next):
    if request.url.path in ["/", "/docs", "/redoc", "/openapi.json", "/auth/token"]:
        return await call_next(request)

    try:
        token = await security(request)
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        request.state.user = payload
    except (JWTError, AttributeError):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return await call_next(request)

async def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")