from django.contrib import admin
from core.models import GenericSettings


@admin.register(GenericSettings)
class GenericSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Бафы статистики для пользователей",
            {
                "fields": (
                    "opened_cases_buff",
                    "users_buff",
                    "online_buff",
                    "purchase_buff",
                    "output_crystal_buff",
                )
            },
        ),
        ("Базовые настройки", {"fields": ("domain_url", "redirect_domain")}),
    )
