from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, VegViewSet, DailyPriceViewSet, OrderViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'vegetables', VegViewSet)
router.register(r'daily-prices', DailyPriceViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
