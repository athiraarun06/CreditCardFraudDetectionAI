"""
Lightweight in-memory sliding-window rate limiter. Good enough for a single-process demo/portfolio
deployment; for multi-instance production use, swap this for a Redis-backed limiter instead.
"""
import time
from collections import defaultdict, deque
from fastapi import Request
from fastapi.responses import JSONResponse

WINDOW_SECONDS = 60
MAX_REQUESTS_PER_WINDOW = 120
_hits: dict[str, deque] = defaultdict(deque)


async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    window = _hits[client_ip]

    while window and now - window[0] > WINDOW_SECONDS:
        window.popleft()

    if len(window) >= MAX_REQUESTS_PER_WINDOW:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please slow down and try again shortly."},
        )

    window.append(now)
    return await call_next(request)
