from django.core.management import BaseCommand

from cases.models import RarityCategory


class Command(BaseCommand):

    def handle(self, *args, **options):
        d = ["COMMON", "UNCOMMON", "RARE", "MYTHICAL", "LEGENDARY", "ULTRALEGENDARY"]
        data = []
        for value in d:
            data.append(RarityCategory(name=value))

        RarityCategory.objects.bulk_create(data)
