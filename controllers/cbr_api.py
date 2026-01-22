import requests

def get_currencies(currency_codes: list, url: str = "https://www.cbr-xml-daily.ru/daily_json.js") -> dict:
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        raise ConnectionError("API недоступен") from e

    try:
        data = response.json()
    except ValueError as e:
        raise ValueError("Некорректный JSON") from e

    if "Valute" not in data:
        raise KeyError("Нет ключа 'Valute'")

    result = {}
    for code in currency_codes:
        if code not in data["Valute"]:
            raise KeyError(f"Валюта {code} отсутствует в данных")
        value = data["Valute"][code].get("Value")
        if not isinstance(value, (int, float)):
            raise TypeError(f"Курс валюты {code} имеет неверный тип")
        result[code] = float(value)
    return result
