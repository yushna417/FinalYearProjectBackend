
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from Vegetable.views import CreateUserView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


def home(request):
    return render(request, "index.html")

urlpatterns = [
    path('', home),  # Root route (127.0.0.1:8000/)
    path('admin/', admin.site.urls),
    path('api/', include('Vegetable.urls')),
    path('api/user/register', CreateUserView.as_view(), name="register"),
    path('api/token/', TokenObtainPairView.as_view(), name='get_token'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('api-auth/', include('rest_framework.urls'))
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
