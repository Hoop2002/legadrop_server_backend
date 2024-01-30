import requests
import hmac
import json
import hashlib


class LavaApi:
    def __init__(self):
        from django.conf import settings

        self.URL = "https://api.lava.ru"
        self.SECRETKEY = settings.GATEWAYS_SETTINGS["LAVA_SECRET_KEY"]
        self.SHOP_ID = settings.GATEWAYS_SETTINGS["LAVA_SHOP_ID"]

    def _create_order(self, data: dict, router: str = "/business/invoice/create"):
        data = self.SyncSortDict(data)
        json_str = json.dumps(data).encode()

        auth = hmac.new(
            bytes(self.SECRETKEY, "UTF-8"),
            json_str,
            hashlib.sha256,
        ).hexdigest()

        response = requests.post(
            self.URL + router,
            json=data,
            headers={
                "Signature": auth,
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )

        return json.loads(response.content.decode("utf-8"))

    def _get_order_status(
        self,
        invoice_id,
        order_id,
        router="/business/invoice/status",
    ):
        data = self.SyncSortDict(
            {"shopId": self.SHOP_ID, "orderId": order_id, "invoiceId": invoice_id},
        )
        json_str = json.dumps(data).encode()

        auth = hmac.new(
            bytes(self.SECRETKEY, "UTF-8"),
            json_str,
            hashlib.sha256,
        ).hexdigest()

        response = requests.post(
            self.URL + router,
            json=data,
            headers={
                "Signature": auth,
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )

        return json.loads(response.content.decode("utf-8"))

    def SyncSortDict(self, data: dict):
        sorted_tuple = sorted(data.items(), key=lambda x: x[0])
        return dict(sorted_tuple)
