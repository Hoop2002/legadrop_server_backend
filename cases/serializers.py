from rest_framework.serializers import ModelSerializer
from cases.models import Case


class CasesSerializer(ModelSerializer):
    class Meta:
        model = Case
        fields = (
            "id",
            "name",
        )
