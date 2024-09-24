# backend/api/middleware/rate_limit.py

from fastapi import Request, HTTPException
from collections import defaultdict
import time

RATE_LIMIT = 100  # requests per minute
RATE_LIMIT_PERIOD = 60  # seconds

request_counts = defaultdict(list)

async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()
    
    # Remove old timestamps
    request_counts[client_ip] = [t for t in request_counts[client_ip] if current_time - t < RATE_LIMIT_PERIOD]
    
    if len(request_counts[client_ip]) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    request_counts[client_ip].append(current_time)
    
    return await call_next(request)