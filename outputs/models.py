from django.db import models
from utils.functions.output_id_generator import output_id_generator


class Output(models.Model):
    MOOGOLD = "moogold"
    TEST = "test"

    OUTPUT_TYPES_CHOICES = (
        (MOOGOLD, "Вывод через сервис Moogold"),
        (TEST, "Вывод test - 'не использовать!'"),
    )

    type_output = models.CharField(max_length=64, choices=OUTPUT_TYPES_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
