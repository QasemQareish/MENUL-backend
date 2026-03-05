from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import KitchenViewSet

router = DefaultRouter()
router.register(r'kitchens', KitchenViewSet, basename='kitchen')

urlpatterns = [
    path('', include(router.urls)),
]
