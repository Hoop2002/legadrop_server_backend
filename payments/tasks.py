from payments.models import PaymentOrder, Calc, PromoCode
from users.models import ActivatedPromo
from gateways.lava_api import LavaApi
from celery import shared_task


@shared_task
def verify_payment_order(lava=LavaApi()):
    payments_orders = PaymentOrder.objects.filter(active=True).all()
    for order in payments_orders:
        user = order.user

        if order.type_payments == order.LAVA:
            data = lava._get_order_status(
                invoice_id=order.lava_id, order_id=order.order_id
            )
            lava_order = data.get("data", False)

            if not lava_order:
                break

            lava_order_status = lava_order.get("status", False)

            if not lava_order_status:
                break

            if lava_order_status == order.CREATE:
                break
            if lava_order_status == order.EXPIRED:
                order.status = order.EXPIRED
                order.active = False
                order.save()
            if lava_order_status == order.SUCCESS:
                activate_promo = ActivatedPromo.objects.filter(
                    user=user, promo__type=PromoCode.BONUS, bonus_using=False
                ).first()

                if activate_promo:
                    comment = f'Пополнение с использованием промокода {activate_promo.promo.name} \
                        "{activate_promo.promo.code_data}" пользоватeлем {user.username} на сумму {round(order.sum, 2)} \nService: LAVA'

                    credit = order.sum * activate_promo.promo.percent
                    debit = (credit - order.sum) * -1
                    balance = credit

                    calc = Calc.objects.create(
                        user=user,
                        credit=credit,
                        debit=debit,
                        balance=balance,
                        comment=comment,
                        order=order,
                    )
                    activate_promo.promo.add(calc)
                    activate_promo.save()

                    order.active = False
                    order.status = order.SUCCESS
                    order.save()
                else:
                    comment = f"Пополнение пользоватeлем {user.username} на сумму {round(order.sum, 2)} \nService: LAVA"

                    credit = order.sum
                    debit = 0
                    balance = credit

                    calc = Calc.objects.create(
                        user=user,
                        credit=credit,
                        debit=debit,
                        balance=balance,
                        comment=comment,
                        order=order,
                    )

                    order.active = False
                    order.status = order.SUCCESS
                    order.save()
