from rest_framework import serializers
from .models import User, Veg, DailyPrice, Order

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class VegSerializer(serializers.ModelSerializer):
    class Meta:
        model = Veg
        fields = '__all__'

class DailyPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyPrice
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
