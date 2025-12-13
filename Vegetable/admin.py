from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import (
    User, Veg, DailyPrice, Order, VendorResponse,
    Notification, FCMDevice
)

# =====================================================
# Custom User Admin
# =====================================================
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['phone', 'full_name', 'role', 'city', 'is_active', 'is_superuser']
    list_filter = ('role', 'city', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('phone', 'full_name')

    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        (_('Personal Info'), {'fields': ('full_name', 'role', 'profile_image', 'city')}),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
        (_('Important Dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'phone', 'full_name', 'role',
                'password1', 'password2',
                'is_staff', 'is_superuser'
            ),
        }),
    )


# =====================================================
# Vegetable Admin
# =====================================================
@admin.register(Veg)
class VegAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit')
    search_fields = ('name',)
    list_filter = ('unit',)


# =====================================================
# Daily Price Admin
# =====================================================
@admin.register(DailyPrice)
class DailyPriceAdmin(admin.ModelAdmin):
    list_display = ('vegetable', 'date', 'min_price', 'max_price', 'avg_price')
    list_filter = ('vegetable', 'date')
    search_fields = ('vegetable__name',)
    date_hierarchy = 'date'


# =====================================================
# Order Admin
# =====================================================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'customer',
        'vegetable',
        'quantity',
        'proposed_price',
        'final_price',
        'delivery_charge',
        'final_delivery_charge',
        'location',
        'order_Status',
        'payment_Method',
        'selected_vendor',
        'created_at'
    )

    list_filter = (
        'order_Status',
        'payment_Method',
        'vegetable',
        'created_at',
        'selected_vendor'
    )

    search_fields = (
        'customer__phone',
        'customer__full_name',
        'vegetable__name',
        'selected_vendor__phone',
        'selected_vendor__full_name',
    )

    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')


# =====================================================
# Vendor Response Admin (NEW)
# =====================================================
@admin.register(VendorResponse)
class VendorResponseAdmin(admin.ModelAdmin):
    list_display = (
        'order',
        'vendor',
        'response_type',
        'counter_price',
        'counter_delivery_charge',
        'created_at'
    )

    list_filter = ('response_type', 'created_at')
    search_fields = (
        'vendor__phone',
        'vendor__full_name',
        'order__id',
        'order__vegetable__name'
    )

    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')


# =====================================================
# Notification Admin
# =====================================================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'order',
        'related_vendor',
        'notification_type',
        'title',
        'is_read',
        'created_at'
    )

    search_fields = ('user__phone', 'title', 'related_vendor__phone')
    list_filter = ('notification_type', 'is_read', 'created_at')
    date_hierarchy = 'created_at'


# =====================================================
# FCM Device Admin
# =====================================================
@admin.register(FCMDevice)
class FCMDeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at')
    search_fields = ('user__phone', 'token')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)


# =====================================================
# Admin Branding
# =====================================================
admin.site.site_header = "TarkariDeal Admin"
admin.site.site_title = "TarkariDeal"
admin.site.index_title = "Welcome to TarkariDeal Admin"
