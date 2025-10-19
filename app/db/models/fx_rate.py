from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, DateTime, Numeric, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class FxRate(Base):

    __tablename__ = "fx_rates"
    __table_args__ = (
        Index("idx_currency_pair_date", "base_currency", "quote_currency", "rate_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    base_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    quote_currency: Mapped[str] = mapped_column(String(3), nullable=False)

    rate: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=8),
        nullable=False
    )

    rate_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    source: Mapped[str] = mapped_column(
        String(50),
        default="frankfurter.app",
        nullable=False
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

    def __repr__(self) -> str:
        return (
            f"<FxRate(id={self.id}, {self.base_currency}/{self.quote_currency}={self.rate}, "
            f"date={self.rate_date})>"
        )
