from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.common import ResponseModel
from app.services.audit_service import AuditService
from app.core.dependencies import get_current_admin_user
from app.db.models.user import User
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/audit", tags=["Audit"])


class AuditLogResponse(BaseModel):
    id: int
    user_id: int | None
    action: str
    entity_type: str
    entity_id: int | None
    ip_address: str | None
    description: str | None
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/logs", response_model=ResponseModel[List[AuditLogResponse]])
async def get_audit_logs(
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    audit_service = AuditService()

    logs = await audit_service.get_all_audit_logs(db, limit, offset)

    return ResponseModel(
        status="success",
        message=f"Retrieved {len(logs)} audit logs",
        data=[AuditLogResponse.model_validate(log) for log in logs],
    )
