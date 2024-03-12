from django.http.response import HttpResponseRedirect, HttpResponseBadRequest
from drf_spectacular.utils import extend_schema

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAdminUser, AllowAny
from payments.manager import PaymentManager

from core.models import GenericSettings
from payments.models import (
    PaymentOrder,
    PromoCode,
    RefLinks,
    Output,
    RefOutput,
    PurchaseCompositeItems,
)
from payments.serializers import (
    UserPaymentOrderSerializer,
    AdminPaymentOrderSerializer,
    AdminPromoCodeSerializer,
    AdminListPromoSerializer,
    ActivatePromoCodeSerializer,
    AdminOutputSerializer,
    AdminListOutputSerializer,
    RefLinksAdminSerializer,
    UserListOutputSerializer,
    UserOutputSerializer,
    UserCreateOutputSerializer,
    AdminGetBalanceMoogoldSerializer,
    AdminRefOutputListSerializer,
    AdminRefOutputSerializer,
    UserRefOutputListSerializer,
    UserRefOutputSerializer,
    UserRefOutputCreateSerializer,
    AdminPurchaseListSerializer,
    AdminPurchaseSerializer,
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


@extend_schema(tags=["referral_program"])
class RefLinksViewSet(GenericViewSet):
    queryset = RefLinks.objects
    serializer_class = SuccessSerializer
    permission_classes = [AllowAny]
    lookup_field = "code_data"
    http_method_names = ["get"]

    @extend_schema(request=None, responses={302: None, 200: SuccessSerializer})
    def ref_link(self, request, *args, **kwargs):
        generic = GenericSettings.load()
        domain = generic.redirect_domain
        ref = self.get_queryset().filter(
            code_data=kwargs["code_data"],
            removed=False,
            active=True,
            from_user__isnull=False,
        )
        if not ref.exists():
            return Response(
                {"message": "Промокод не найден"}, status.HTTP_404_NOT_FOUND
            )

        if self.request.get_host() != domain:
            response = HttpResponseRedirect(
                f"https://{domain}/ref/{kwargs['code_data']}"
            )
            return response

        if not request.user.is_authenticated:
            response = HttpResponseRedirect("/sign_in")
            response.set_cookie(key="ref", value=kwargs["code_data"], expires=3600 * 12)
            return response
        if request.user == ref.first().from_user.user:
            return HttpResponseBadRequest("Попытка активировать собственную ссылку")
        message, success = ref.first().activate_link(self.request.user)
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
        if count > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)


