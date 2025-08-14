
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from Vegetable.views import CreateUserView, CurrentUserView, LogoutView, CustomTokenObtainPairView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import  TokenRefreshView


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
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
