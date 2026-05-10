from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
from app.schemas.user import UserResponse


class PostCreate(BaseModel):
    title: str
    content: str
    is_published: bool = True

    @field_validator("title")
    def title_must_be_valid(cls, value):
        value = value.strip()
        if len(value) < 3:
            raise ValueError("Title must be at least 3 characters")
        return value

    @field_validator("content")
    def content_must_be_valid(cls, value):
        value = value.strip()
        if len(value) < 10:
            raise ValueError("Content must be at least 10 characters")
        return value


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    is_published: bool
    created_at: datetime
    updated_at: datetime
    owner_id: int
    author: UserResponse

    class Config:
        from_attributes = True


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_published: Optional[bool] = None
