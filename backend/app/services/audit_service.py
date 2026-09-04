"""Audit logging service for tracking significant actions."""
import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import AuditLog


async def audit(
    db: AsyncSession,
    organization_id: uuid.UUID,
    user_id: Optional[uuid.UUID],
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    details: dict = None,
    ip_address: Optional[str] = None,
):
    """
    Log an audit event.
    
    Args:
        db: Database session
        organization_id: Organization ID
        user_id: User ID (optional for system events)
        action: Action performed (e.g., 'auth:login_success', 'signal:ingest')
        resource_type: Type of resource (e.g., 'user', 'signal', 'opportunity')
        resource_id: ID of the resource (optional)
        details: Additional details (optional)
        ip_address: Client IP address (optional)
    """
    log = AuditLog(
        organization_id=organization_id,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {},
        ip_address=ip_address,
    )
    db.add(log)
    # Don't flush — let the caller's transaction handle it


async def audit_auth_event(
    db: AsyncSession,
    action: str,
    user_id: Optional[uuid.UUID] = None,
    organization_id: Optional[uuid.UUID] = None,
    ip_address: Optional[str] = None,
    details: dict = None,
):
    """Helper for authentication events."""
    if organization_id and user_id:
        await audit(
            db=db,
            organization_id=organization_id,
            user_id=user_id,
            action=action,
            resource_type="auth",
            details=details,
            ip_address=ip_address,
        )
