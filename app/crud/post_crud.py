from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate


async def get_by_id(db: AsyncSession, post_id: int) -> Post | None:
    result = await db.execute(
        select(Post)
        .options(joinedload(Post.author))
        .where(Post.id == post_id)
    )
    return result.unique().scalars().first()


async def get_all(db: AsyncSession, skip: int = 0, limit: int = 10) -> Sequence[Post]:
    result = await db.execute(
        select(Post)
        .options(joinedload(Post.author))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_by_user_id(db: AsyncSession, user_id: int) -> list[Post]:
    result = await db.execute(select(Post).where(Post.owner_id == user_id))
    return result.scalars().all()


async def create(db: AsyncSession, data: PostCreate, owner_id: int) -> Post:
    post = Post(
        title=data.title,
        content=data.content,
        is_published=data.is_published,
        owner_id=owner_id
    )
    db.add(post)
    await db.flush()
    await db.refresh(post)
    return post


async def update(db: AsyncSession, post: Post, data: PostUpdate) -> Post:
    update_data = data.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(post, field, value)
    await db.flush()
    await db.refresh(post)
    return post


async def delete(db: AsyncSession, post: Post) -> None:
    await db.delete(post)
    await db.flush()
