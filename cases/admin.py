from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse

from cases.models import (
    Case,
    ConditionCase,
    OpenedCases,
    Item,
    RarityCategory,
    Category,
    UserItems,
)

admin.site.register(Case)
admin.site.register(ConditionCase)
admin.site.register(OpenedCases)
admin.site.register(RarityCategory)
admin.site.register(Category)


@admin.register(UserItems)
class UserItemsAdmin(admin.ModelAdmin):
    list_display = ("id", "user_link", "item", "active")
    list_display_links = ("id",)
    list_filter = ("user", "active", "item")

    def user_link(self, instance):
        return mark_safe(
            '<a href="{}">{}</a>'.format(
                reverse("admin:auth_user_change", args=(instance.user.pk,)),
                instance.user.username,
            )
        )

    user_link.short_description = "Пользователь"


class CasesInline(admin.TabularInline):
    model = Case.items.through
    extra = 0


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "item_id", "price", "sale", "created_at")
    list_editable = ("sale", "price")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "item_id",
                    "name",
                    "sale",
                    "color",
                    "image",
                    "step_down_factor",
                    "rarity_category",
                    "created_at",
                )
            },
        ),
        ("Цены", {"fields": ("price", "price_in_rubles")}),
    )
    #
    readonly_fields = ("item_id", "created_at")
    inlines = [CasesInline]
