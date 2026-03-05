from rest_framework import serializers

from apps.accounts.models import User
from apps.accounts.serializers import UserSerializer


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password"]


class LoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField()
    password = serializers.CharField(write_only=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()


__all__ = [
    "RegisterSerializer",
    "LoginSerializer",
    "ChangePasswordSerializer",
    "UserSerializer",
]
