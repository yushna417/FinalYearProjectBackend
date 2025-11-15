from .models import Order, Notification
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def consumer_orders(request):
    """Get all orders for the current consumer"""
    if request.user.role != 'consumer':
        return Response({'error': 'Only consumers can access this'}, status=403)
    
    orders = Order.objects.filter(consumer=request.user).order_by('-created_at')
    
    orders_data = []
    for order in orders:
        order_data = {
            'id': order.id,
            'vegetable_name': order.vegetable_name,
            'quantity': order.quantity,
            'proposed_price': str(order.proposed_price),
            'counter_price': str(order.counter_price) if order.counter_price else None,
            'final_price': str(order.final_price) if order.final_price else None,
            'location': order.location,
            'status': order.status,
            'vendor_name': order.vendor.username if order.vendor else None,
            'created_at': order.created_at,
            'updated_at': order.updated_at
        }
        orders_data.append(order_data)
    
    return Response({'orders': orders_data})

@api_view(['POST'])
def consumer_response(request, order_id):
    order = get_object_or_404(Order, id=order_id, consumer=request.user)
    action = request.data.get('action')  # 'accept_counter', 'reject_counter'
    
    if action == 'accept_counter' and order.status == 'countered':
        order.status = 'accepted'
        order.final_price = order.counter_price
        
        # Notify vendor
        Notification.objects.create(
            user=order.vendor,
            order=order,
            notification_type='accepted',
            title='Counter Offer Accepted!',
            message=f'Consumer accepted your counter offer for {order.vegetable_name}'
        )
        
    elif action == 'reject_counter' and order.status == 'countered':
        order.status = 'rejected'
        
        # Notify vendor
        Notification.objects.create(
            user=order.vendor,
            order=order,
            notification_type='rejected', 
            title='Counter Offer Rejected',
            message=f'Consumer rejected your counter offer for {order.vegetable_name}'
        )
    
    order.save()
    
    return Response({'success': True, 'status': order.status})