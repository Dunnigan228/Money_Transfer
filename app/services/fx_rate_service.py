from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict
import httpx
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db.models.fx_rate import FxRate
from app.utils.redis_client import redis_client


class FxRateService:

    def __init__(self):
        self.api_url = settings.frankfurter_api_url
        self.cache_ttl = settings.redis_cache_ttl

    async def fetch_latest_rates(
        self,
        base_currency: str = "USD",
    ) -> Dict[str, Decimal]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.api_url}/v1/latest",
                    params={"base": base_currency},
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()

                rates = {base_currency: Decimal("1.0")}
                for currency, rate in data.get("rates", {}).items():
                    rates[currency] = Decimal(str(rate))

                return rates
            except httpx.HTTPError as e:
                raise Exception(f"Failed to fetch exchange rates: {str(e)}")

    async def get_exchange_rate(
        self,
        db: AsyncSession,
        base_currency: str,
        quote_currency: str,
    ) -> Optional[Decimal]:
        if base_currency == quote_currency:
            return Decimal("1.0")

        cache_key = f"fx_rate:{base_currency}:{quote_currency}"
        cached_rate = await redis_client.get(cache_key)
        if cached_rate:
            return Decimal(cached_rate)

        stmt = (
            select(FxRate)
            .where(
                and_(
                    FxRate.base_currency == base_currency,
                    FxRate.quote_currency == quote_currency,
                )
            )
            .order_by(FxRate.rate_date.desc())
            .limit(1)
        )

        result = await db.execute(stmt)
        fx_rate = result.scalar_one_or_none()

        if fx_rate:
            await redis_client.set(cache_key, str(fx_rate.rate), self.cache_ttl)
            return fx_rate.rate

        stmt = (
            select(FxRate)
            .where(
                and_(
                    FxRate.base_currency == quote_currency,
                    FxRate.quote_currency == base_currency,
                )
            )
            .order_by(FxRate.rate_date.desc())
            .limit(1)
        )

        result = await db.execute(stmt)
        fx_rate = result.scalar_one_or_none()

        if fx_rate and fx_rate.rate != 0:
            inverted_rate = Decimal("1.0") / fx_rate.rate
            await redis_client.set(cache_key, str(inverted_rate), self.cache_ttl)
            return inverted_rate

        return None

    async def update_rates_from_api(
        self,
        db: AsyncSession,
        base_currency: str = "USD",
    ) -> int:
        rates = await self.fetch_latest_rates(base_currency)
        rate_date = datetime.utcnow()
        count = 0

        for quote_currency, rate in rates.items():
            if quote_currency == base_currency:
                continue

            fx_rate = FxRate(
                base_currency=base_currency,
                quote_currency=quote_currency,
                rate=rate,
                rate_date=rate_date,
                source="frankfurter.app",
            )
            db.add(fx_rate)
            count += 1

        await db.commit()
        return count

    async def convert_amount(
        self,
        db: AsyncSession,
        amount: Decimal,
        from_currency: str,
        to_currency: str,
    ) -> tuple[Decimal, Decimal]:
        if from_currency == to_currency:
            return amount, Decimal("1.0")

        rate = await self.get_exchange_rate(db, from_currency, to_currency)

        if rate is None:
            raise ValueError(
                f"Exchange rate not available for {from_currency}/{to_currency}"
            )

        converted_amount = amount * rate
        converted_amount = converted_amount.quantize(Decimal("0.01"))

        return converted_amount, rate

    async def get_all_supported_currencies(self, db: AsyncSession) -> list[str]:
        cache_key = "fx_currencies:all"
        cached_currencies = await redis_client.get_json(cache_key)
        if cached_currencies:
            return cached_currencies

        stmt = select(FxRate.quote_currency).distinct()
        result = await db.execute(stmt)
        currencies = [row[0] for row in result.fetchall()]

        stmt = select(FxRate.base_currency).distinct()
        result = await db.execute(stmt)
        base_currencies = [row[0] for row in result.fetchall()]

        all_currencies = sorted(list(set(currencies + base_currencies)))
        await redis_client.set_json(cache_key, all_currencies, self.cache_ttl)
        return all_currencies
