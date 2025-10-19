from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, DateTime, Numeric, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Account(Base):

    __tablename__ = "accounts"
    __table_args__ = (
        Index("idx_user_currency", "user_id", "currency"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    balance: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=2),
        default=Decimal("0.00"),
        nullable=False
    )

    fixed_commission: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=2),
        nullable=True
    )
    percentage_commission: Mapped[Decimal] = mapped_column(
        Numeric(precision=5, scale=4),
        nullable=True
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

    user: Mapped["User"] = relationship("User", back_populates="accounts")

    def __repr__(self) -> str:
        return f"<Account(id={self.id}, user_id={self.user_id}, currency={self.currency}, balance={self.balance})>"
