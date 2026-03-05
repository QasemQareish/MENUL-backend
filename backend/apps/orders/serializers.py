from rest_framework import serializers

from apps.restaurants.models import Table
from apps.access_utils import resolve_waiter_branch
from .models import OrderSession, OrderItem


class FlexibleTableField(serializers.PrimaryKeyRelatedField):
    """
    Accepts table primary key by default.
    If pk is not found, for authenticated staff it falls back to table `number`
    within their allowed scope (branch for waiter/branch_manager, restaurant for owner).
    """

    def to_internal_value(self, data):
        try:
            return super().to_internal_value(data)
        except serializers.ValidationError:
            request = self.context.get("request")

            try:
                table_number = int(data)
            except (TypeError, ValueError):
                raise

            queryset = self.get_queryset()
            candidates = queryset.none()

            if request and request.user.is_authenticated:
                user = request.user
                if user.role == "waiter":
                    waiter_branch = resolve_waiter_branch(user)
                    if waiter_branch:
                        candidates = queryset.filter(branch=waiter_branch, number=table_number)
                elif user.role == "branch_manager" and user.branch_id:
                    candidates = queryset.filter(branch=user.branch, number=table_number)
                elif user.role == "owner" and user.restaurant_id:
                    candidates = queryset.filter(branch__restaurant=user.restaurant, number=table_number)
                else:
                    candidates = queryset.filter(number=table_number)
            else:
                candidates = queryset.filter(number=table_number)

            count = candidates.count()
            if count == 1:
                return candidates.first()

            if count > 1:
                raise serializers.ValidationError(
                    "رقم الطاولة غير فريد. أرسل رقم المعرف الأساسي للطاولة (id)."
                )

            raise serializers.ValidationError(f'Invalid pk "{data}" - object does not exist.')


class OrderItemSerializer(serializers.ModelSerializer):
    session_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = OrderItem
        fields = "__all__"
        read_only_fields = (
            "price_at_order_time",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        request = self.context.get("request")
        is_create = self.instance is None

        if not is_create:
            return attrs

        order_session = attrs.get("order_session")
        provided_password = attrs.get("session_password")

        if not order_session:
            raise serializers.ValidationError({"order_session": "رقم الجلسة مطلوب"})

        if not order_session.active:
            raise serializers.ValidationError({"order_session": "الجلسة مغلقة"})

        if request and request.user.is_authenticated:
            return attrs

        if not provided_password:
            raise serializers.ValidationError({"session_password": "كود الجلسة مطلوب"})

        if provided_password != order_session.session_password:
            raise serializers.ValidationError({"session_password": "كود الجلسة غير صحيح"})

        return attrs


class OrderSessionSerializer(serializers.ModelSerializer):
    table = FlexibleTableField(queryset=Table.objects.all())
    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = OrderSession
        fields = "__all__"
        read_only_fields = (
            "active",
            "total_amount",
            "session_password",
            "opened_at",
            "closed_at",
        )
