from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, DateTime, Numeric, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
import enum


class TransferStatus(str, enum.Enum):
    CREATED = "created"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Transfer(Base):

    __tablename__ = "transfers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    from_account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id"),
        nullable=False,
        index=True
    )
    to_account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id"),
        nullable=False,
        index=True
    )

    from_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    to_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    from_amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=2),
        nullable=False
    )
    to_amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=2),
        nullable=False
    )

    exchange_rate: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=8),
        nullable=False
    )
    commission_amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=2),
        default=Decimal("0.00"),
        nullable=False
    )
    fixed_commission: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=2),
        default=Decimal("0.00"),
        nullable=False
    )
    percentage_commission: Mapped[Decimal] = mapped_column(
        Numeric(precision=5, scale=4),
        default=Decimal("0.00"),
        nullable=False
    )

    status: Mapped[TransferStatus] = mapped_column(
        SQLEnum(TransferStatus),
        default=TransferStatus.CREATED,
        nullable=False,
        index=True
    )
    idempotency_key: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Transfer(id={self.id}, from_account={self.from_account_id}, "
            f"to_account={self.to_account_id}, status={self.status})>"
        )
