from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Notification



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_notifications(request):
    """Get all notifications for current user"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    notifications_data = []
    for notification in notifications:
        notifications_data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'type': notification.notification_type,
            'order_id': notification.order.id,
            'is_read': notification.is_read,
            'created_at': notification.created_at
        })
    
    return Response({'notifications': notifications_data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    return Response({'success': True, 'message': 'Notification marked as read'})