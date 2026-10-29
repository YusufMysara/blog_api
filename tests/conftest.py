"""Test setup: a real PostgreSQL database built by the Alembic migrations, and a real Redis.

Settings come from environment variables (CI sets them); the defaults below match the
throwaway containers described in the README. The database name must end in "_test",
so the tests can never run against the development database.
"""
import asyncio
import os
from pathlib import Path

# Must happen before any app module is imported: settings and the engine are created at import time.
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5435/blog_test")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6381")

import asyncpg
import pytest
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.engine import make_url

from app.core.redis import redis_client
from app.database import engine
from main import app

ROOT = Path(__file__).resolve().parents[1]
DB_URL = make_url(os.environ["DATABASE_URL"])


async def _recreate_database() -> None:
    connection = await asyncpg.connect(
        user=DB_URL.username, password=DB_URL.password, host=DB_URL.host, port=DB_URL.port, database="postgres"
    )
    try:
        await connection.execute(f'DROP DATABASE IF EXISTS "{DB_URL.database}" WITH (FORCE)')
        await connection.execute(f'CREATE DATABASE "{DB_URL.database}"')
    finally:
        await connection.close()


@pytest.fixture(scope="session", autouse=True)
def database():
    """A fresh test database, built by the real migrations (so the migrations are tested too)."""
    assert DB_URL.database.endswith("_test"), "tests must never run against the development database"
    asyncio.run(_recreate_database())
    command.upgrade(Config(str(ROOT / "alembic.ini")), "head")
    yield


@pytest.fixture(autouse=True)
async def clean_state(database):
    """Empty every table and Redis after each test, so no test depends on another."""
    yield
    async with engine.begin() as connection:
        await connection.execute(text("TRUNCATE users, posts, tags, post_tags RESTART IDENTITY CASCADE"))
    await redis_client.flushdb()


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as http_client:
        yield http_client
