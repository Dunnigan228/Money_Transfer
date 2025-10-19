from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db.models.transfer import Transfer, TransferStatus
from app.db.models.account import Account
from app.db.models.ledger_entry import LedgerEntry, LedgerEntryType
from app.db.models.user import User
from app.services.fx_rate_service import FxRateService
from app.services.account_service import AccountService
from app.schemas.transfer import TransferCreate


class TransferService:

    def __init__(self):
        self.fx_service = FxRateService()
        self.account_service = AccountService()

    def calculate_commission(
        self,
        amount: Decimal,
        fixed_commission: Optional[Decimal] = None,
        percentage_commission: Optional[Decimal] = None,
    ) -> Decimal:
        fixed = fixed_commission or Decimal(str(settings.default_fixed_commission))
        percentage = percentage_commission or Decimal(
            str(settings.default_percentage_commission)
        )

        commission = fixed + (amount * percentage)
        return commission.quantize(Decimal("0.01"))

    async def create_transfer(
        self,
        db: AsyncSession,
        user: User,
        transfer_data: TransferCreate,
        idempotency_key: Optional[str] = None,
    ) -> Transfer:
        if idempotency_key:
            stmt = select(Transfer).where(Transfer.idempotency_key == idempotency_key)
            result = await db.execute(stmt)
            existing_transfer = result.scalar_one_or_none()

            if existing_transfer:
                if existing_transfer.user_id != user.id:
                    raise ValueError("Idempotency key already used by another user")

                return existing_transfer

        from_account = await self.account_service.get_account_by_id(
            db, transfer_data.from_account_id
        )
        to_account = await self.account_service.get_account_by_id(
            db, transfer_data.to_account_id
        )

        if not from_account:
            raise ValueError("Source account not found")
        if not to_account:
            raise ValueError("Destination account not found")

        if from_account.user_id != user.id:
            raise ValueError("You don't own the source account")

        from_currency = from_account.currency
        to_currency = to_account.currency

        if transfer_data.from_amount is not None:
            from_amount = transfer_data.from_amount
            to_amount, exchange_rate = await self.fx_service.convert_amount(
                db, from_amount, from_currency, to_currency
            )
        else:
            to_amount = transfer_data.to_amount
            from_amount, inverse_rate = await self.fx_service.convert_amount(
                db, to_amount, to_currency, from_currency
            )
            exchange_rate = Decimal("1.0") / inverse_rate if inverse_rate != 0 else Decimal("1.0")

        commission = self.calculate_commission(
            from_amount,
            from_account.fixed_commission,
            from_account.percentage_commission,
        )

        total_debit = from_amount + commission

        if not await self.account_service.check_sufficient_balance(
            from_account, total_debit
        ):
            raise ValueError("Insufficient funds")

        transfer = Transfer(
            from_account_id=from_account.id,
            to_account_id=to_account.id,
            from_currency=from_currency,
            to_currency=to_currency,
            from_amount=from_amount,
            to_amount=to_amount,
            exchange_rate=exchange_rate,
            commission_amount=commission,
            fixed_commission=from_account.fixed_commission or Decimal("0.00"),
            percentage_commission=from_account.percentage_commission or Decimal("0.00"),
            status=TransferStatus.CREATED,
            user_id=user.id,
            idempotency_key=idempotency_key,
            description=transfer_data.description,
        )

        db.add(transfer)
        await db.flush()
        await db.refresh(transfer)

        return transfer

    async def execute_transfer(
        self,
        db: AsyncSession,
        transfer: Transfer,
    ) -> Transfer:
        try:
            transfer.status = TransferStatus.PROCESSING
            await db.flush()

            from_account = await self.account_service.get_account_by_id(
                db, transfer.from_account_id
            )
            to_account = await self.account_service.get_account_by_id(
                db, transfer.to_account_id
            )

            if not from_account or not to_account:
                raise ValueError("Account not found")

            total_debit = transfer.from_amount + transfer.commission_amount
            await self.account_service.update_balance(
                db, from_account, -total_debit
            )

            debit_entry = LedgerEntry(
                account_id=from_account.id,
                transfer_id=transfer.id,
                entry_type=LedgerEntryType.DEBIT,
                amount=total_debit,
                currency=from_account.currency,
                balance_after=from_account.balance,
                description=f"Transfer to account {to_account.id}",
            )
            db.add(debit_entry)

            await self.account_service.update_balance(
                db, to_account, transfer.to_amount
            )

            credit_entry = LedgerEntry(
                account_id=to_account.id,
                transfer_id=transfer.id,
                entry_type=LedgerEntryType.CREDIT,
                amount=transfer.to_amount,
                currency=to_account.currency,
                balance_after=to_account.balance,
                description=f"Transfer from account {from_account.id}",
            )
            db.add(credit_entry)

            transfer.status = TransferStatus.COMPLETED
            transfer.completed_at = datetime.utcnow()

            await db.commit()
            await db.refresh(transfer)

            return transfer

        except Exception as e:
            transfer.status = TransferStatus.FAILED
            transfer.error_message = str(e)
            await db.commit()
            raise

    async def get_transfer_by_id(
        self,
        db: AsyncSession,
        transfer_id: int,
    ) -> Optional[Transfer]:
        stmt = select(Transfer).where(Transfer.id == transfer_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_transfers(
        self,
        db: AsyncSession,
        user_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Transfer]:
        stmt = (
            select(Transfer)
            .where(Transfer.user_id == user_id)
            .order_by(Transfer.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_account_transfers(
        self,
        db: AsyncSession,
        account_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Transfer]:
        stmt = (
            select(Transfer)
            .where(
                or_(
                    Transfer.from_account_id == account_id,
                    Transfer.to_account_id == account_id,
                )
            )
            .order_by(Transfer.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())
