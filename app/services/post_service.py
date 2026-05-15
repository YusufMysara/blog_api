import json
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import redis_client
from app.crud import post_crud
from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate

CACHE_TTL = 60  # seconds


async def _invalidate_posts_cache() -> None:
    async for key in redis_client.scan_iter("cache:posts:*"):
        await redis_client.delete(key)


async def get_post(db: AsyncSession, post_id: int) -> Post:
    post = await post_crud.get_by_id(db, post_id)
    if not post:
        raise ValueError("Post Not Found")
    return post


async def get_all_posts(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10
) -> Sequence[Post]:
    # Step 1 — check cache first
    cache_key = f"cache:posts:{skip}:{limit}"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # Step 2 — cache miss, query database
    posts = await post_crud.get_all(db, skip, limit)

    # Step 3 — serialize and store in cache
    posts_data = [
        {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "is_published": post.is_published,
            "owner_id": post.owner_id,
            "created_at": str(post.created_at),
            "updated_at": str(post.updated_at),
            "author": {
                "id": post.author.id,
                "name": post.author.name,
                "email": post.author.email,
                "is_active": post.author.is_active,
                "created_at": str(post.author.created_at)
            } if post.author else None
        }
        for post in posts
    ]
    await redis_client.setex(cache_key, CACHE_TTL, json.dumps(posts_data))

    return posts


async def create(
    db: AsyncSession,
    data: PostCreate,
    owner_id: int
) -> Post:
    post = await post_crud.create(db, data, owner_id)
    await _invalidate_posts_cache()
    return post


async def update(
    db: AsyncSession,
    post_id: int,
    data: PostUpdate,
    current_user_id: int
) -> Post:
    post = await post_crud.get_by_id(db, post_id)
    if not post:
        raise ValueError("Post Not Found")
    if post.owner_id != current_user_id:
        raise ValueError("Not Authorized")
    updated = await post_crud.update(db, post, data)
    await _invalidate_posts_cache()
    return updated


async def delete(
    db: AsyncSession,
    post_id: int,
    current_user_id: int
) -> None:
    post = await post_crud.get_by_id(db, post_id)
    if not post:
        raise ValueError("Post Not Found")
    if post.owner_id != current_user_id:
        raise ValueError("Not Authorized")
    await post_crud.delete(db, post)
    await _invalidate_posts_cache()