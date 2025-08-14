from rest_framework import serializers
from .models import User, Veg, DailyPrice, Order

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone', 'password', 'full_name', 'role', 'profile_image', 'city'] 
        extra_kwargs = {
        "password":{"write_only":True },
        "phone": {"required": True},
        "full_name": {"required": True},
        "role": {"required": True},
        "city": {"required": True},
        }
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class VegSerializer(serializers.ModelSerializer):
    class Meta:
        model = Veg
        fields = ['id', 'name', 'unit']

# serializers.py
class DailyPriceSerializer(serializers.ModelSerializer):
    daily_change = serializers.SerializerMethodField()
    trend = serializers.SerializerMethodField()

    class Meta:
        model = DailyPrice
        fields = '__all__'

    def get_daily_change(self, obj):
        if hasattr(obj, 'daily_change'):
            return round(obj.daily_change, 2)
        return None

    def get_trend(self, obj):
        if hasattr(obj, 'daily_change'):
            if obj.daily_change > 0: return 'up'
            if obj.daily_change < 0: return 'down'
        return 'neutral'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
