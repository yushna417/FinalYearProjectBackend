from rest_framework import serializers
from .models import User, Veg, DailyPrice, Order

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone', 'password', 'full_name', 'role', 'profile_image', 'city'] 
        extra_kwargs = {"password":{"write_only":True }}
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

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
