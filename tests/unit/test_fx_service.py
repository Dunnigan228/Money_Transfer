import pytest
from decimal import Decimal
from app.services.fx_rate_service import FxRateService
from app.db.models.fx_rate import FxRate
from datetime import datetime


@pytest.mark.asyncio
async def test_convert_same_currency(db_session):
    fx_service = FxRateService()

    amount = Decimal("100.00")
    converted, rate = await fx_service.convert_amount(
        db_session, amount, "USD", "USD"
    )

    assert converted == amount
    assert rate == Decimal("1.0")


@pytest.mark.asyncio
async def test_convert_with_rate(db_session):
    fx_rate = FxRate(
        base_currency="USD",
        quote_currency="EUR",
        rate=Decimal("0.92"),
        rate_date=datetime.utcnow(),
        source="test",
    )
    db_session.add(fx_rate)
    await db_session.commit()

    fx_service = FxRateService()

    amount = Decimal("100.00")
    converted, rate = await fx_service.convert_amount(
        db_session, amount, "USD", "EUR"
    )

    assert converted == Decimal("92.00")
    assert rate == Decimal("0.92")


@pytest.mark.asyncio
async def test_convert_without_rate(db_session):
    fx_service = FxRateService()

    with pytest.raises(ValueError, match="Exchange rate not available"):
        await fx_service.convert_amount(
            db_session, Decimal("100.00"), "USD", "XYZ"
        )
