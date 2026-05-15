from fastapi import HTTPException, Request, status
from app.core.redis import redis_client


async def login_rate_limit(request: Request):
    # Use client IP as identifier
    client_ip = request.client.host
    key = f"rate_limit:login:{client_ip}"

    # Get current attempt count
    current = await redis_client.get(key)

    if current is None:
        # First attempt — create counter with 60 second window
        await redis_client.setex(key, 60, 1)
    elif int(current) >= 5:
        # Too many attempts
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Try again in 60 seconds."
        )
    else:
        # Increment counter
        await redis_client.incr(key)
