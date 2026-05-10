from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.core.security import verify_token
from app.crud.user_crud import get_by_email

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
http_bearer = HTTPBearer()


async def get_current_user(db: AsyncSession = Depends(get_db),
                           credentials: HTTPAuthorizationCredentials = Depends(http_bearer)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    payload = verify_token(token)
    if not payload:
        raise credentials_exception

    email = payload.get("sub")
    if not email:
        raise credentials_exception

    user = await get_by_email(db, email)
    if not user:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")

    return user
