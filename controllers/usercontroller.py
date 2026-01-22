# controllers/usercontroller.py

"""
Контроллер для работы с пользователями в памяти.
"""

from typing import List, Optional
from models.user import User


class UserController:
    """
    Контроллер пользователей. Хранение данных в памяти.
    """

    def __init__(self):
        """Инициализация контроллера с пустым списком пользователей."""
        self.users: List[User] = []
        self.next_id: int = 1

    def add_user(self, name: str) -> User:
        """
        Добавить нового пользователя.

        Args:
            name (str): Имя пользователя.

        Returns:
            User: Объект созданного пользователя.
        """
        user = User(name)
        user.id = self.next_id
        self.next_id += 1
        self.users.append(user)
        return user

    def list_users(self) -> List[User]:
        """
        Получить список всех пользователей.

        Returns:
            List[User]: Список пользователей.
        """
        return self.users

    def get_user(self, user_id: int) -> Optional[User]:
        """
        Получить пользователя по ID.

        Args:
            user_id (int): ID пользователя.

        Returns:
            Optional[User]: Пользователь или None, если не найден.
        """
        for u in self.users:
            if u.id == user_id:
                return u
        return None
