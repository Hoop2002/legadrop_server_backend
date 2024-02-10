from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse

from payments.models import PaymentOrder, Calc, PromoCode, Output

admin.site.register(PaymentOrder)
admin.site.register(Output)

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
        ("Связи", {"fields": ("user", "promo_using", "order")}),
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
