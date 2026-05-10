from app.core.security import verify_password, create_access_token
from app.models import User
from app.schemas import UserCreate, UserLogin
from app.crud import user_crud
from sqlalchemy.ext.asyncio import AsyncSession


async def register(db: AsyncSession, data: UserCreate) -> User:
    existing_user = await user_crud.get_by_email(db, data.email)
    if existing_user:
        raise ValueError("Email already registered")

    user = await user_crud.create(db, data)
    return user


async def login(db: AsyncSession, data: UserLogin) -> dict:
    user = await user_crud.get_by_email(db, data.email)
    if not user:
        raise ValueError("Invalid credentials")

    if not verify_password(data.password, user.password):
        raise ValueError("Invalid credentials")

    if not user.is_active:
        raise ValueError("Account Disabled")

    access_token = create_access_token({"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}
