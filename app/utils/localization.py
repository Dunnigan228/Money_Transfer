from typing import Optional
from babel import Locale
from babel.dates import format_datetime
from babel.numbers import format_currency, format_decimal
from app.core.config import settings


class Localization:

    def __init__(self):
        self.default_locale = settings.default_language
        self.supported_languages = settings.supported_languages_list

        self.translations = {
            "en": {
                "transfer_completed": "Transfer completed successfully",
                "transfer_failed": "Transfer failed",
                "insufficient_funds": "Insufficient funds",
                "account_not_found": "Account not found",
                "invalid_currency": "Invalid currency",
                "user_registered": "User registered successfully",
                "user_not_found": "User not found",
                "invalid_credentials": "Invalid credentials",
            },
            "ru": {
                "transfer_completed": "Перевод выполнен успешно",
                "transfer_failed": "Перевод не выполнен",
                "insufficient_funds": "Недостаточно средств",
                "account_not_found": "Счет не найден",
                "invalid_currency": "Недопустимая валюта",
                "user_registered": "Пользователь зарегистрирован",
                "user_not_found": "Пользователь не найден",
                "invalid_credentials": "Неверные учетные данные",
            },
            "kk": {
                "transfer_completed": "Аударым сәтті орындалды",
                "transfer_failed": "Аударым орындалмады",
                "insufficient_funds": "Қаражат жеткіліксіз",
                "account_not_found": "Шот табылмады",
                "invalid_currency": "Валюта жарамсыз",
                "user_registered": "Пайдаланушы тіркелді",
                "user_not_found": "Пайдаланушы табылмады",
                "invalid_credentials": "Қате тіркелгі деректері",
            },
        }

    def get_locale(self, language: Optional[str] = None) -> Locale:
        lang = language or self.default_locale
        if lang not in self.supported_languages:
            lang = self.default_locale
        return Locale(lang)

    def translate(self, key: str, language: Optional[str] = None) -> str:
        lang = language or self.default_locale
        if lang not in self.supported_languages:
            lang = self.default_locale

        return self.translations.get(lang, {}).get(
            key, self.translations["en"].get(key, key)
        )

    def format_money(
        self,
        amount: float,
        currency: str,
        language: Optional[str] = None,
    ) -> str:
        locale = self.get_locale(language)
        return format_currency(amount, currency, locale=locale)

    def format_number(
        self,
        number: float,
        language: Optional[str] = None,
    ) -> str:
        locale = self.get_locale(language)
        return format_decimal(number, locale=locale)


localization = Localization()
