from rest_framework import viewsets
from .models import User, Veg, DailyPrice, Order
from .serializers import UserSerializer, VegSerializer, DailyPriceSerializer, OrderSerializer


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
class VegViewSet(viewsets.ModelViewSet):
    queryset = Veg.objects.all()
    serializer_class = VegSerializer

class DailyPriceViewSet(viewsets.ModelViewSet):
    queryset = DailyPrice.objects.all()
    serializer_class = DailyPriceSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
