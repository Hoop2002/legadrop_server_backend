from django.conf import settings
from payments.models import PaymentOrder, PurchaseCompositeItems, Output
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
            # "shopId": settings.GATEWAYS_SETTINGS["LAVA_SHOP_ID"],
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
            sum=vals["sum"],
        )

        return payment_order

    def _create_moogold_output(
        self, output, product_id, quantity, server, uid, user_item
    ):

        moogold_order = self.moogold.buy_moogold_item(
            product_id=product_id, quantity=quantity, server=server, uid=uid
        )

        purchase = PurchaseCompositeItems.objects.create(
            type=PurchaseCompositeItems.MOOGOLD,
            status=PurchaseCompositeItems.PROCCESS,
            output=output,
            ext_id_order=moogold_order["order_id"],
            player_id=moogold_order["account_details"]["User ID"],
            server=moogold_order["account_details"]["Server"],
            user_item=user_item,
        )
        purchase.save()

    def _enough_money_moogold_balance(self, price: float):
        """
        price - цена в рублях
        метод возвращает True в случае если денег на балансе хватает
        False в случае если денег недостаточно
        """
        balance = round(float(self.moogold.get_moogold_balance()["balance"]), 2)
        if balance < price:
            return False
        else:
            return True

    def _get_status_order_in_moogold(self, order_id):
        return self.moogold.get_moogold_order_detail(order_id=order_id)["order_status"] 