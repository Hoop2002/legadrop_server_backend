from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    image = models.ImageField(verbose_name="Фотография пользователя")
    locale = models.CharField(verbose_name="Локаль", max_length=8, default="ru")
    verified = models.BooleanField(verbose_name="Верифицирован", default=False)
    individual_percent = models.FloatField(
        verbose_name="Индивидуальный процент", default=1
    )

    def __str__(self):
        return self.user.username