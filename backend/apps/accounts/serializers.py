from rest_framework import serializers

from .models import User
from .services.accounts_services import create_internal_user


class UserSerializer(serializers.ModelSerializer):
    restaurant = serializers.StringRelatedField()
    branch = serializers.StringRelatedField()
    kitchen = serializers.StringRelatedField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "restaurant", "branch", "kitchen"]


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "role", "restaurant", "branch", "kitchen"]

    def validate(self, data):
        role = data.get("role")
        if role == "owner" and not data.get("restaurant"):
            raise serializers.ValidationError({"restaurant": "Owner must be assigned to a restaurant"})
        if role == "branch_manager" and not data.get("branch"):
            raise serializers.ValidationError({"branch": "Branch Manager must be assigned to a branch"})
        if role in ["kitchen_manager", "chef"] and not data.get("kitchen"):
            raise serializers.ValidationError({"kitchen": f"{role.replace('_', ' ').title()} must be assigned to a kitchen"})
        if role == "waiter" and not data.get("branch"):
            raise serializers.ValidationError({"branch": "Waiter must be assigned to a branch"})
        return data

    def create(self, validated_data):
        return create_internal_user(validated_data)
