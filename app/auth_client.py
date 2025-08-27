import os
import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

load_dotenv()
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:5001")

security = HTTPBearer()


class User:
    def __init__(self, user_data: dict):
        self.id = user_data.get("id")
        self.email = user_data.get("email")
        self.is_active = user_data.get("is_active", True)
        self.is_superuser = user_data.get("is_superuser", False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:

    token = credentials.credentials

    try:
        response = requests.get(
            f"{AUTH_SERVICE_URL}/users/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )

        if response.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        elif response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

        user_data = response.json()
        return User(user_data)

    except requests.RequestException:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable",
        )


async def get_current_superuser(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return current_user
