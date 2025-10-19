from decimal import Decimal
from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.account import Account
from app.db.models.user import User
from app.schemas.account import AccountCreate


class AccountService:

    async def create_account(
        self,
        db: AsyncSession,
        user: User,
        account_data: AccountCreate,
    ) -> Account:
        stmt = select(Account).where(
            and_(
                Account.user_id == user.id,
                Account.currency == account_data.currency.upper(),
            )
        )
        result = await db.execute(stmt)
        existing_account = result.scalar_one_or_none()

        if existing_account:
            raise ValueError(
                f"Account already exists for currency {account_data.currency}"
            )

        account = Account(
            user_id=user.id,
            currency=account_data.currency.upper(),
            balance=Decimal("0.00"),
            fixed_commission=account_data.fixed_commission,
            percentage_commission=account_data.percentage_commission,
        )

        db.add(account)
        await db.commit()
        await db.refresh(account)

        return account

    async def get_user_accounts(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> List[Account]:
        stmt = select(Account).where(Account.user_id == user_id)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_account_by_id(
        self,
        db: AsyncSession,
        account_id: int,
    ) -> Optional[Account]:
        stmt = select(Account).where(Account.id == account_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_account_by_currency(
        self,
        db: AsyncSession,
        user_id: int,
        currency: str,
    ) -> Optional[Account]:
        stmt = select(Account).where(
            and_(
                Account.user_id == user_id,
                Account.currency == currency.upper(),
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_balance(
        self,
        db: AsyncSession,
        account: Account,
        amount: Decimal,
    ) -> Account:
        account.balance += amount

        if account.balance < 0:
            raise ValueError("Insufficient funds")

        await db.flush()
        await db.refresh(account)
        return account

    async def check_sufficient_balance(
        self,
        account: Account,
        amount: Decimal,
    ) -> bool:
        return account.balance >= amount
