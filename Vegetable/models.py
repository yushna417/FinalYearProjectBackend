from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
from django.utils import timezone
# User model

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

    date_joined = models.DateField(default=timezone.now)
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

# Order
class Order(models.Model):
    customer = models.ForeignKey(User, related_name='customer_orders', on_delete=models.CASCADE)
    vendor = models.ForeignKey(User, related_name='vendor_orders', on_delete=models.CASCADE)
    vegetable = models.ForeignKey(Veg, on_delete=models.CASCADE)
    quantity = models.FloatField()
    price = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
