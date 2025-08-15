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

class DailyPriceSerializer(serializers.ModelSerializer):
    daily_change = serializers.SerializerMethodField()
    trend = serializers.SerializerMethodField()

    class Meta:
        model = DailyPrice
        fields = [
            'id', 'date', 'min_price', 'max_price', 'avg_price',
            'vegetable', 'daily_change', 'trend',
        ]

    def get_daily_change(self, obj):
        prev_price = getattr(obj, 'previous_price', None)
        if prev_price is None or prev_price == 0:
            return None
        return round(((obj.avg_price - prev_price) / prev_price) * 100, 2)

    def get_trend(self, obj):
        change = self.get_daily_change(obj)
        if change is None:
            return "neutral"
        return "up" if change > 0 else "down" if change < 0 else "neutral"


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
