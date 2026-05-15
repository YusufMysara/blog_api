import redis.asyncio as redis
from app.core.config import setting

redis_client = redis.Redis(
    host=setting.REDIS_HOST,
    port=setting.REDIS_PORT,
    db=0,
    decode_responses=True
)