from django.contrib import admin, messages
from django.utils.safestring import mark_safe
from django.urls import reverse

from payments.models import (
    PaymentOrder,
    Calc,
    PromoCode,
    Output,
    CompositeItems,
    PurchaseCompositeItems,
    RefLinks,
)
from users.models import UserItems


@admin.register(PaymentOrder)
class AdminPaymentOrder(admin.ModelAdmin):
    list_display = ("order_id", "sum", "user_link", "manually_approved", "active")
    readonly_fields = ("created_at", "updated_at")
    actions = ["approve_payment"]

    def user_link(self, instance):
        return mark_safe(
            '<a href="{}">{}</a>'.format(
                reverse("admin:auth_user_change", args=(instance.user.pk,)),
                instance.user.username,
            )
        )

    user_link.short_description = "Пользователь"

    @admin.action(description="Ручное одобрение")
    def approve_payment(self, request, queryset):
        success = []
        error = []
        for instance in queryset:
            try:
                instance.approval_payment_order(request.user)
                success.append(f"ордер {instance.order_id} успешно одобрен")
            except Exception as err:
                error.append(f"ордер {instance.order_id} не одобрен")
        if len(success) > 0:
            self.message_user(request, message=f"{success}", level=messages.SUCCESS)
        if len(error) > 0:
            self.message_user(request, message=f"{error}", level=messages.ERROR)


@admin.register(RefLinks)
class RefLinkAdmin(admin.ModelAdmin):
    list_display = ("code_data", "user_link", "active")
    readonly_fields = ("created_at", "updated_at")

    def user_link(self, instance):
        return mark_safe(
            '<a href="{}">{}</a>'.format(
                reverse("admin:auth_user_change", args=(instance.from_user.user.pk,)),
                instance.from_user.user.username,
            )
        )

    user_link.short_description = "Пользователь"


@admin.register(PurchaseCompositeItems)
class AdminPurchaseCompositeItems(admin.ModelAdmin):
    fields = (
        "pci_id",
        "name",
        "type",
        "status",
        "ext_id_order",
        "player_id",
        "output",
        "created_at",
        "updated_at",
        "removed",
    )
    readonly_fields = ("updated_at", "created_at")


@admin.register(CompositeItems)
class AdminCompositeItems(admin.ModelAdmin):
    fields = (
        "technical_name",
        "name",
        "type",
        "service",
        "ext_id",
        "composite_item_id",
        "crystals_quantity",
        "price_dollar",
        "created_at",
        "updated_at",
        "removed",
    )

    readonly_fields = ("composite_item_id", "updated_at", "created_at")


class OutputInline(admin.TabularInline):
    model = UserItems
    extra = 0


class PurchaseCompositeItemsOutputInline(admin.TabularInline):
    model = PurchaseCompositeItems
    extra = 0


@admin.register(Output)
class OutputAdmin(admin.ModelAdmin):
    fields = (
        "output_id",
        "type",
        "user",
        "player_id",
        "comment",
        "status",
        "created_at",
        "updated_at",
        "active",
        "removed",
        "remove_user",
    )
    inlines = [OutputInline, PurchaseCompositeItemsOutputInline]
    readonly_fields = ("output_id", "updated_at", "created_at")


@admin.register(Calc)
class CalcAdmin(admin.ModelAdmin):
    list_display = (
        "calc_id",
        "user_link",
        "debit",
        "credit",
        "comment",
        "created_at",
    )
    list_display_links = ("calc_id", "user_link")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Связи", {"fields": ("user", "promo_using", "order", "ref_link")}),
        ("Деньги", {"fields": ("debit", "credit", "balance", "comment")}),
        (None, {"fields": ("created_at", "updated_at", "demo")}),
    )

    def user_link(self, instance):
        return mark_safe(
            '<a href="{}">{}</a>'.format(
                reverse("admin:auth_user_change", args=(instance.user.pk,)),
                instance.user.username,
            )
        )

    user_link.short_description = "Пользователь"


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "summ", "type", "created_at", "active")
    list_display_links = ("name",)
    list_editable = ("active",)
    fieldsets = (
        ("Основа", {"fields": ("name", "code_data", "type", "activations", "removed")}),
        (
            "Настройки",
            {
                "fields": (
                    "summ",
                    "limit_for_user",
                    "percent",
                    "bonus_limit",
                    "limit_activations",
                    "to_date",
                    "active",
                )
            },
        ),
        ("Даты", {"fields": ("created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at", "activations")
