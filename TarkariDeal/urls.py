
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from Vegetable.views import CreateUserView, CurrentUserView, LogoutView, CustomTokenObtainPairView, UpdateProfileImageView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import  TokenRefreshView
from Vegetable.orderCustomer import customer_order_detail, customer_orders, customer_response
from Vegetable.orderVendor import vendor_orders, vendor_response
from Vegetable.createOrder import create_order, order_detail, order_vendor_responses
from Vegetable.notification import mark_notification_read, user_notifications


def home(request):
    return render(request, "index.html")

urlpatterns = [
    path('', home),  
    path('admin/', admin.site.urls),
    path('api/', include('Vegetable.urls')),
    path('api/user/register', CreateUserView.as_view(), name="register"),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='get_token'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('api/is_loggedIn/', CurrentUserView.as_view(), name='current-user'),
    path('api/logout', LogoutView.as_view(), name='logout'),
    path('api/user/update-profile-image/', UpdateProfileImageView.as_view(), name='update-profile-image'),

    path('api/create-order/', create_order, name='create-order'),
    path('api/vendor-orders/', vendor_orders, name='vendor-orders'),
    path('api/costumer-orders/', customer_orders, name='costumer-orders'),
    path('api/orders/<int:order_id>/vendor-response/', vendor_response, name='vendor-response'),
    path('api/orders/<int:order_id>/customer-response/', customer_response, name='costumer-response'),
    path('api/orders/<int:order_id>/order-vendor-responses/', order_vendor_responses, name='order-vendor-responses'),
    path('api/orders/<int:order_id>/customer-detail/',customer_order_detail, name='customer-order-detail'),
    
    # Notifications
    path('api/notifications/', user_notifications, name='user-notifications'),
    path('api/notifications/<int:notification_id>/mark-read/', mark_notification_read, name='mark-notification-read'),
    
    # Order Details
    path('api/order/<int:order_id>/', order_detail, name='order-detail'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


