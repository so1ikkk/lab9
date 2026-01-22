# myapp.py
"""
Главный модуль веб-приложения CurrenciesListApp.

Содержит:
- инициализацию базы данных и контроллеров
- получение курсов валют с API ЦБ
- маршрутизацию HTTP-запросов
- рендеринг страниц с помощью Jinja2

Архитектура:
- MVC: модели в models/, контроллеры в controllers/, шаблоны в templates/
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
from typing import Dict, List

from controllers.databasecontroller import CurrencyRatesCRUD
from controllers.currencycontroller import CurrencyController
from controllers.cbr_api import get_currencies
from controllers.usercontroller import UserController
from models import Author

# ===== Инициализация пользователей =====
user_controller = UserController()
user_controller.add_user("Ярослав")
user_controller.add_user("Виктория")
user_controller.add_user("Антон")

# ===== Инициализация Jinja2 Environment =====
template_path = os.path.join(os.path.dirname(__file__), "templates")
env = Environment(loader=FileSystemLoader(template_path), autoescape=select_autoescape())

# ===== Автор проекта =====
main_author = Author("Иголкин Владислав 504623", "P3124")

# ===== Инициализация базы данных и контроллеров =====
db_controller = CurrencyRatesCRUD()
currency_controller = CurrencyController(db_controller)

# ===== Список валют =====
currency_codes: List[str] = ["USD", "EUR", "GBP", "AUD"]

# ===== Подтягиваем курсы ЦБ =====
try:
    rates: Dict[str, float] = get_currencies(currency_codes)
    for code, value in rates.items():
        existing = db_controller._read(code)
        if not existing:
            db_controller._create([{
                "num_code": "840" if code == "USD" else
                            "978" if code == "EUR" else
                            "826" if code == "GBP" else
                            "036",
                "char_code": code,
                "name": code,  # Можно заменить на полное название валюты
                "value": value,
                "nominal": 1
            }])
        else:
            db_controller._update({code: value})
except Exception as e:
    print("Не удалось получить курсы ЦБ:", e)

# ===== Шаблоны =====
template_index = env.get_template("index.html")
template_currencies = env.get_template("currencies.html")
template_author = env.get_template("author.html")
template_users = env.get_template("users.html")
template_user = env.get_template("user.html")


# ===== HTTP Handler =====
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    """Обработчик HTTP-запросов для веб-приложения CurrenciesListApp."""

    def do_GET(self) -> None:
        """Обрабатывает GET-запросы и рендерит соответствующие страницы."""
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        url_query = parse_qs(self.path.partition("?")[-1])

        navigation = [
            {"caption": "Главная", "href": "/"},
            {"caption": "Об авторе", "href": "/author"},
            {"caption": "Пользователи", "href": "/users"}
        ]

        # ===== Главная страница =====
        if self.path == "/":
            result = template_index.render(
                myapp="CurrenciesListApp",
                navigation=navigation,
                author_name=main_author.name,
                author_group=main_author.group,
                currencies=currency_controller.list_currencies()
            )

        # ===== Страница автора =====
        elif self.path.startswith("/author"):
            result = template_author.render(
                author_name=main_author.name,
                author_group=main_author.group,
                navigation=navigation
            )

        # ===== Список всех валют =====
        elif self.path.startswith("/currencies"):
            result = template_currencies.render(
                currencies=currency_controller.list_currencies(),
                navigation=navigation
            )

        # ===== Удаление валюты =====
        elif "currency/delete" in self.path and "id" in url_query:
            currency_controller.delete_currency(int(url_query["id"][0]))
            result = template_currencies.render(
                currencies=currency_controller.list_currencies(),
                navigation=navigation
            )

        # ===== Обновление курса валют =====
        elif "currency/update" in self.path:
            for code, val in url_query.items():
                currency_controller.update_currency(code.upper(), float(val[0]))
            result = template_currencies.render(
                currencies=currency_controller.list_currencies(),
                navigation=navigation
            )

        # ===== Вывод валют в консоль (отладка) =====
        elif "currency/show" in self.path:
            print(currency_controller.list_currencies())
            result = "<h1>Смотрите консоль</h1>"

        # ===== Список пользователей =====
        elif self.path.startswith("/users"):
            result = template_users.render(
                users=user_controller.list_users(),
                navigation=navigation
            )

        # ===== Просмотр одного пользователя =====
        elif self.path.startswith("/user") and "id" in url_query:
            user_id: int = int(url_query["id"][0])
            user = user_controller.get_user(user_id)
            result = template_user.render(user=user, navigation=navigation)

        # ===== Страница не найдена =====
        else:
            result = "<h1>Страница не найдена</h1>"

        self.wfile.write(result.encode("utf-8"))


# ===== Запуск сервера =====
def run_server(host: str = "localhost", port: int = 8080) -> None:
    """Запускает HTTP сервер на указанном хосте и порту."""
    httpd = HTTPServer((host, port), SimpleHTTPRequestHandler)
    print(f"Server is running at http://{host}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()
