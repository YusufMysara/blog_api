from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password


async def get_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def get_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def get_all(db: AsyncSession, skip: int = 0, limit: int = 10) -> list[User] | None:
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()


async def create(db: AsyncSession, data: UserCreate) -> User:
    print(f"Password being hashed: {data.password}")
    print(f"Password length: {len(data.password)}")
    user = User(
        name=data.name,
        email=data.email,
        password=hash_password(data.password)
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def update(db: AsyncSession, user: User, data: UserUpdate) -> User:
    update_data = data.model_dump(exclude_none=True)

    if "password" in update_data:
        user.password = hash_password(update_data["password"])

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.flush()
    await db.refresh(user)
    return user


async def delete(db: AsyncSession, user: User) -> None:
    await db.delete(user)
    await db.flush()
