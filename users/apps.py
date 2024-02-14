from django.apps import AppConfig

from django.db.models.signals import post_save


def create_user_profile(sender, instance, **kwargs):
    from users.models import UserProfile
    if not instance.profile:
        UserProfile.objects.create(user=instance)


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        from django.contrib.auth.models import User

        post_save.connect(
            create_user_profile,
            sender=User,
        )
