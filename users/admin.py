from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin
from users.models import UserProfile, UserItems
from django.utils.safestring import mark_safe
from django.urls import reverse


admin.site.unregister(User)


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


class UserProfileInline(admin.TabularInline):
    admin_select_related = ("user",)
    model = UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_select_related = True
    inlines = [UserProfileInline]
