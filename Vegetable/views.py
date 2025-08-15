from rest_framework import viewsets, generics, status
from .models import User, Veg, DailyPrice, Order
from .serializers import UserSerializer, VegSerializer, DailyPriceSerializer, OrderSerializer
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken 
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import OuterRef, Subquery, F, FloatField, Case, When, DateField
from django.db.models.functions import Cast


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
class VegViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Veg.objects.all()
    serializer_class = VegSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['name']
    search_fields = ['name']

class DailyPriceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DailyPrice.objects.all()

    serializer_class = DailyPriceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['vegetable']
    ordering_fields = ['date']
    ordering = ['-date']

    def get_queryset(self):
        queryset = DailyPrice.objects.all()

        previous_price_subquery = DailyPrice.objects.filter(
            vegetable=OuterRef('vegetable'),
            date__lt=OuterRef('date')
        ).order_by('-date').values('avg_price')[:1]

        previous_date_subquery = DailyPrice.objects.filter(
            vegetable=OuterRef('vegetable'),
            date__lt=OuterRef('date')
        ).order_by('-date').values('date')[:1]

        queryset = queryset.annotate(
            previous_date=Subquery(previous_date_subquery, output_field=DateField()),
            previous_price=Subquery(previous_price_subquery),
            daily_change_percentage=Case(
                When(
                    previous_price__isnull=False,
                    then=((F('avg_price') - F('previous_price')) / F('previous_price')) * 100
                ),
                default=None,
                output_field=FloatField()
            )
        )
        return queryset

    @action(detail=False, methods=['get'])
    def with_daily_change(self, request):
        queryset = self.filter_queryset(self.get_queryset()).order_by('-date')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

class OrderListView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the refresh token
            return Response({"detail": "Successfully logged out."})
        except Exception as e:
            return Response({"error": "Invalid token or token missing."}, status=400)
    

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = TokenObtainPairSerializer(data = request.data)
        try:
            serializer.is_valid(raise_exception=True)

        except Exception as e:
            return Response ({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        token_data = serializer.validated_data
        user = serializer.user

        token_data['role'] = user.role

        return Response(token_data, status=status.HTTP_200_OK)