from fastapi import HTTPException, Request, status
from app.utils.redis_client import redis_client
from app.core.config import settings
import time


async def rate_limit_check(request: Request, user_id: int = None):
    if user_id:
        key = f"rate_limit:user:{user_id}"
    else:
        client_ip = request.client.host
        key = f"rate_limit:ip:{client_ip}"

    current_time = int(time.time())
    window_start = current_time - 60

    try:
        pipe_key = f"{key}:{current_time // 60}"

        current_count = await redis_client.get(pipe_key)
        if current_count is None:
            current_count = 0
        else:
            current_count = int(current_count)

        if current_count >= settings.rate_limit_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )

        await redis_client.set(pipe_key, str(current_count + 1), ttl=60)

    except HTTPException:
        raise
    except Exception:
        pass
