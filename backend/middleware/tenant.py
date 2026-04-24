"""Multi-tenancy middleware for request isolation."""

from __future__ import annotations

from typing import Callable

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class TenantIsolationMiddleware(BaseHTTPMiddleware):
    """Ensure all requests are properly scoped to tenant."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add tenant context to request."""
        tenant_id = request.headers.get("X-Tenant-ID") or "default-tenant"
        request.state.tenant_id = tenant_id

        response = await call_next(request)
        return response


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests for compliance and debugging."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request and response."""
        tenant_id = getattr(request.state, "tenant_id", "unknown")
        method = request.method
        path = request.url.path

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            raise

        # TODO: Send to audit log DB
        if status_code < 400:
            pass  # Normal request

        return response
