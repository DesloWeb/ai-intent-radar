"""Rate limiting middleware."""
from __future__ import annotations
import time
from collections import defaultdict
from typing import Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: Optional[int] = None):
        super().__init__(app)
        self.rpm = requests_per_minute or settings.RATE_LIMIT_PER_MINUTE
        self.requests: dict = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = 60.0

        # Clean old entries
        self.requests[client_ip] = [
            t for t in self.requests[client_ip] if now - t < window
        ]

        if len(self.requests[client_ip]) >= self.rpm:
            return Response(
                content='{"detail":"Rate limit exceeded. Try again later."}',
                status_code=429,
                media_type="application/json",
            )

        self.requests[client_ip].append(now)
        return await call_next(request)
