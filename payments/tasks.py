from celery import shared_task
from django.utils import timezone
from payments.models import PaymentOrder, Calc, PromoCode, CompositeItems
from users.models import ActivatedPromo
from gateways.lava_api import LavaApi
from gateways.moogold_api import MoogoldApi


@shared_task
def deactivate_expired_promo():
    now = timezone.localtime()
    PromoCode.objects.filter(to_date__lte=now, to_date__isnull=False).update(
        active=False
    )


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

                    credit = float(order.sum) * float(activate_promo.promo.percent)
                    debit = (credit - float(order.sum)) * -1
                    balance = credit

                    calc = Calc.objects.create(
                        user=user,
                        credit=credit,
                        debit=debit,
                        balance=balance,
                        comment=comment,
                        demo=user.profile.demo,
                        order=order,
                    )
                    activate_promo.calc_promo.add(calc)
                    activate_promo.save()

                    order.active = False
                    order.status = order.SUCCESS
                    order.save()
                else:
                    comment = f"Пополнение пользоватeлем {user.username} на сумму {round(order.sum, 2)} \nService: LAVA"

                    credit = float(order.sum)
                    debit = 0
                    balance = credit

                    calc = Calc.objects.create(
                        user=user,
                        credit=credit,
                        debit=debit,
                        balance=balance,
                        comment=comment,
                        demo=user.profile.demo,
                        order=order,
                    )

                    order.active = False
                    order.status = order.SUCCESS
                    order.save()


@shared_task
def updating_moogold_composite_items(moogold=MoogoldApi()):
    data = moogold.get_moogold_genshin_items()

    for com_item in data["Variation"]:
        item = CompositeItems.objects.filter(ext_id=com_item["variation_id"]).first()
        if not item:
            composite_item = CompositeItems.objects.create(
                ext_id=com_item["variation_id"],
                technical_name=com_item["variation_name"],
                price_dollar=com_item["variation_price"],
                service=CompositeItems.MOOGOLD,
            )
        else:
            composite_item = item
            composite_item.ext_id = com_item["variation_id"]
            composite_item.technical_name = com_item["variation_name"]
            composite_item.price_dollar = com_item["variation_price"]
            composite_item.service = CompositeItems.MOOGOLD

        composite_item.save()
