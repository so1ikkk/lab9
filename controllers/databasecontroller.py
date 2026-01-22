# controllers/databasecontroller.py

"""
Модуль работы с базой данных в памяти (SQLite) для валют и пользователей.

Содержит CRUD для валют, пользователей и привязки валют к пользователям.
"""

import sqlite3
from typing import List, Dict, Optional


class CurrencyRatesCRUD:
    """
    Класс для работы с валютами и пользователями в SQLite.
    """

    def __init__(self, currency_rates_obj: Optional[List[Dict]] = None):
        """
        Инициализация базы данных в памяти и создание таблиц.

        Args:
            currency_rates_obj (Optional[List[Dict]]): Список валют для первичного наполнения базы.
        """
        self.__currency_rates_obj = currency_rates_obj or []
        self.__con = sqlite3.connect(":memory:")
        self.__cursor = self.__con.cursor()
        self.__create_tables()

        if self.__currency_rates_obj:
            self._create()

    def __create_tables(self) -> None:
        """Создание таблиц currency, user и user_currency."""
        self.__cursor.execute("""
            CREATE TABLE IF NOT EXISTS currency (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                num_code TEXT NOT NULL,
                char_code TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                value FLOAT,
                nominal INTEGER
            )
        """)
        self.__cursor.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        """)
        self.__cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_currency (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                currency_id INTEGER NOT NULL,
                FOREIGN KEY(user_id) REFERENCES user(id),
                FOREIGN KEY(currency_id) REFERENCES currency(id)
            )
        """)
        self.__con.commit()

    # ===== Валюты =====
    def _create(self, data: Optional[List[Dict]] = None) -> None:
        """
        Добавить валюты в базу.

        Args:
            data (Optional[List[Dict]]): Список словарей валют.
        """
        if data is None:
            data = self.__currency_rates_obj
        if not data:
            return
        sql = """
            INSERT INTO currency(num_code, char_code, name, value, nominal)
            VALUES(:num_code, :char_code, :name, :value, :nominal)
        """
        self.__cursor.executemany(sql, data)
        self.__con.commit()

    def _read(self, char_code: Optional[str] = None) -> List[Dict]:
        """
        Получить валюты из базы.

        Args:
            char_code (Optional[str]): Символьный код валюты.

        Returns:
            List[Dict]: Список валют или одна валюта по коду.
        """
        if char_code:
            self.__cursor.execute("SELECT * FROM currency WHERE char_code = ?", (char_code.upper(),))
        else:
            self.__cursor.execute("SELECT * FROM currency")
        rows = self.__cursor.fetchall()
        return [
            {
                "id": r[0], "num_code": r[1], "char_code": r[2],
                "name": r[3], "value": float(r[4]), "nominal": r[5]
            }
            for r in rows
        ]

    def _update(self, currency: Dict[str, float]) -> None:
        """
        Обновить курс валюты.

        Args:
            currency (Dict[str, float]): Словарь {char_code: value}.
        """
        code, val = list(currency.items())[0]
        self.__cursor.execute(
            "UPDATE currency SET value = ? WHERE char_code = ?",
            (float(val), code.upper())
        )
        self.__con.commit()

    def _delete(self, currency_id: int) -> None:
        """
        Удалить валюту по ID.

        Args:
            currency_id (int): ID валюты.
        """
        self.__cursor.execute("DELETE FROM currency WHERE id = ?", (currency_id,))
        self.__con.commit()

    # ===== Пользователи =====
    def create_user(self, name: str) -> int:
        """
        Добавить пользователя.

        Args:
            name (str): Имя пользователя.

        Returns:
            int: ID нового пользователя.
        """
        self.__cursor.execute("INSERT INTO user(name) VALUES(?)", (name,))
        self.__con.commit()
        return self.__cursor.lastrowid

    def read_users(self) -> List[Dict]:
        """
        Получить всех пользователей.

        Returns:
            List[Dict]: Список пользователей.
        """
        self.__cursor.execute("SELECT * FROM user")
        rows = self.__cursor.fetchall()
        return [{"id": r[0], "name": r[1]} for r in rows]

    def get_user(self, user_id: int) -> Optional[Dict]:
        """
        Получить пользователя по ID.

        Args:
            user_id (int): ID пользователя.

        Returns:
            Optional[Dict]: Данные пользователя или None.
        """
        self.__cursor.execute("SELECT * FROM user WHERE id=?", (user_id,))
        r = self.__cursor.fetchone()
        return {"id": r[0], "name": r[1]} if r else None

    # ===== Пользовательские валюты =====
    def assign_currency_to_user(self, user_id: int, currency_id: int) -> None:
        """
        Назначить валюту пользователю.

        Args:
            user_id (int): ID пользователя.
            currency_id (int): ID валюты.
        """
        self.__cursor.execute(
            "INSERT INTO user_currency(user_id, currency_id) VALUES(?,?)",
            (user_id, currency_id)
        )
        self.__con.commit()

    def get_user_currencies(self, user_id: int) -> List[Dict]:
        """
        Получить все валюты, привязанные к пользователю.

        Args:
            user_id (int): ID пользователя.

        Returns:
            List[Dict]: Список валют.
        """
        self.__cursor.execute("""
            SELECT c.id, c.num_code, c.char_code, c.name, c.value, c.nominal
            FROM currency c
            JOIN user_currency uc ON c.id = uc.currency_id
            WHERE uc.user_id=?
        """, (user_id,))
        rows = self.__cursor.fetchall()
        return [
            {"id": r[0], "num_code": r[1], "char_code": r[2],
             "name": r[3], "value": float(r[4]), "nominal": r[5]}
            for r in rows
        ]

    def __del__(self):
        """Закрытие соединения при удалении объекта."""
        try:
            if hasattr(self, "_CurrencyRatesCRUD__cursor"):
                self.__cursor = None
            if hasattr(self, "_CurrencyRatesCRUD__con") and self.__con:
                self.__con.close()
        except Exception:
            pass
