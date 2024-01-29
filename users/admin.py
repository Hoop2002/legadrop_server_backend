from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin
from users.models import UserProfile


admin.site.unregister(User)


class UserProfileInline(admin.TabularInline):
    admin_select_related = ("user",)
    model = UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_select_related = True
    inlines = [UserProfileInline]
