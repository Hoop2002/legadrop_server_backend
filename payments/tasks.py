from celery import shared_task
from django.utils import timezone
from django.db.models import Q
from payments.models import (
    PaymentOrder,
    Calc,
    PromoCode,
    CompositeItems,
    Output,
    PurchaseCompositeItems,
)
from users.models import ActivatedPromo, ActivatedLinks
from gateways.lava_api import LavaApi
from gateways.moogold_api import MoogoldApi
from payments.manager import PaymentManager

from utils.decorators import single_task


@shared_task
def deactivate_expired_promo():
    now = timezone.localtime()
    PromoCode.objects.filter(Q(to_date__lte=now) | Q(to_date__isnull=False)).update(
        active=False
    )


@shared_task
@single_task(None)
def withdrawal_price_output():
    outputs_orders = Output.objects.filter(
        removed=False,
        withdrawal_price=False,
        status=Output.PROCCESS,
        active=True,
    )
    for out in outputs_orders:
        out.withdrawal_price = out.cost_withdrawal_of_items_in_rub
        out.save()


@shared_task
@single_task(None)
def calc_remaining_activations():
    """Таска для пересчёта остатка активаций промокода.
    Рассчитана на пересчёт раз в 5-10 минут
    """
    now = timezone.localtime()
    codes = PromoCode.objects.filter(
        Q(active=True, limit_activations__isnull=False, removed=False)
        & (Q(to_date__gte=now) | Q(to_date__isnull=True))
    ).distinct()
    for code in codes:
        code.remaining_activations = code.get_remaining_activations
        code.save()


@shared_task
@single_task(None)
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
                continue

            lava_order_status = lava_order.get("status", False)

            if not lava_order_status:
                continue

            if lava_order_status == order.CREATE:
                continue
            if lava_order_status == order.EXPIRED:
                order.status = order.EXPIRED
                order.active = False
                order.save()
            if lava_order_status == order.SUCCESS:
                activate_promo = ActivatedPromo.objects.filter(
                    user=user, promo__type=PromoCode.BONUS, bonus_using=False
                ).first()
                activated_link = ActivatedLinks.objects.filter(
                    user=user, bonus_using=False
                ).first()

                if activate_promo or activated_link:
                    if activate_promo:
                        comment = f'Пополнение с использованием промокода {activate_promo.promo.name} \
                                   f"{activate_promo.promo.code_data}" пользоватeлем {user.username} на сумму {round(order.sum, 2)} \nService: LAVA\n'
                        balance = float(order.sum) * float(activate_promo.promo.percent)
                    else:
                        comment = f'Пополнение с использованием реферальной ссылки {activated_link.link.code_data} \
                                    "{activated_link.link.code_data}" пользоватeлем {user.username} на сумму {round(order.sum, 2)} \nService: LAVA\n'
                        balance = float(order.sum) * float(activated_link.link.bonus)

                    calc = Calc.objects.create(
                        user=user,
                        balance=balance,
                        comment=comment,
                        demo=user.profile.demo,
                        order=order,
                    )
                    if activate_promo:
                        activate_promo.calc_promo.add(calc)
                        activate_promo.save()
                    else:
                        activated_link.calc_link.add(calc)
                        activated_link.save()

                    order.active = False
                    order.status = order.SUCCESS
                    order.save()
                else:
                    comment = f"Пополнение пользоватeлем {user.username} на сумму {round(order.sum, 2)} \nService: LAVA"

                    balance = float(order.sum)

                    calc = Calc.objects.create(
                        user=user,
                        balance=balance,
                        comment=comment,
                        demo=user.profile.demo,
                        order=order,
                    )

                    order.active = False
                    order.status = order.SUCCESS
                    order.save()

        if order.type_payments == order.FREEKASSA:
            activate_promo = ActivatedPromo.objects.filter(
                user=user, promo__type=PromoCode.BONUS, bonus_using=False
            ).first()
            activated_link = ActivatedLinks.objects.filter(
                user=user, bonus_using=False
            ).first()

            if activate_promo or activated_link:
                if activate_promo:
                    comment = f'Пополнение с использованием промокода {activate_promo.promo.name} \
                                   f"{activate_promo.promo.code_data}" пользоватeлем {user.username} на сумму {round(order.sum, 2)} \nService: FREEKASSA'
                    balance = float(order.sum) * float(activate_promo.promo.percent)
                else:
                    comment = f'Пополнение с использованием реферальной ссылки {activated_link.link.code_data} \
                                    "{activated_link.link.code_data}" пользоватeлем {user.username} на сумму {round(order.sum, 2)} \nService: FREEKASSA'
                    balance = float(order.sum) * float(activated_link.link.bonus)

                calc = Calc.objects.create(
                    user=user,
                    balance=balance,
                    comment=comment,
                    demo=user.profile.demo,
                    order=order,
                )

                if activate_promo:
                    activate_promo.calc_promo.add(calc)
                    activate_promo.save()
                else:
                    activated_link.calc_link.add(calc)
                    activated_link.save()

                order.active = False
                order.status = order.SUCCESS
                order.save()

            else:
                comment = f"Пополнение пользоватeлем {user.username} на сумму {round(order.sum, 2)} \nService: FREEKASSA"

                balance = float(order.sum)

                calc = Calc.objects.create(
                    user=user,
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
        item = CompositeItems.objects.filter(
            ext_id=com_item["variation_id"], removed=False
        ).first()
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


@shared_task
def check_output_status_in_moogold(manager=PaymentManager()):
    outputs = Output.objects.filter(active=True).all()

    for output in outputs:
        purchase_items = output.purchase_ci_outputs.all()

        for pci in purchase_items:
            if pci.type == pci.MOOGOLD:
                status = manager._get_status_order_in_moogold(pci.ext_id_order)

                if status == pci.COMPLETED:
                    pci.status = pci.COMPLETED
                if status == pci.PROCCESS:
                    pci.status = pci.PROCCESS
                if status == pci.INCORRECT_DETAILS:
                    pci.status = pci.INCORRECT_DETAILS
                if status == pci.RESTOCK:
                    pci.status = pci.RESTOCK
                if status == pci.REFUNDED:
                    pci.status = pci.REFUNDED

            pci.save()
        if purchase_items.count() != 0:
            if (
                purchase_items.count()
                == output.purchase_ci_outputs.all()
                .filter(status=PurchaseCompositeItems.COMPLETED)
                .count()
            ):
                output.status = output.COMPLETED
                output.active = False

        output.save()
