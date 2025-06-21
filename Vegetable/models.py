from django.db import models
from django.contrib.auth.models import AbstractUser

# User model
class User(AbstractUser):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
    ]
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    city = models.CharField(max_length=100)


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

# Order
class Order(models.Model):
    customer = models.ForeignKey(User, related_name='customer_orders', on_delete=models.CASCADE)
    vendor = models.ForeignKey(User, related_name='vendor_orders', on_delete=models.CASCADE)
    vegetable = models.ForeignKey(Veg, on_delete=models.CASCADE)
    quantity = models.FloatField()
    price = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
