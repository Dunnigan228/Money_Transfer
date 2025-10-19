from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.account import AccountCreate, AccountResponse, AccountOperationRequest
from app.schemas.common import ResponseModel
from app.services.account_service import AccountService
from app.services.audit_service import AuditService
from app.core.dependencies import get_current_active_user
from app.db.models.user import User
from app.utils.localization import localization

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("", response_model=ResponseModel[AccountResponse], status_code=status.HTTP_201_CREATED)
async def create_account(
    account_data: AccountCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    account_service = AccountService()
    audit_service = AuditService()

    try:
        account = await account_service.create_account(db, current_user, account_data)

        await audit_service.log_action(
            db=db,
            action="account_created",
            entity_type="account",
            entity_id=account.id,
            user=current_user,
            new_values={"currency": account.currency, "balance": str(account.balance)},
        )

        await db.commit()

        return ResponseModel(
            status="success",
            message=f"Account created for {account.currency}",
            data=AccountResponse.model_validate(account),
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=ResponseModel[List[AccountResponse]])
async def get_accounts(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    account_service = AccountService()

    accounts = await account_service.get_user_accounts(db, current_user.id)

    return ResponseModel(
        status="success",
        message=f"Retrieved {len(accounts)} accounts",
        data=[AccountResponse.model_validate(acc) for acc in accounts],
    )


@router.get("/{account_id}", response_model=ResponseModel[AccountResponse])
async def get_account(
    account_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    account_service = AccountService()

    account = await account_service.get_account_by_id(db, account_id)

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=localization.translate("account_not_found", current_user.preferred_language),
        )

    if account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this account",
        )

    return ResponseModel(
        status="success",
        message="Account retrieved",
        data=AccountResponse.model_validate(account),
    )


@router.post("/{account_id}/deposit", response_model=ResponseModel[AccountResponse])
async def deposit_to_account(
    account_id: int,
    operation: AccountOperationRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    account_service = AccountService()
    audit_service = AuditService()

    account = await account_service.get_account_by_id(db, account_id)

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=localization.translate("account_not_found", current_user.preferred_language),
        )

    if account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this account",
        )

    old_balance = account.balance

    try:
        await account_service.update_balance(db, account, operation.amount)

        await audit_service.log_action(
            db=db,
            action="account_deposit",
            entity_type="account",
            entity_id=account.id,
            user=current_user,
            old_values={"balance": str(old_balance)},
            new_values={"balance": str(account.balance), "amount": str(operation.amount)},
        )

        await db.commit()

        return ResponseModel(
            status="success",
            message=f"Deposited {operation.amount} {account.currency}",
            data=AccountResponse.model_validate(account),
        )

    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{account_id}/withdraw", response_model=ResponseModel[AccountResponse])
async def withdraw_from_account(
    account_id: int,
    operation: AccountOperationRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    account_service = AccountService()
    audit_service = AuditService()

    account = await account_service.get_account_by_id(db, account_id)

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=localization.translate("account_not_found", current_user.preferred_language),
        )

    if account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this account",
        )

    if not await account_service.check_sufficient_balance(account, operation.amount):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=localization.translate("insufficient_funds", current_user.preferred_language),
        )

    old_balance = account.balance

    try:
        await account_service.update_balance(db, account, -operation.amount)

        await audit_service.log_action(
            db=db,
            action="account_withdraw",
            entity_type="account",
            entity_id=account.id,
            user=current_user,
            old_values={"balance": str(old_balance)},
            new_values={"balance": str(account.balance), "amount": str(operation.amount)},
        )

        await db.commit()

        return ResponseModel(
            status="success",
            message=f"Withdrawn {operation.amount} {account.currency}",
            data=AccountResponse.model_validate(account),
        )

    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
