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
# admin.site.register(Item)
admin.site.register(RarityCategory)
admin.site.register(Category)


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
