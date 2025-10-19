from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.fx_rate import FxRateResponse, FxRateListResponse
from app.schemas.common import ResponseModel
from app.services.fx_rate_service import FxRateService
from app.core.dependencies import get_current_active_user, get_current_admin_user
from app.db.models.user import User

router = APIRouter(prefix="/rates", tags=["Exchange Rates"])


@router.get("/latest", response_model=ResponseModel[FxRateListResponse])
async def get_latest_rates(
    base: str = "USD",
    current_user: User = Depends(get_current_active_user),
):
    fx_service = FxRateService()

    try:
        rates = await fx_service.fetch_latest_rates(base.upper())

        return ResponseModel(
            status="success",
            message=f"Latest rates for {base}",
            data=FxRateListResponse(
                base=base.upper(),
                date="latest",
                rates=rates,
            ),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/convert")
async def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    fx_service = FxRateService()

    try:
        from decimal import Decimal
        converted_amount, rate = await fx_service.convert_amount(
            db,
            Decimal(str(amount)),
            from_currency.upper(),
            to_currency.upper(),
        )

        return ResponseModel(
            status="success",
            message="Currency converted",
            data={
                "from_currency": from_currency.upper(),
                "to_currency": to_currency.upper(),
                "from_amount": str(amount),
                "to_amount": str(converted_amount),
                "exchange_rate": str(rate),
            },
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/currencies", response_model=ResponseModel[List[str]])
async def get_supported_currencies(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    fx_service = FxRateService()

    currencies = await fx_service.get_all_supported_currencies(db)

    return ResponseModel(
        status="success",
        message=f"Retrieved {len(currencies)} currencies",
        data=currencies,
    )


@router.post("/update")
async def update_exchange_rates(
    base: str = "USD",
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    fx_service = FxRateService()

    try:
        count = await fx_service.update_rates_from_api(db, base.upper())

        return ResponseModel(
            status="success",
            message=f"Updated {count} exchange rates for base currency {base.upper()}",
            data={"count": count, "base_currency": base.upper()},
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
