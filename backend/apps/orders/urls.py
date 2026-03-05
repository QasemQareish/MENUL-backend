from rest_framework.routers import DefaultRouter
from .views import OrderSessionViewSet, OrderItemViewSet

router = DefaultRouter()
router.register(r'sessions', OrderSessionViewSet, basename='ordersession')
router.register(r'items', OrderItemViewSet, basename='orderitem')

urlpatterns = router.urls
