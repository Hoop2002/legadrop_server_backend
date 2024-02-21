from django.apps import AppConfig

from django.db.models.signals import post_save


def create_user_profile(sender, instance, **kwargs):
    from users.models import UserProfile

    if not hasattr(instance, "profile"):
        UserProfile.objects.create(user=instance)


def create_ref_link(sender, instance, **kwargs):
    from payments.models import RefLinks

    if hasattr(instance, "profile"):
        if not instance.profile.ref_links.exists():
            RefLinks.objects.create(from_user=instance.profile)


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        from django.contrib.auth.models import User

        post_save.connect(
            create_user_profile,
            sender=User,
        )

        post_save.connect(
            create_user_profile,
            sender=User,
        )
