from app.database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import PostResponse, PostCreate, PostUpdate
from app.services import post_service
from app.dependencies.auth import get_current_user
from app.models import User

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    try:
        post = await post_service.get_post(db, post_id)
        return post
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/", response_model=list[PostResponse])
async def get_all_posts(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    return await post_service.get_all_posts(db, skip, limit)


@router.post("/", response_model=PostResponse)
async def create_post(data: PostCreate, db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    return await post_service.create(db, data, current_user.id)


@router.put("/{post_id}", response_model=PostResponse)
async def update(post_id: int, data: PostUpdate, current_user: User = Depends(get_current_user),
                 db: AsyncSession = Depends(get_db)):
    try:
        return await post_service.update(db, post_id, data, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(post_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        await post_service.delete(db, post_id, current_user.id)
    except ValueError as e:
        error_message = str(e)
        if "Not Found" in error_message:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)
        if "Not Authorized" in error_message:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)
