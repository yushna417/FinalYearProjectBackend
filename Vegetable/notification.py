from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Notification


# In views.py
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_notifications(request):
    """Get all notifications for the current user"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Check if unread_only parameter is provided
    unread_only = request.query_params.get('unread_only', 'false').lower() == 'true'
    if unread_only:
        notifications = notifications.filter(is_read=False)
    
    notification_data = []
    for notification in notifications:
        notification_data.append({
            'id': notification.id,
            'user': notification.user.id,
            'order': notification.order.id if notification.order else None,
            'notification_type': notification.notification_type,
            'title': notification.title,
            'message': notification.message,
            'is_read': notification.is_read,
            'created_at': notification.created_at,
        })
    
    return Response({'notifications': notification_data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id):
    """Mark a specific notification as read"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return Response({
            'success': True,
            'message': 'Notification marked as read'
        })
    except Notification.DoesNotExist:
        return Response({
            'error': 'Notification not found or not authorized'
        }, status=404)
    

