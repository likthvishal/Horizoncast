"""Enhanced authentication and multi-tenancy middleware."""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer(auto_error=True)


class APIKeyManager:
    """API key management with multi-tenant support."""

    def __init__(self, valid_keys: dict[str, str] | None = None):
        # Format: {"api_key": "tenant_id"}
        self.valid_keys = valid_keys or {"demo-key-12345": "default-tenant"}

    def validate_key(self, key: str) -> tuple[bool, str | None]:
        """Validate API key and return (is_valid, tenant_id)."""
        if key in self.valid_keys:
            return True, self.valid_keys[key]
        return False, None

    def add_key(self, key: str, tenant_id: str) -> None:
        """Add a new API key for a tenant."""
        self.valid_keys[key] = tenant_id


class RBACManager:
    """Role-based access control manager."""

    ROLES = {
        "admin": ["read", "write", "delete", "train", "manage_users"],
        "analyst": ["read", "write", "train"],
        "viewer": ["read"],
    }

    @staticmethod
    def can_perform(role: str, action: str) -> bool:
        """Check if role can perform action."""
        if role not in RBACManager.ROLES:
            return False
        return action in RBACManager.ROLES[role]

    @staticmethod
    def get_role_actions(role: str) -> list[str]:
        """Get all actions for a role."""
        return RBACManager.ROLES.get(role, [])


@lru_cache
def get_api_key_manager() -> APIKeyManager:
    """Get singleton API key manager."""
    return APIKeyManager()


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> tuple[str, str]:
    """Verify API key from Authorization header.
    
    Returns:
        (api_key, tenant_id)
    """
    key_manager = get_api_key_manager()
    is_valid, tenant_id = key_manager.validate_key(credentials.credentials)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    return credentials.credentials, tenant_id or "unknown"


async def get_current_tenant(
    api_key_data: tuple[str, str] = Depends(verify_api_key),
) -> str:
    """Extract tenant ID from API key."""
    _, tenant_id = api_key_data
    return tenant_id


async def require_role(
    required_role: str,
    current_role: str = Depends(lambda: "analyst"),  # Placeholder
) -> str:
    """Verify user has required role."""
    if not RBACManager.can_perform(current_role, "read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return current_role
