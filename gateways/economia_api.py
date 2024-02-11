import requests
import json


def get_currency() -> dict:
    response = requests.get(url=f"https://economia.awesomeapi.com.br/last/USD-RUb")
    return json.loads(response.content.decode("utf-8"))
