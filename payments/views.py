from django.http.response import HttpResponseRedirect
from drf_spectacular.utils import extend_schema

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAdminUser, AllowAny


from payments.models import PaymentOrder, PromoCode
from payments.serializers import (
    UserPaymentOrderSerializer,
    AdminPaymentOrderSerializer,
    AdminPromoCodeSerializer,
    AdminListPromoSerializer,
    ActivatePromoCodeSerializer,
)
from utils.serializers import SuccessSerializer


class UserPaymentOrderViewSet(ModelViewSet):
    serializer_class = UserPaymentOrderSerializer
    queryset = PaymentOrder.objects
    pagination_class = LimitOffsetPagination
    lookup_field = "order_id"
    http_method_names = ["get", "post"]

    def list(self, request, *args, **kwargs):
        payments = request.user.user_payments_orders.all()
        result = self.paginate_queryset(payments)
        serializer = self.get_serializer(result, many=True)
        response = self.get_paginated_response(serializer.data)
        return response


@extend_schema(tags=["admin/payments"])
class AdminPaymentOrderViewSet(ModelViewSet):
    serializer_class = AdminPaymentOrderSerializer
    queryset = PaymentOrder.objects.all()
    permission_classes = [IsAdminUser]
    lookup_field = "order_id"
    http_method_names = ["get", "post"]

    @extend_schema(responses={200: SuccessSerializer}, request=None)
    @action(detail=True, methods=["post"])
    def approval(self, request, *args, **kwargs):
        payment = self.get_object()
        if not payment:
            return Response(
                {"message": "Такого пополнения не существует"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not payment.active:
            return Response(
                {"message": "Уже одобрен или отменен"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        message, success = payment.approval_payment_order(approval_user=request.user)

        return Response({"message": message}, status=status.HTTP_200_OK)


@extend_schema(tags=["promo"])
class PromoViewSet(GenericViewSet):
    queryset = PromoCode.objects
    serializer_class = ActivatePromoCodeSerializer
    lookup_field = "code_data"
    http_method_names = ["post", "get"]

    def get_permissions(self):
        if self.action == "ref_link":
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    @extend_schema(responses={200: SuccessSerializer})
    @action(detail=False, methods=["post"])
    def activate(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        promo = PromoCode.objects.get(code_data=serializer.validated_data["code_data"])
        message, success = promo.activate_promo(self.request.user)
        if not success:
            return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": message}, status=status.HTTP_200_OK)

    @extend_schema(request=None, responses={302: None})
    def ref_link(self, request, *args, **kwargs):
        promo = self.get_queryset().filter(
            code_data=kwargs["code_data"],
            removed=False,
            active=True,
            from_user__isnull=False,
        )
        if not promo.exists():
            return Response({"message": "Промокод не найден"}, status.HTTP_400_BAD_REQUEST)
        if not request.user.is_authenticated:
            response = HttpResponseRedirect('/sign_in')
            response.set_cookie(key='ref', value=kwargs['code_data'])
            return response
        message, success = promo.first().activate_promo(self.request.user)
        if not success:
            return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": message}, status=status.HTTP_200_OK)


@extend_schema(tags=["admin/promo"])
class AdminPromoCodeViewSet(ModelViewSet):
    queryset = PromoCode.objects.filter(removed=False)
    serializer_class = AdminPromoCodeSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ["get", "post", "delete", "put"]

    def get_serializer_class(self):
        if self.action == "list":
            return AdminListPromoSerializer
        return AdminPromoCodeSerializer

    @extend_schema(
        description=(
            "Ни одно поле для этого запроса не является обязательным, можно отправить хоть пустой"
            "объект, тогда ничего не будет обновлено. Но если поле отправляется, то его надо заполнить"
        )
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(request=None)
    def destroy(self, request, *args, **kwargs):
        count = (
            self.get_queryset()
            .filter(id=self.kwargs["pk"], removed=False)
            .update(removed=True)
        )
        if count < 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)
