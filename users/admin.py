from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin
from users.models import UserProfile, UserItems, ActivatedPromo, ActivatedLinks
from django.utils.safestring import mark_safe
from django.urls import reverse


admin.site.unregister(User)


@admin.register(UserItems)
class UserItemsAdmin(admin.ModelAdmin):
    list_display = ("id", "user_link", "item", "active", "withdrawn")
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


class UserProfileInline(admin.TabularInline):
    admin_select_related = ("user",)
    model = UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_select_related = True
    inlines = [UserProfileInline]


@admin.register(ActivatedPromo)
class PromoActivationsAdmin(admin.ModelAdmin):
    list_display = ("user", "promo", "created_at")
    readonly_fields = ("created_at",)


@admin.register(ActivatedLinks)
class ActivatedLinksAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "link", "bonus_using")
    readonly_fields = ("created_at", "updated_at")
