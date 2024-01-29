from django.contrib import admin

# Register your models here.

from payments.models import PaymentOrder

admin.site.register(PaymentOrder)
