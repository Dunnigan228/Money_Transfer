from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class AccountBase(BaseModel):

    currency: str = Field(min_length=3, max_length=3, description="ISO 4217 currency code")


class AccountCreate(AccountBase):

    fixed_commission: Optional[Decimal] = Field(default=None, ge=0)
    percentage_commission: Optional[Decimal] = Field(default=None, ge=0, le=1)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "currency": "USD",
                "fixed_commission": 0.0,
                "percentage_commission": 0.01
            }
        }
    )


class AccountResponse(AccountBase):

    id: int
    user_id: int
    balance: Decimal
    fixed_commission: Optional[Decimal]
    percentage_commission: Optional[Decimal]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": 1,
                "currency": "USD",
                "balance": "1000.00",
                "fixed_commission": None,
                "percentage_commission": None,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }
    )


class AccountOperationRequest(BaseModel):

    amount: Decimal = Field(gt=0, description="Amount to deposit or withdraw")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "amount": "1000.00"
            }
        }
    )
