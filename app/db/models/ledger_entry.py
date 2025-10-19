from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, DateTime, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
import enum


class LedgerEntryType(str, enum.Enum):
    DEBIT = "debit"
    CREDIT = "credit"


class LedgerEntry(Base):

    __tablename__ = "ledger_entries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id"),
        nullable=False,
        index=True
    )

    transfer_id: Mapped[int] = mapped_column(
        ForeignKey("transfers.id"),
        nullable=False,
        index=True
    )

    entry_type: Mapped[LedgerEntryType] = mapped_column(
        SQLEnum(LedgerEntryType),
        nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=2),
        nullable=False
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False)

    balance_after: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=2),
        nullable=False
    )

    description: Mapped[str] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"<LedgerEntry(id={self.id}, account_id={self.account_id}, "
            f"type={self.entry_type}, amount={self.amount})>"
        )
