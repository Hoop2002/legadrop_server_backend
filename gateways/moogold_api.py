from django.conf import settings
import time
import hmac
import hashlib
import base64
import json
import requests


class MoogoldApi:
    def __init__(self):
        self.SECRETKEY = settings.GATEWAYS_SETTINGS["MOOGOLD_SECRET_KEY"]
        self.PARTNER_ID = settings.GATEWAYS_SETTINGS["MOOGOLD_PARTNER_ID"]
        self.CATEGORY = settings.GATEWAYS_SETTINGS["GENSHIN_CATEGORY"]

    def buy_moogold_item(self, product_id, quantity, server, uid):
        order = {
            "path": "order/create_order",
            "data": {
                "category": self.CATEGORY,
                "product-id": product_id,
                "quantity": quantity,
                "User ID": uid,
                "Server": server,
            },
        }
        order_json = json.dumps(order)

        timestamp = str(int(time.time()))

        path = "order/create_order"
        string_to_sign = order_json + timestamp + path

        auth = hmac.new(
            bytes(self.SECRET_KEY, "utf-8"),
            msg=string_to_sign.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()

        auth_basic = base64.b64encode(
            f"{self.PARTNER_ID}:{self.SECRET_KEY}".encode()
        ).decode()

        headers = {
            "timestamp": timestamp,
            "auth": auth,
            "Authorization": "Basic " + auth_basic,
            "Content-Type": "application/json",
        }

        response = requests.post(
            url="https://moogold.com/wp-json/v1/api/order/create_order",
            data=order_json,
            headers=headers,
        )

        return json.loads(response.content.decode("utf-8"))

    def get_moogold_order_detail(self, order_id):
        order = {"path": "order/order_detail", "order_id": order_id}
        order_json = json.dumps(order)

        timestamp = str(int(time.time()))

        path = "order/order_detail"
        string_to_sign = order_json + timestamp + path

        auth = hmac.new(
            bytes(self.SECRET_KEY, "utf-8"),
            msg=string_to_sign.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()

        auth_basic = base64.b64encode(
            f"{self.PARTNER_ID}:{self.SECRET_KEY}".encode()
        ).decode()

        headers = {
            "timestamp": timestamp,
            "auth": auth,
            "Authorization": "Basic " + auth_basic,
            "Content-Type": "application/json",
        }

        response = requests.post(
            url="https://moogold.com/wp-json/v1/api/order/order_detail",
            data=order_json,
            headers=headers,
        )

        return json.loads(response.content.decode("utf-8"))

    def get_moogold_balance(self):
        order = {"path": "user/balance"}
        order_json = json.dumps(order)

        timestamp = str(int(time.time()))

        path = "user/balance"
        string_to_sign = order_json + timestamp + path

        auth = hmac.new(
            bytes(self.SECRET_KEY, "utf-8"),
            msg=string_to_sign.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()

        auth_basic = base64.b64encode(
            f"{self.PARTNER_ID}:{self.SECRET_KEY}".encode()
        ).decode()

        headers = {
            "timestamp": timestamp,
            "auth": auth,
            "Authorization": "Basic " + auth_basic,
            "Content-Type": "application/json",
        }

        response = requests.post(
            url="https://moogold.com/wp-json/v1/api/user/balance",
            data=order_json,
            headers=headers,
        )

        return json.loads(response.content.decode("utf-8"))

    def get_moogold_genshin_items(self):
        path = "product/product_detail"
        order = {"path": path, "product_id": self.CATEGORY}
        order_json = json.dumps(order)
        timestamp = str(int(time.time()))

        string_to_sign = order_json + timestamp + path

        auth = hmac.new(
            bytes(self.SECRETKEY, "utf-8"),
            msg=string_to_sign.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()

        auth_basic = base64.b64encode(
            f"{self.PARTNER_ID}:{self.SECRET_KEY}".encode()
        ).decode()

        headers = {
            "timestamp": timestamp,
            "auth": auth,
            "Authorization": "Basic " + auth_basic,
            "Content-Type": "application/json",
        }

        response = requests.post(
            url="https://moogold.com/wp-json/v1/api/product/product_detail",
            data=order_json,
            headers=headers,
        )

        return json.loads(response.content.decode("utf-8"))
