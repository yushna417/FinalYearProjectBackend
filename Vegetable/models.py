from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
from datetime import date


class CustomUserManager(UserManager):
    def _create_user(self, phone, password, **extra_fields):
        if not phone:
            raise ValueError('The Phone number must be set')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone, password, **extra_fields)

    def create_superuser(self, phone=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(phone, password, **extra_fields)
    

class User(AbstractBaseUser, PermissionsMixin):
    
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
    ]
    full_name = models.CharField(max_length=255)
    phone = models.CharField(
        max_length=15,
        unique=True,)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    city = models.CharField(max_length=100)

    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateField(default=date.today)
    last_login = models.DateField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone'
    PHONE_FIELD = 'phone'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.full_name.split()[0] if self.full_name else ""



# Vegetable
class Veg(models.Model):
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=50)

# Daily Price
class DailyPrice(models.Model):
    vegetable = models.ForeignKey(Veg, on_delete=models.CASCADE)
    date = models.DateField()
    min_price = models.FloatField()
    max_price = models.FloatField()
    avg_price = models.FloatField()

# models.py - Add new models

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('vendor_accepted', 'Vendor Accepted'),
        ('customer_accepted', 'Customer Accepted'),
        ('customer_rejected', 'Customer Rejected'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
    ]

    PAYMENT_CHOICES = [
        ('qr', 'QR'),
        ('cash', 'CASH')
    ]

    customer = models.ForeignKey(User, related_name='customer_orders', on_delete=models.CASCADE)
    # Remove vendor field from Order - it will be in VendorResponse
    vegetable = models.ForeignKey(Veg, on_delete=models.CASCADE)
    quantity = models.FloatField(null=True, blank=True)
    proposed_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    delivery_charge = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_Method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, null=True, blank=True)
    order_Status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Final vendor selection (only set when customer accepts an offer)
    selected_vendor = models.ForeignKey(User, null=True, blank=True, 
                                        related_name='selected_orders', on_delete=models.SET_NULL)
    final_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    final_delivery_charge = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.vegetable.name}"

class VendorResponse(models.Model):
    RESPONSE_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('countered', 'Countered'),
        ('customer_accepted', 'Customer Accepted'),
        ('customer_rejected', 'Customer Rejected'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='vendor_responses')
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendor_responses')
    response_type = models.CharField(max_length=20, choices=RESPONSE_CHOICES, default='pending')
    
    # For counter offers
    counter_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    counter_delivery_charge = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['order', 'vendor']  # One response per vendor per order
    
    def __str__(self):
        return f"{self.vendor.full_name} - {self.response_type} - Order #{self.order.id}"

# models.py - Update Notification model
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('new_order', 'New Order'),
        ('vendor_accepted', 'Vendor Accepted'),
        ('vendor_rejected', 'Vendor Rejected'),
        ('vendor_countered', 'Vendor Countered'),
        ('customer_accepted', 'Customer Accepted Vendor'),
        ('customer_rejected', 'Customer Rejected Vendor'),
        ('order_completed', 'Order Completed'),
        ('order_expired', 'Order Expired'),
        ('multiple_offers', 'Multiple Offers Received'),
    ]    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES, null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Add fields for vendor-specific notifications
    related_vendor = models.ForeignKey(User, null=True, blank=True, 
                                       related_name='related_notifications', 
                                       on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.title} - {self.user.full_name}"

class FCMDevice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

