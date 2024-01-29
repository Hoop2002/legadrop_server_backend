from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from cases.serializers import CasesSerializer
from cases.models import Case


class CasesViewSet(ModelViewSet):
    serializer_class = CasesSerializer
    queryset = Case.objects

    def list(self, request, *args, **kwargs):
        q = Case.objects.all()
        ser = self.get_serializer(q)
        return Response(ser.data)
