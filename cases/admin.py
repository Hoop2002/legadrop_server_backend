from django.contrib import admin

from cases.models import (
    Case,
    ConditionCase,
    OpenedCases,
    Item,
    RarityCategory,
    Category,
    Contests,
)

admin.site.register(ConditionCase)


@admin.register(Contests)
class ContestsAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "timer", "active", "one_time")
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("items", "conditions", "participants")


@admin.register(OpenedCases)
class OpenedCasesAdmin(admin.ModelAdmin):
    list_display = ("case", "user", "open_date")
    readonly_fields = ("open_date",)


@admin.register(Category)
class AdminCategory(admin.ModelAdmin):
    readonly_fields = ("category_id",)


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ("case_id", "name", "translit_name", "price")
    readonly_fields = ("created_at", "updated_at", "translit_name", "case_id")
    filter_horizontal = ("items", "conditions")
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
    fields = ("rarity_id", "name", "category_percent", "rarity_color")
    readonly_fields = ("rarity_id",)


class CasesInline(admin.TabularInline):
    model = Case.items.through
    extra = 0


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "item_id",
        "price",
        "sale",
        "service",
        "type",
        "crystals_quantity",
        "is_output",
        "created_at",
    )
    list_editable = ("sale", "price")
    list_filter = ("sale", "created_at")
    search_fields = ("name", "item_id")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "item_id",
                    "name",
                    "sale",
                    "type",
                    "service",
                    "image",
                    "step_down_factor",
                    "rarity_category",
                    "crystals_quantity",
                    "is_output",
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
