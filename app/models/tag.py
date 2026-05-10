import uuid
from sqlalchemy import Column, String, Table, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.database import Base

post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True)
)

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)

    posts = relationship("Post", secondary=post_tags, back_populates="tags")

    def __repr__(self):
        return f"<Tag {self.name}>"