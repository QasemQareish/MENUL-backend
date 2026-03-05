from rest_framework import serializers
from .models import Restaurant, Branch, Table

class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ['id', 'branch', 'number', 'seats']


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'restaurant', 'branch_number', 'name', 'location', 'is_active']
        read_only_fields = ['id', 'branch_number']

class RestaurantSerializer(serializers.ModelSerializer):
    branches = BranchSerializer(many=True, read_only=True)

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'default_language', 'primary_color', 'branches']
