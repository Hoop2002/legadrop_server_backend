from django.conf import settings
from payments.models import PaymentOrder
from gateways.lava_api import LavaApi
from gateways.moogold_api import MoogoldApi
from utils.functions import payment_order_id_generator
from rest_framework import status
from rest_framework.exceptions import APIException
from datetime import datetime


class PaymentManager:
    def __init__(self):
        self.lava = LavaApi()
        self.moogold = MoogoldApi()

    def _create_lava_payment_order(self, vals: dict) -> PaymentOrder:
        order_id = payment_order_id_generator()

        data = {
            "comment": f"ID: {order_id}",
            "customFields": "",
            "expire": 15,  # минут
            "failUrl": settings.BASE_URL,
            "hookUrl ": "https://lava.ru",
            "includeService": (
                [vals.get("include_service_lava", False)]
                if vals.get("include_service_lava", False)
                else ["card", "sbp", "qiwi"]
            ),
            "orderId": order_id,
            "shopId": settings.GATEWAYS_SETTINGS["LAVA_SHOP_ID"],
            "successUrl": settings.BASE_URL + settings.BACK_URL_LAVA + str(order_id),
            "sum": round(float(vals["sum"]), 2),
        }

        result = self.lava._create_order(data=data)
        status_lava = result.get("status", False)
        if status_lava != status.HTTP_200_OK:
            raise APIException(detail="Внутренняя ошибка сервера! Попробуйте позже...")

        res = result.get("data")

        payment_order = PaymentOrder.objects.create(
            order_id=order_id,
            email=vals["email"] if vals["email"] else "",
            type_payments=vals["type_payments"],
            user=vals["user"],
            lava_id=res["id"],
            lava_link=res["url"],
            lava_expired=datetime.strptime(res["expired"], "%Y-%m-%d %H:%M:%S"),
            project_lava=res["shop_id"],
            project_lava_name=res["merchantName"],
            status_lava_num=res["status"],
            include_service_lava=", ".join(res["include_service"]),
            active=True,
        )

        return payment_order

    def _create_moogold_output(self, vals: dict):
        pass
