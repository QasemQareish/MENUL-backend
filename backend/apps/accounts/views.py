from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import User
from .serializers import UserSerializer, UserCreateSerializer


ROLE_HIERARCHY = {
    "superadmin": 5,
    "admin": 4,
    "owner": 3,
    "branch_manager": 2,
    "kitchen_manager": 2,
    "chef": 1,
    "waiter": 1,
}


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        user = self.request.user

        if user.role == "superadmin":
            return User.objects.all()
        if user.role == "admin":
            return User.objects.filter(role__in=['owner', 'branch_manager', 'kitchen_manager', 'chef', 'waiter'])
        if user.role == "owner":
            return User.objects.filter(restaurant=user.restaurant)
        if user.role == "branch_manager":
            return User.objects.filter(branch=user.branch)
        if user.role == "kitchen_manager":
            return User.objects.filter(kitchen=user.kitchen)
        raise PermissionDenied("Not authorized to access this resource")

    def _check_permissions_for_user(self, target_user: User):
        current_user = self.request.user

        if ROLE_HIERARCHY.get(target_user.role, 0) >= ROLE_HIERARCHY.get(current_user.role, 0):
            raise PermissionDenied("You cannot modify or delete a user with same or higher role.")

        if current_user.role == "owner" and target_user.restaurant != current_user.restaurant:
            raise PermissionDenied("User is not in your restaurant.")
        if current_user.role == "branch_manager" and target_user.branch != current_user.branch:
            raise PermissionDenied("User is not in your branch.")
        if current_user.role == "kitchen_manager" and target_user.kitchen != current_user.kitchen:
            raise PermissionDenied("User is not in your kitchen.")

    def perform_create(self, serializer):
        current_user = self.request.user
        target_role = serializer.validated_data.get("role")

        if current_user.role not in ["superadmin", "admin", "owner", "branch_manager", "kitchen_manager"]:
            raise PermissionDenied("Not authorized to create users")

        if ROLE_HIERARCHY.get(target_role, 0) >= ROLE_HIERARCHY.get(current_user.role, 0):
            raise PermissionDenied("You cannot create a user with same or higher role")

        restaurant = serializer.validated_data.get("restaurant")
        branch = serializer.validated_data.get("branch")
        kitchen = serializer.validated_data.get("kitchen")

        if current_user.role == "owner":
            if restaurant and restaurant != current_user.restaurant:
                raise PermissionDenied("Restaurant is outside your scope")
            if branch and branch.restaurant != current_user.restaurant:
                raise PermissionDenied("Branch is outside your scope")
            if kitchen and kitchen.branch.restaurant != current_user.restaurant:
                raise PermissionDenied("Kitchen is outside your scope")

        if current_user.role == "branch_manager":
            if branch and branch != current_user.branch:
                raise PermissionDenied("Branch is outside your scope")
            if kitchen and kitchen.branch != current_user.branch:
                raise PermissionDenied("Kitchen is outside your scope")

        if current_user.role == "kitchen_manager" and kitchen and kitchen != current_user.kitchen:
            raise PermissionDenied("Kitchen is outside your scope")

        try:
            serializer.save()
        except ValueError as e:
            raise ValidationError({"detail": str(e)})

    def perform_update(self, serializer):
        target_user = self.get_object()
        self._check_permissions_for_user(target_user)
        serializer.save()

    def perform_destroy(self, instance):
        self._check_permissions_for_user(instance)
        instance.delete()
