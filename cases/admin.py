from django.contrib import admin

from cases.models import (
    Case,
    ConditionCase,
    OpenedCases,
    Item,
    RarityCategory,
    Category,
)

admin.site.register(Case)
admin.site.register(ConditionCase)
admin.site.register(OpenedCases)
admin.site.register(Category)


@admin.register(RarityCategory)
class RarityAdmin(admin.ModelAdmin):
    list_display = ("rarity_id", "name", "category_percent")
    fields = ("rarity_id", "name", "category_percent")


class CasesInline(admin.TabularInline):
    model = Case.items.through
    extra = 0


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "item_id", "price", "sale", "created_at")
    list_editable = ("sale", "price")
    list_filter = ("sale", "created_at")
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
                    "removed",
                )
            },
        ),
        (
            "Цены",
            {"fields": ("price", "purchase_price", "sale_price", "percent_price")},
        ),
    )
    #
    readonly_fields = ("item_id", "created_at")
    inlines = [CasesInline]
