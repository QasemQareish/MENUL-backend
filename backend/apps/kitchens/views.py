from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import Kitchen
from .serializers import KitchenSerializer


class KitchenViewSet(viewsets.ModelViewSet):
    serializer_class = KitchenSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role in ['superadmin', 'admin']:
            return Kitchen.objects.all()

        if user.role == 'owner':
            return Kitchen.objects.filter(branch__restaurant=user.restaurant)

        if user.role == 'branch_manager':
            return Kitchen.objects.filter(branch=user.branch)

        if user.role == 'kitchen_manager':
            if user.kitchen:
                return Kitchen.objects.filter(id=user.kitchen.id)
            return Kitchen.objects.none()

        return Kitchen.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        branch = serializer.validated_data['branch']

        if user.role not in ['superadmin', 'admin', 'owner', 'branch_manager']:
            raise PermissionDenied('ليس لديك صلاحية إنشاء مطبخ')

        if user.role == 'owner' and branch.restaurant != user.restaurant:
            raise PermissionDenied('لا يمكنك إنشاء مطبخ خارج مطعمك')

        if user.role == 'branch_manager' and branch != user.branch:
            raise PermissionDenied('لا يمكنك إنشاء مطبخ خارج فرعك')

        serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        instance = serializer.instance
        branch = serializer.validated_data.get('branch', instance.branch)

        if user.role in ['superadmin', 'admin']:
            serializer.save()
            return

        if user.role == 'owner' and branch.restaurant == user.restaurant:
            serializer.save()
            return

        if user.role == 'branch_manager' and branch == user.branch and instance.branch == user.branch:
            serializer.save()
            return

        if user.role == 'kitchen_manager' and user.kitchen and instance.id == user.kitchen.id and branch == user.kitchen.branch:
            serializer.save()
            return

        raise PermissionDenied('ليس لديك صلاحية تعديل هذا المطبخ')

    def perform_destroy(self, instance):
        user = self.request.user

        if user.role in ['superadmin', 'admin']:
            instance.delete()
            return

        if user.role == 'owner' and instance.branch.restaurant == user.restaurant:
            instance.delete()
            return

        if user.role == 'branch_manager' and instance.branch == user.branch:
            instance.delete()
            return

        raise PermissionDenied('ليس لديك صلاحية حذف هذا المطبخ')
