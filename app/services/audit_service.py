from typing import Optional, Dict, Any, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.audit import Audit
from app.db.models.user import User


class AuditService:

    async def log_action(
        self,
        db: AsyncSession,
        action: str,
        entity_type: str,
        entity_id: Optional[int] = None,
        user: Optional[User] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Audit:
        audit = Audit(
            user_id=user.id if user else None,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        db.add(audit)
        await db.flush()
        await db.refresh(audit)

        return audit

    async def get_user_audit_logs(
        self,
        db: AsyncSession,
        user_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Audit]:
        stmt = (
            select(Audit)
            .where(Audit.user_id == user_id)
            .order_by(Audit.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_entity_audit_logs(
        self,
        db: AsyncSession,
        entity_type: str,
        entity_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Audit]:
        stmt = (
            select(Audit)
            .where(Audit.entity_type == entity_type, Audit.entity_id == entity_id)
            .order_by(Audit.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_all_audit_logs(
        self,
        db: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Audit]:
        stmt = (
            select(Audit)
            .order_by(Audit.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())
