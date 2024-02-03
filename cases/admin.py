from django.contrib import admin

from cases.models import (
    Case,
    ConditionCase,
    OpenedCases,
    Item,
    RarityCategory,
    Category,
)

admin.site.register(ConditionCase)
admin.site.register(OpenedCases)


@admin.register(Category)
class AdminCategory(admin.ModelAdmin):
    readonly_fields = ("category_id",)


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ("case_id", "name", "translit_name", "price")
    readonly_fields = ("created_at", "updated_at", "translit_name", "case_id")
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "case_id",
                    "name",
                    "translit_name",
                    "active",
                    "image",
                    "price",
                    "case_free",
                    "category",
                    "items",
                    "conditions",
                    "created_at",
                    "updated_at",
                    "removed",
                ],
            },
        ),
    ]


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
