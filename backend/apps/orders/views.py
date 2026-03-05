from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied

from .models import OrderSession, OrderItem
from .serializers import OrderSessionSerializer, OrderItemSerializer
from .services import create_session_if_not_exists, update_order_status, add_order_item
from apps.access_utils import is_kitchen_role, resolve_waiter_branch


class OrderSessionViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSessionSerializer
    permission_classes = [IsAuthenticated]

    def _get_waiter_branch(self, user):
        if user.kitchen_id:
            return user.kitchen.branch
        if user.branch_id:
            return user.branch
        return None

    def get_queryset(self):
        user = self.request.user
        if is_kitchen_role(user):
            return OrderSession.objects.none()
        if user.role == "waiter":
            waiter_branch = resolve_waiter_branch(user)
            if not waiter_branch:
                return OrderSession.objects.none()
            return OrderSession.objects.filter(table__branch=waiter_branch)
        return OrderSession.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        table = serializer.validated_data["table"]

        if is_kitchen_role(user):
            raise PermissionDenied("ليس لديك صلاحية إنشاء جلسة طلب")

        if user.role == "waiter":
            waiter_branch = resolve_waiter_branch(user)
            if not waiter_branch:
                raise PermissionDenied("الويتر يجب أن يكون مربوطًا بفرع أو مطبخ")
            if table.branch != waiter_branch:
                raise PermissionDenied("لا يمكنك إنشاء جلسة خارج نطاق طاولاتك")

        session = create_session_if_not_exists(table)
        serializer.instance = session


class OrderItemViewSet(viewsets.ModelViewSet):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return OrderItem.objects.none()
        if user.role in ["superadmin", "admin"]:
            return OrderItem.objects.all()
        if user.role == "owner":
            return OrderItem.objects.filter(order_session__table__branch__restaurant=user.restaurant)
        if user.role == "branch_manager":
            return OrderItem.objects.filter(order_session__table__branch=user.branch)
        if user.role == "waiter":
            waiter_branch = resolve_waiter_branch(user)
            if not waiter_branch:
                return OrderItem.objects.none()
            return OrderItem.objects.filter(order_session__table__branch=waiter_branch)
        if is_kitchen_role(user):
            return OrderItem.objects.filter(item__kitchen=user.kitchen)
        return OrderItem.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        session = serializer.validated_data["order_session"]
        item = serializer.validated_data["item"]
        quantity = serializer.validated_data.get("quantity", 1)
        notes = serializer.validated_data.get("notes", "")

        if user.is_authenticated:
            if user.role == "chef":
                raise PermissionDenied("الشيف لا يمكنه إضافة عناصر للطلب")

            if user.role not in ["waiter", "branch_manager", "owner", "superadmin", "admin", "customer"]:
                raise PermissionDenied("ليس لديك صلاحية إنشاء هذا الطلب")

            if user.role == "owner" and session.table.branch.restaurant != user.restaurant:
                raise PermissionDenied("لا يمكنك إنشاء طلب خارج مطعمك")

            if user.role == "branch_manager" and session.table.branch != user.branch:
                raise PermissionDenied("لا يمكنك إنشاء طلب خارج فرعك")

            if user.role == "waiter":
                waiter_branch = resolve_waiter_branch(user)
                if not waiter_branch:
                    raise PermissionDenied("الويتر يجب أن يكون مربوطًا بفرع أو مطبخ")
                if session.table.branch != waiter_branch:
                    raise PermissionDenied("لا يمكنك إنشاء طلب خارج نطاق طاولاتك")

        order_item = add_order_item(session=session, item=item, quantity=quantity, notes=notes)
        serializer.instance = order_item

    def perform_update(self, serializer):
        user = self.request.user
        instance = serializer.instance
        new_status = serializer.validated_data.get("status")

        if user.role in ["chef", "kitchen_manager"]:
            if instance.item.kitchen != user.kitchen:
                raise PermissionDenied("لا يمكنك تعديل طلب خارج مطبخك")
            if not new_status:
                raise PermissionDenied("يجب تحديد الحالة الجديدة")
            update_order_status(user, instance, new_status)
            return

        if user.role in ["waiter", "branch_manager", "owner", "superadmin", "admin"]:
            serializer.save()
            return

        raise PermissionDenied("ليس لديك صلاحية تعديل هذا الطلب")
