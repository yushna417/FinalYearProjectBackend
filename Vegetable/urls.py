from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, VegViewSet, DailyPriceViewSet, OrderListView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'vegetables', VegViewSet)
router.register(r'daily-prices', DailyPriceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('orders/', OrderListView.as_view(), name='order-list'),
]
