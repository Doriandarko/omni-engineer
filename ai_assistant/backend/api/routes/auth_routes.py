from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from ..models.auth_models import Token, User
from ..services.auth_service import AuthService

router = APIRouter()
auth_service = AuthService()

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = auth_service.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=User)
async def register_user(user: User):
    try:
        new_user = auth_service.create_user(user)
        return new_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))