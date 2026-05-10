from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import setting

# engine is the connection pool -> You can send thousands of requests over one connection.
engine = create_async_engine(setting.DATABASE_URL, echo=True)

# Session Factory
#sessionmaker is a factory function — it creates a class that produces sessions with specific settings baked in.
#AsyncSessionLocal is now a class — not a session, not a connection. A class that creates sessions with those exact settings every time you call it.
# session is a workplace that uses a connection temporarily
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


#One engine. One factory. Thousands of sessions over the app's lifetime.


#DeclarativeBase is a factory — every direct inheritance creates a new isolated registry.
# Base is one instance from that factory — everyone who inherits it shares the same registry.
#if classes share the same registry, they can have relationships and alembic see them together
class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:      #session = AsyncSessionLocal()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
