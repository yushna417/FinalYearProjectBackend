from rest_framework import viewsets, generics
from .models import User, Veg, DailyPrice, Order
from .serializers import UserSerializer, VegSerializer, DailyPriceSerializer, OrderSerializer
# from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated, AllowAny

# Create your views here.

# User = get_user_model()
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

class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]