from payments.models import PaymentOrder
from gateways.lava_api import LavaApi
from gateways.moogold_api import MoogoldApi
from utils.functions import payment_order_id_generator


class PaymentManager:
    def __init__(self):
        self.lava = LavaApi()
        self.moogold = MoogoldApi()

    def _create_lava_payment_order(self, vals: dict) -> PaymentOrder:
        order_id = payment_order_id_generator()
        payment_order = PaymentOrder.objects.create(
            order_id=order_id, type_payments=vals["type_payments"], email=vals["email"]
        )

        lava_order = {}

        return payment_order

    def _create_moogold_output(self, vals: dict):
        pass
