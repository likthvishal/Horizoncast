"""Authentication and authorization utilities."""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()


class APIKeyManager:
    """Simple API key management (for prototype; use OAuth2 in production)."""

    def __init__(self, valid_keys: list[str] | None = None):
        self.valid_keys = set(valid_keys or ["demo-key-12345"])

    def validate_key(self, key: str) -> bool:
        """Check if key is valid."""
        return key in self.valid_keys

    def add_key(self, key: str) -> None:
        """Add a new valid key."""
        self.valid_keys.add(key)


@lru_cache
def get_api_key_manager() -> APIKeyManager:
    """Get singleton API key manager."""
    return APIKeyManager()


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Verify API key from Authorization header."""
    key_manager = get_api_key_manager()
    if not key_manager.validate_key(credentials.credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return credentials.credentials


async def get_current_tenant(api_key: str = Depends(verify_api_key)) -> str:
    """Extract tenant ID from API key (placeholder)."""
    return "default-tenant"
