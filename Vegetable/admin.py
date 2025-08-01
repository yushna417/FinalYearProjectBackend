from django.contrib import admin
from .models import User, Veg, Order, DailyPrice


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'role', 'phone', 'city')


@admin.register(Veg)
class VegAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit')


@admin.register(DailyPrice)
class DailyPriceAdmin(admin.ModelAdmin):
    list_display = ('vegetable', 'date', 'min_price', 'max_price', 'avg_price')
    list_filter = ('date', 'vegetable')  # Optional filters
    search_fields = ('vegetable__name',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'vendor', 'vegetable', 'quantity', 'price', 'date')
    list_filter = ('date', 'vegetable')
    search_fields = ('customer__username', 'vendor__username', 'vegetable__name')
