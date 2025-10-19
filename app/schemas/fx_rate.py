from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class FxRateResponse(BaseModel):

    id: int
    base_currency: str = Field(min_length=3, max_length=3)
    quote_currency: str = Field(min_length=3, max_length=3)
    rate: Decimal
    rate_date: datetime
    source: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "base_currency": "USD",
                "quote_currency": "EUR",
                "rate": "0.92",
                "rate_date": "2024-01-01T00:00:00",
                "source": "frankfurter.app",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }
    )


class FxRateListResponse(BaseModel):

    base: str
    date: str
    rates: dict[str, Decimal]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "base": "USD",
                "date": "2024-01-01",
                "rates": {
                    "EUR": "0.92",
                    "GBP": "0.79",
                    "JPY": "110.50"
                }
            }
        }
    )
