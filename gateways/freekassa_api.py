from django.conf import settings
import json
import requests
import hashlib
import hmac


class FreeKassaApi:
    def __init__(self) -> None:
        self.APIKEY = settings.FREEKASSA_API_KEY
        self.SECRET_KEY_ONE = settings.FREEKASSA_SECRET_KEY_ONE
        self.SECRET_KEY_TWO = settings.FREEKASSA_SECRET_KEY_TWO
        self.SHOP_ID = settings.FREEKASSA_SHOP_ID
        self.URL = "https://api.freekassa.ru/v1"
        self.CREATE_ORDER_PATH = "/orders/create"

    def _create_order(self, data: dict):
        data.update({"shopId": self.SHOP_ID})
        json_req = self.sort_dict(data=data)

        message = "|".join([f"{value}" for key, value in json_req.items()])

        signature = hmac.new(
            settings.FREEKASSA_API_KEY.encode(), message.encode(), hashlib.sha256
        ).hexdigest()

        json_req.update({"signature": signature})

        response = requests.post(url=self.URL + self.CREATE_ORDER_PATH, json=json_req)
        content = json.loads(response.content.decode("utf-8"))
        content.update({"status_code": response.status_code})
        return content

    def sort_dict(self, data: dict):
        sorted_tuple = sorted(data.items(), key=lambda x: x[0])
        return dict(sorted_tuple)
