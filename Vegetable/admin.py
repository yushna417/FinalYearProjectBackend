from django.contrib import admin
from .models import User, Veg, Order, DailyPrice
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['phone', 'full_name', 'role', 'is_superuser']
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        (_('Personal info'), {'fields': ('full_name', 'role', 'profile_image', 'city')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'full_name', 'role', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )
    search_fields = ('phone', 'full_name')
    USERNAME_FIELD = 'phone'


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
