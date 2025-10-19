from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.transfer import TransferCreate, TransferResponse
from app.schemas.common import ResponseModel
from app.services.transfer_service import TransferService
from app.services.audit_service import AuditService
from app.core.dependencies import get_current_active_user, get_idempotency_key
from app.db.models.user import User
from app.utils.message_broker import publish_transfer_task, publish_notification_task
from app.utils.localization import localization

router = APIRouter(prefix="/transfers", tags=["Transfers"])


@router.post("", response_model=ResponseModel[TransferResponse], status_code=status.HTTP_201_CREATED)
async def create_transfer(
    transfer_data: TransferCreate,
    current_user: User = Depends(get_current_active_user),
    idempotency_key: Optional[str] = Depends(get_idempotency_key),
    db: AsyncSession = Depends(get_db),
):
    transfer_service = TransferService()
    audit_service = AuditService()

    try:
        transfer = await transfer_service.create_transfer(
            db, current_user, transfer_data, idempotency_key
        )

        is_new_transfer = transfer.status.value == "created"

        if is_new_transfer:
            await audit_service.log_action(
                db=db,
                action="transfer_created",
                entity_type="transfer",
                entity_id=transfer.id,
                user=current_user,
                new_values={
                    "from_account_id": transfer.from_account_id,
                    "to_account_id": transfer.to_account_id,
                    "amount": str(transfer.from_amount),
                    "currency": transfer.from_currency,
                },
            )

            await db.commit()

            await publish_transfer_task(transfer.id)

            await publish_notification_task(
                current_user.id,
                localization.translate("transfer_completed", current_user.preferred_language),
                "info",
            )

            message = "Transfer created and queued for processing"
        else:
            message = "Transfer already exists (idempotent response)"

        return ResponseModel(
            status="success",
            message=message,
            data=TransferResponse.model_validate(transfer),
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=ResponseModel[List[TransferResponse]])
async def get_transfers(
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    transfer_service = TransferService()

    transfers = await transfer_service.get_user_transfers(
        db, current_user.id, limit, offset
    )

    return ResponseModel(
        status="success",
        message=f"Retrieved {len(transfers)} transfers",
        data=[TransferResponse.model_validate(t) for t in transfers],
    )


@router.get("/{transfer_id}", response_model=ResponseModel[TransferResponse])
async def get_transfer(
    transfer_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    transfer_service = TransferService()

    transfer = await transfer_service.get_transfer_by_id(db, transfer_id)

    if not transfer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transfer not found",
        )

    if transfer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this transfer",
        )

    return ResponseModel(
        status="success",
        message="Transfer retrieved",
        data=TransferResponse.model_validate(transfer),
    )
