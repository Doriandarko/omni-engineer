# backend/api/services/auth_service.py

from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from ..models.auth_models import User, UserInDB
from ...utils.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return pwd_context.hash(password)

    def authenticate_user(self, username: str, password: str):
        user = self.get_user(username)
        if not user:
            return False
        if not self.verify_password(password, user.hashed_password):
            return False
        return user

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def get_user(self, username: str):
        # In a real application, this would query a database
        # For this example, we'll use a hardcoded user
        if username == "testuser":
            return UserInDB(
                username=username,
                email="testuser@example.com",
                full_name="Test User",
                hashed_password=self.get_password_hash("testpassword")
            )

    def create_user(self, user: User):
        # In a real application, this would insert the user into a database
        # For this example, we'll just return the user with a hashed password
        hashed_password = self.get_password_hash(user.password)
        return UserInDB(**user.dict(), hashed_password=hashed_password)