@extend_schema(tags=["admin/outputs"])
class AdminOutputsViewSet(ModelViewSet):
    queryset = Output.objects.filter(removed=False)
    serializer_class = AdminOutputSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ["get", "post", "delete"]
    lookup_field = "output_id"

    def get_serializer_class(self):
        if self.action == "list":
            return AdminListOutputSerializer
        return AdminOutputSerializer

    @extend_schema(responses={200: SuccessSerializer}, request=None)
    @action(detail=True, methods=["post"])
    def approval(self, request, *args, **kwargs):
        output = self.get_object()
        if not output:
            return Response(
                {"message": "Такого вывода не существует"},
                status=status.HTTP_404_NOT_FOUND,
            )
        message, success = output.approval_output(approval_user=request.user)

        return Response({"message": message}, status=success)

    @extend_schema(responses={200: SuccessSerializer}, request=None)
    def destroy(self, request, *args, **kwargs):
        output = self.get_object()
        if not output:
            return Response(
                {"message": "Такого вывода не существует"},
                status=status.HTTP_404_NOT_FOUND,
            )

        message, success = output.remove(user_remove=request.user)

        return Response({"message": message}, status=success)

    def create(self, request, *args, **kwargs):
        return Response({"detail": "Method Not Allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@extend_schema(tags=["admin/ref_links"])
class AdminRefLinkViewSet(ModelViewSet):
    queryset = RefLinks.objects.filter(removed=False)
    serializer_class = RefLinksAdminSerializer
    permission_classes = [IsAdminUser]
    lookup_field = "code_data"
    http_method_names = ["get", "put", "delete"]

    @extend_schema(
        description=(
            "Ни одно поле для этого запроса не является обязательным, можно отправить хоть пустой"
            "объект, тогда ничего не будет обновлено. Но если поле отправляется, то его надо заполнить"
        )
    )
    def update(self, request, *args, **kwargs):
        return super(AdminRefLinkViewSet, self).update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        count = (
            self.get_queryset()
            .filter(code_data=self.kwargs["code_data"], removed=False)
            .update(removed=True, active=False)
        )
        if count > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)


@extend_schema(tags=["output"])
class UserOutputsViewSet(ModelViewSet):
    queryset = Output.objects.filter(removed=False)
    serializer_class = UserOutputSerializer
    http_method_names = ["get", "post"]
    lookup_field = "output_id"
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action == "list":
            return UserListOutputSerializer
        if self.action == "create":
            return UserCreateOutputSerializer
        return UserOutputSerializer

    def list(self, request, *args, **kwargs):
        outputs = request.user.user_outputs.filter(removed=False).all()
        result = self.paginate_queryset(outputs)
        serializer = self.get_serializer(result, many=True)
        response = self.get_paginated_response(serializer.data)
        return response

    def create(self, request, *args, **kwargs):
        if not request.user.profile.withdrawal_is_allowed:
            return Response(
                {"message": "Вам не разрешен вывод"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            output = serializer.save()
            return Response(UserOutputSerializer(output).data)


@extend_schema(tags=["admin/analytics"])
class AdminBalanceInMoogoldViewSet(GenericViewSet):
    http_method_names = ["get"]
    serializer_class = AdminGetBalanceMoogoldSerializer
    permission_classes = [IsAdminUser]

    @action(detail=False)
    def balance(self, request, manager=PaymentManager()):
        balance = manager._get_moogold_balance()
        return Response(AdminGetBalanceMoogoldSerializer({"balance": balance}).data)


@extend_schema(tags=["admin/ref_outputs"])
class AdminRefOutputViewSet(ModelViewSet):
    http_method_names = ["get", "post", "delete"]
    queryset = RefOutput.objects.filter(removed=False)
    serializer_class = AdminRefOutputSerializer
    permission_classes = [IsAdminUser]
    lookup_field = "ref_output_id"

    def get_serializer_class(self):
        if self.action == "list":
            return AdminRefOutputListSerializer
        return AdminRefOutputSerializer

    @extend_schema(responses={200: SuccessSerializer}, request=None)
    def destroy(self, request, *args, **kwargs):
        ref_output = self.get_object()
        if not ref_output:
            return Response(
                {"message": "Такого вывода не существует"},
                status=status.HTTP_404_NOT_FOUND,
            )

        message, success = ref_output.remove()

        return Response({"message": message}, status=success)

    @extend_schema(responses={200: SuccessSerializer}, request=None)
    @action(detail=True, methods=["post"])
    def completed(self, request, *args, **kwargs):
        ref_output = self.get_object()
        if not ref_output:
            return Response(
                {"message": "Такого вывода не существует"},
                status=status.HTTP_404_NOT_FOUND,
            )

        message, success = ref_output.completed()

        return Response({"message": message}, status=success)

    @extend_schema(responses={200: SuccessSerializer}, request=None)
    @action(detail=True, methods=["post"])
    def canceled(self, request, *args, **kwargs):
        ref_output = self.get_object()
        if not ref_output:
            return Response(
                {"message": "Такого вывода не существует"},
                status=status.HTTP_404_NOT_FOUND,
            )

        message, success = ref_output.cancel()

        return Response({"message": message}, status=success)


@extend_schema(tags=["admin/purchase"])
class AdminPurchaseViewSet(ModelViewSet):
    http_method_names = ["get"]
    queryset = PurchaseCompositeItems.objects.filter(removed=False)
    serializer_class = AdminPurchaseSerializer
    permission_classes = [IsAdminUser]
    lookup_field = "id"

    def get_serializer_class(self):
        if self.action == "list":
            return AdminPurchaseListSerializer
        return AdminPurchaseSerializer


@extend_schema(tags=["ref_outputs"])
class UserRefOutputViewSet(ModelViewSet):
    http_method_names = ["get", "post"]
    queryset = RefOutput.objects.filter(removed=False)
    lookup_field = "ref_output_id"
    serializer_class = UserRefOutputSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return UserRefOutputListSerializer
        if self.action == "create":
            return UserRefOutputCreateSerializer
        return UserRefOutputSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            ref_output = serializer.save()
            return Response(UserRefOutputSerializer(ref_output).data)


@extend_schema(tags=["freekassa"])
class AdminFreekassaNotifyViewSet(GenericViewSet):
    http_method_names = ["post"]
    permission_classes = [AllowAny]

    def notification(self, request, *args, **kwargs):
        data = request.data
        order = PaymentOrder.objects.filter(order_id=data["MERCHANT_ORDER_ID"]).first()
        order.active = True
        order.status = PaymentOrder.SUCCESS
        order.save()
        return Response({"message": "OK"})
