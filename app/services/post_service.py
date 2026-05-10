from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate
from app.crud import post_crud


async def get_post(db: AsyncSession, post_id: int) -> Post | None:
    post = await post_crud.get_by_id(db, post_id)
    if not post:
        raise ValueError("Post Not Found")
    return post


async def get_all_posts(db: AsyncSession, skip: int = 0, limit: int = 10) -> Sequence[Post]:
    return await post_crud.get_all(db, skip, limit)


async def create(db: AsyncSession, data: PostCreate, owner_id: int) -> Post:
    return await post_crud.create(db, data, owner_id)


async def update(db: AsyncSession, post_id: int, data: PostUpdate, current_user_id: int) -> Post:
    post = await post_crud.get_by_id(db, post_id)
    if not post:
        raise ValueError("Post Not Found")
    if post.owner_id != current_user_id:
        raise ValueError("Not Authorized")
    return await post_crud.update(db, post, data)


async def delete(db: AsyncSession, post_id: int, current_user_id: int) -> None:
    post = await post_crud.get_by_id(db, post_id)
    if not post:
        raise ValueError("Post Not Found")
    if post.owner_id != current_user_id:
        raise ValueError("Not Authorized")
    await post_crud.delete(db, post)