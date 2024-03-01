from django.conf import settings
from payments.models import PaymentOrder, PurchaseCompositeItems, Output
from core.models import GenericSettings
from gateways.lava_api import LavaApi
from gateways.moogold_api import MoogoldApi
from gateways.freekassa_api import FreeKassaApi
from utils.functions import payment_order_id_generator, get_client_ip
from rest_framework import status
from rest_framework.exceptions import APIException
from datetime import datetime
import time


class PaymentManager:
    def __init__(self):
        self.lava = LavaApi()
        self.moogold = MoogoldApi()
        self.freekassa = FreeKassaApi()

    def _create_freekassa_payment_order(self, request, vals: dict) -> PaymentOrder:
        """
        vals:
        {
            "shopId": shopid (str)
            "nonce": time (int)
            "paymentId": pay_id (str)
            "i": pay_method (int)
            "email": email (str)
            "ip": ip (str)
            "amount": sum (float)
            "currency": currency (str) default="RUB"
            "tel": phone (str)
            "success_url": url (str)
            "failure_url": url (str)
            "notification_url": url (str)
        }
        """

        generic = GenericSettings.objects.first()
        order_id = payment_order_id_generator()
        client_ip = get_client_ip(request=request)
        data = {
            "shopId": settings.FREEKASSA_SHOP_ID,
            "nonce": int(time.time()),
            "paymentId": order_id,
            "i": int(vals["include_service"]),
            "email": vals["email"],
            "ip": client_ip,
            "amount": round(float(vals["sum"]) + 0.1, 2),
            "currency": "RUB",
            "success_url": generic.free_kassa_success_url + str(order_id),
            "failure_url": generic.free_kassa_failure_url,
            "notification_url": f"https://{generic.notify_domain}/{settings.FREEKASSA_NOTIFY_PREFIX}/freekassa/notification",
        }

        result = self.freekassa._create_order(data)
        status_code = result.get("status_code", False)

        if status_code != status.HTTP_200_OK:
            raise APIException(detail="Внутренняя ошибка сервера! Попробуйте позже...")

        payment_order = PaymentOrder.objects.create(
            order_id=order_id,
            email=vals["email"] if vals["email"] else "",
            type_payments=vals["type_payments"],
            user=request.user,
            location=result["location"],
            include_service=vals["include_service"],
            active=False,
            sum=vals["sum"],
        )

        return payment_order

    def _create_lava_payment_order(self, vals: dict) -> PaymentOrder:
        order_id = payment_order_id_generator()

        data = {
            "comment": f"ID: {order_id}",
            "customFields": "",
            "expire": 15,  # минут
            "failUrl": settings.BASE_URL,
            "hookUrl ": "https://lava.ru",
            "includeService": (
                [vals.get("include_service", False)]
                if vals.get("include_service", False)
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
            location=res["url"],
            lava_expired=datetime.strptime(res["expired"], "%Y-%m-%d %H:%M:%S"),
            project_lava=res["shop_id"],
            project_lava_name=res["merchantName"],
            status_lava_num=res["status"],
            include_service=", ".join(res["include_service"]),
            active=True,
            sum=vals["sum"],
        )

        return payment_order

    def _create_moogold_output(
        self, output, product_id, quantity, server, uid, user_item, composite_item
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
            composite_item=composite_item,
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

    def _get_moogold_balance(self):
        balance = round(float(self.moogold.get_moogold_balance()["balance"]), 2)
        return balance
