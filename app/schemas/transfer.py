from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator


class TransferBase(BaseModel):

    from_account_id: int
    to_account_id: int
    description: Optional[str] = None


class TransferCreate(TransferBase):

    from_amount: Optional[Decimal] = Field(default=None, gt=0)
    to_amount: Optional[Decimal] = Field(default=None, gt=0)

    @model_validator(mode='after')
    def validate_amounts(self):
        from_amt = self.from_amount
        to_amt = self.to_amount

        if from_amt is None and to_amt is None:
            raise ValueError("Either from_amount or to_amount must be specified")
        if from_amt is not None and to_amt is not None:
            raise ValueError("Only one of from_amount or to_amount should be specified")
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "from_account_id": 1,
                "to_account_id": 2,
                "from_amount": "100.00",
                "description": "Payment for services"
            }
        }
    )


class TransferResponse(TransferBase):

    id: int
    from_currency: str
    to_currency: str
    from_amount: Decimal
    to_amount: Decimal
    exchange_rate: Decimal
    commission_amount: Decimal
    fixed_commission: Decimal
    percentage_commission: Decimal
    status: str
    user_id: int
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "from_account_id": 1,
                "to_account_id": 2,
                "from_currency": "USD",
                "to_currency": "EUR",
                "from_amount": "100.00",
                "to_amount": "92.00",
                "exchange_rate": "0.92",
                "commission_amount": "1.00",
                "fixed_commission": "0.00",
                "percentage_commission": "0.01",
                "status": "completed",
                "user_id": 1,
                "description": "Payment for services",
                "error_message": None,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "completed_at": "2024-01-01T00:00:05"
            }
        }
    )
