import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import unittest
from unittest.mock import MagicMock
from .controllers.currencycontroller import CurrencyController
from .controllers.usercontroller import UserController



class TestCurrencyController(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.controller = CurrencyController(self.mock_db)

    def test_list_currencies(self):
        self.mock_db._read.return_value = [{"id": 1, "char_code": "USD", "value": 90}]
        result = self.controller.list_currencies()
        self.assertEqual(result[0]['char_code'], "USD")
        self.mock_db._read.assert_called_once()

    def test_update_currency(self):
        self.controller.update_currency("USD", 100.5)
        self.mock_db._update.assert_called_once_with({"USD": 100.5})

    def test_delete_currency(self):
        self.controller.delete_currency(1)
        self.mock_db._delete.assert_called_once_with(1)


class TestUserController(unittest.TestCase):
    def setUp(self):
        self.controller = UserController()
        self.controller.add_user("Антон")
        self.controller.add_user("Мария")

    def test_list_users(self):
        users = self.controller.list_users()
        self.assertEqual(len(users), 2)
        self.assertEqual(users[0].name, "Антон")
        self.assertEqual(users[1].name, "Мария")

    def test_get_user(self):
        user = self.controller.get_user(1)
        self.assertEqual(user.name, "Антон")
        self.assertIsNone(self.controller.get_user(99))

    def test_add_user(self):
        self.controller.add_user("Игорь")
        users = self.controller.list_users()
        self.assertEqual(len(users), 3)
        self.assertEqual(users[2].name, "Игорь")


if __name__ == "__main__":
    unittest.main()

