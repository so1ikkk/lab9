"""
Модуль контроллера валют.

Контроллер управляет CRUD-операциями с валютами и может обновлять курсы
валют через API Центробанка России.
"""

from typing import List, Optional
from controllers.databasecontroller import CurrencyRatesCRUD
from controllers.cbr_api import get_currencies


class CurrencyController:
    """
    Контроллер для управления валютами.
    """

    def __init__(self, db_controller: CurrencyRatesCRUD):
        """
        Инициализация контроллера.

        Args:
            db_controller (CurrencyRatesCRUD): Объект для работы с БД валют.
        """
        self.db = db_controller

    def list_currencies(self) -> list:
        """
        Получить список всех валют.

        Returns:
            list: Список валют в виде словарей.
        """
        return self.db._read()

    def get_currency(self, char_code: str) -> Optional[dict]:
        """
        Получить одну валюту по символьному коду.

        Args:
            char_code (str): Символьный код валюты (например, 'USD').

        Returns:
            dict | None: Данные валюты или None, если не найдено.
        """
        result = self.db._read(char_code.upper())
        return result[0] if result else None

    def update_currency(self, char_code: str, value: float) -> None:
        """
        Обновить курс валюты.

        Args:
            char_code (str): Символьный код валюты.
            value (float): Новый курс.
        """
        self.db._update({char_code.upper(): value})

    def delete_currency(self, currency_id: int) -> None:
        """
        Удалить валюту по ID.

        Args:
            currency_id (int): ID валюты в базе.
        """
        self.db._delete(currency_id)

    def update_from_cbr(self, currency_codes: List[str]) -> None:
        """
        Обновить курсы валют через API Центробанка.

        Args:
            currency_codes (List[str]): Список символьных кодов валют.
        """
        rates = get_currencies(currency_codes)
        for code, value in rates.items():
            # Если валюты нет в БД, создаём её
            if not self.get_currency(code):
                self.db._create([{
                    "num_code": self._default_num_code(code),
                    "char_code": code,
                    "name": code,
                    "value": value,
                    "nominal": 1
                }])
            else:
                self.update_currency(code, value)

    @staticmethod
    def _default_num_code(char_code: str) -> str:
        """
        Возвращает числовой код валюты по символьному коду.

        Args:
            char_code (str): Символьный код валюты.

        Returns:
            str: Числовой код валюты.
        """
        mapping = {"USD": "840", "EUR": "978", "GBP": "826", "AUD": "036"}
        return mapping.get(char_code.upper(), "000")
