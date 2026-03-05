from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import Category, Item
from .serializers import CategorySerializer, ItemSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ["superadmin", "admin"]:
            return Category.objects.all()
        if user.role == "owner":
            return Category.objects.filter(kitchen__branch__restaurant=user.restaurant)
        if user.role == "branch_manager":
            return Category.objects.filter(kitchen__branch=user.branch)
        if user.role in ["kitchen_manager", "chef"]:
            return Category.objects.filter(kitchen=user.kitchen)
        return Category.objects.none()

    def _enforce_write_scope(self, kitchen):
        user = self.request.user
        if user.role in ["superadmin", "admin"]:
            return
        if user.role == "owner" and kitchen.branch.restaurant == user.restaurant:
            return
        if user.role == "branch_manager" and kitchen.branch == user.branch:
            return
        if user.role == "kitchen_manager" and kitchen == user.kitchen:
            return
        raise PermissionDenied("ليس لديك صلاحية التعديل على هذا التصنيف")

    def perform_create(self, serializer):
        kitchen = serializer.validated_data["kitchen"]
        self._enforce_write_scope(kitchen)
        serializer.save()

    def perform_update(self, serializer):
        kitchen = serializer.validated_data.get("kitchen", serializer.instance.kitchen)
        self._enforce_write_scope(kitchen)
        serializer.save()


class ItemViewSet(viewsets.ModelViewSet):
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ["superadmin", "admin"]:
            return Item.objects.all()
        if user.role == "owner":
            return Item.objects.filter(kitchen__branch__restaurant=user.restaurant)
        if user.role == "branch_manager":
            return Item.objects.filter(kitchen__branch=user.branch)
        if user.role in ["kitchen_manager", "chef"]:
            return Item.objects.filter(kitchen=user.kitchen)
        return Item.objects.none()

    def _enforce_write_scope(self, kitchen):
        user = self.request.user
        if user.role in ["superadmin", "admin"]:
            return
        if user.role == "owner" and kitchen.branch.restaurant == user.restaurant:
            return
        if user.role == "branch_manager" and kitchen.branch == user.branch:
            return
        if user.role == "kitchen_manager" and kitchen == user.kitchen:
            return
        raise PermissionDenied("ليس لديك صلاحية التعديل على هذا العنصر")

    def perform_create(self, serializer):
        kitchen = serializer.validated_data.get("kitchen") or serializer.validated_data["category"].kitchen
        self._enforce_write_scope(kitchen)
        serializer.save()

    def perform_update(self, serializer):
        kitchen = serializer.validated_data.get("kitchen")
        if not kitchen and serializer.validated_data.get("category"):
            kitchen = serializer.validated_data["category"].kitchen
        kitchen = kitchen or serializer.instance.kitchen
        self._enforce_write_scope(kitchen)
        serializer.save()
