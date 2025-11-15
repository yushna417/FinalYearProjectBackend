
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from Vegetable.views import CreateUserView, CurrentUserView, LogoutView, CustomTokenObtainPairView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import  TokenRefreshView
from Vegetable.orderCustomer import consumer_orders, consumer_response
from Vegetable.orderVendor import vendor_orders, vendor_response
from Vegetable.createOrder import create_order, order_detail
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

    path('create-order/', create_order, name='create-order'),
    path('vendor-orders/', vendor_orders, name='vendor-orders'),
    path('consumer-orders/', consumer_orders, name='consumer-orders'),
    path('order/<int:order_id>/vendor-response/', vendor_response, name='vendor-response'),
    path('order/<int:order_id>/consumer-response/', consumer_response, name='consumer-response'),
    
    # Notifications
    path('notifications/', user_notifications, name='user-notifications'),
    path('notifications/<int:notification_id>/mark-read/', mark_notification_read, name='mark-notification-read'),
    
    # Order Details
    path('order/<int:order_id>/', order_detail, name='order-detail'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


