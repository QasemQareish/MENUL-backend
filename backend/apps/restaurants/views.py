from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import Restaurant, Branch, Table
from .serializers import RestaurantSerializer, BranchSerializer, TableSerializer
from apps.access_utils import is_kitchen_role, resolve_waiter_branch


class RestaurantViewSet(viewsets.ModelViewSet):
    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['superadmin', 'admin']:
            return Restaurant.objects.all()
        if user.role == 'owner':
            return Restaurant.objects.filter(id=user.restaurant_id)
        return Restaurant.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role not in ['superadmin', 'admin']:
            raise PermissionDenied('ليس لديك صلاحية إنشاء مطعم')
        serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        if user.role in ['superadmin', 'admin']:
            serializer.save()
            return
        if user.role == 'owner' and serializer.instance.id == user.restaurant_id:
            serializer.save()
            return
        raise PermissionDenied('ليس لديك صلاحية تعديل هذا المطعم')

    def perform_destroy(self, instance):
        user = self.request.user
        if user.role not in ['superadmin', 'admin']:
            raise PermissionDenied('ليس لديك صلاحية حذف هذا المطعم')
        if instance.branches.exists():
            raise PermissionDenied('لا يمكن حذف مطعم يحتوي على فروع')
        instance.delete()


class BranchViewSet(viewsets.ModelViewSet):
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return Branch.objects.all()
        if user.role == 'admin':
            return Branch.objects.filter(restaurant__isnull=False)
        if user.role == 'owner':
            return Branch.objects.filter(restaurant=user.restaurant)
        if user.role == 'branch_manager' and user.branch:
            return Branch.objects.filter(id=user.branch.id)
        return Branch.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        restaurant = serializer.validated_data['restaurant']

        if user.role not in ['superadmin', 'admin', 'owner']:
            raise PermissionDenied('ليس لديك صلاحية إنشاء فرع')

        if user.role == 'owner' and restaurant != user.restaurant:
            raise PermissionDenied('لا يمكنك إنشاء فرع خارج مطعمك')

        last_branch = Branch.objects.filter(restaurant=restaurant).order_by('-branch_number').first()
        next_number = 1 if not last_branch else last_branch.branch_number + 1
        serializer.save(branch_number=next_number, is_active=True)

    def perform_update(self, serializer):
        user = self.request.user
        instance = serializer.instance
        target_restaurant = serializer.validated_data.get('restaurant', instance.restaurant)

        if user.role in ['superadmin', 'admin']:
            serializer.save()
            return
        if user.role == 'owner' and target_restaurant == user.restaurant:
            serializer.save()
            return
        if user.role == 'branch_manager' and user.branch and instance.id == user.branch.id:
            serializer.save()
            return
        raise PermissionDenied('ليس لديك صلاحية تعديل هذا الفرع')

    def perform_destroy(self, instance):
        user = self.request.user

        if user.role not in ['superadmin', 'admin', 'owner']:
            raise PermissionDenied('ليس لديك صلاحية حذف هذا الفرع')

        if user.role == 'owner' and instance.restaurant != user.restaurant:
            raise PermissionDenied('لا يمكنك حذف فرع خارج مطعمك')

        if instance.tables.exists():
            for table in instance.tables.all():
                if table.order_sessions.exists():
                    raise PermissionDenied('لا يمكن حذف فرع يحتوي على طلبات نشطة')
        instance.delete()


class TableViewSet(viewsets.ModelViewSet):
    serializer_class = TableSerializer
    permission_classes = [IsAuthenticated]

    def _is_kitchen_role(self, user):
        return user.role in ['kitchen_manager', 'chef']

    def _get_waiter_branch(self, user):
        if user.kitchen_id:
            return user.kitchen.branch
        if user.branch_id:
            return user.branch
        return None

    def get_queryset(self):
        user = self.request.user
        if is_kitchen_role(user):
            return Table.objects.none()
        if user.role == 'waiter':
            waiter_branch = resolve_waiter_branch(user)
            if not waiter_branch:
                return Table.objects.none()
            return Table.objects.filter(branch=waiter_branch)
        return Table.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        if is_kitchen_role(user):
            raise PermissionDenied('ليس لديك صلاحية إنشاء طاولة')

        if user.role == 'waiter':
            waiter_branch = resolve_waiter_branch(user)
            if not waiter_branch:
                raise PermissionDenied('الويتر يجب أن يكون مربوطًا بفرع أو مطبخ')
            if serializer.validated_data['branch'] != waiter_branch:
                raise PermissionDenied('لا يمكنك إنشاء طاولة خارج نطاقك')

        serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        if is_kitchen_role(user):
            raise PermissionDenied('ليس لديك صلاحية تعديل هذه الطاولة')

        if user.role == 'waiter':
            waiter_branch = resolve_waiter_branch(user)
            if not waiter_branch:
                raise PermissionDenied('الويتر يجب أن يكون مربوطًا بفرع أو مطبخ')
            target_branch = serializer.validated_data.get('branch', serializer.instance.branch)
            if serializer.instance.branch != waiter_branch or target_branch != waiter_branch:
                raise PermissionDenied('لا يمكنك تعديل طاولة خارج نطاقك')

        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if is_kitchen_role(user):
            raise PermissionDenied('ليس لديك صلاحية حذف هذه الطاولة')

        if user.role == 'waiter':
            waiter_branch = resolve_waiter_branch(user)
            if not waiter_branch or instance.branch != waiter_branch:
                raise PermissionDenied('لا يمكنك حذف طاولة خارج نطاقك')

        instance.delete()
