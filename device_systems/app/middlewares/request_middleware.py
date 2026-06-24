"""
Custom request middleware for device_systems.
Adds traceability headers, measures response time, and logs request information.
"""

import time
import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Configure logger
logger = logging.getLogger("device_systems")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class RequestMiddleware(BaseHTTPMiddleware):
    """
    Custom middleware that:
    - Measures response time and adds X-Process-Time header
    - Adds X-App-Name header
    - Generates or propagates X-Request-ID header
    - Logs method, path, and status code for every request
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Generate or propagate request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])

        # Record start time
        start_time = time.time()

        # Process the request
        response: Response = await call_next(request)

        # Calculate processing time
        process_time = time.time() - start_time

        # Add custom headers to response
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        response.headers["X-App-Name"] = "device_systems"
        response.headers["X-Request-ID"] = request_id

        # Log request details
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} "
            f"- Status: {response.status_code} "
            f"- Time: {process_time:.4f}s"
        )

        return response
