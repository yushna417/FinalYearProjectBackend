from .models import Order, Notification
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vendor_orders(request):
    """Get all pending orders for vendors"""
    if request.user.role != 'vendor':
        return Response({'error': 'Only vendors can access this'}, status=403)
    
    # Get all pending orders (not assigned to any vendor yet)
    pending_orders = Order.objects.filter(
        status='pending'
    ).exclude(
        vendor=request.user  # Exclude orders already responded to by this vendor
    )
    
    orders_data = []
    for order in pending_orders:
        orders_data.append({
            'id': order.id,
            'vegetable_name': order.vegetable_name,
            'quantity': order.quantity,
            'proposed_price': str(order.proposed_price),
            'location': order.location,
            'consumer_name': order.consumer.username,
            'created_at': order.created_at
        })
    
    return Response({'orders': orders_data})


@api_view(['POST'])
def vendor_response(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    action = request.data.get('action')  # 'accept', 'reject', 'counter'
    counter_price = request.data.get('counter_price')
    
    if action == 'accept':
        order.status = 'accepted'
        order.vendor = request.user
        order.final_price = order.proposed_price
        
        # Notify consumer
        Notification.objects.create(
            user=order.consumer,
            order=order,
            notification_type='accepted',
            title='Order Accepted!',
            message=f'Your order for {order.vegetable_name} has been accepted'
        )
        
    elif action == 'reject':
        order.status = 'rejected'
        order.vendor = request.user
        
        # Notify consumer
        Notification.objects.create(
            user=order.consumer,
            order=order,
            notification_type='rejected',
            title='Order Rejected',
            message=f'Your order for {order.vegetable_name} was rejected'
        )
        
    elif action == 'counter' and counter_price:
        order.status = 'countered'
        order.vendor = request.user
        order.counter_price = counter_price
        
        # Notify consumer
        Notification.objects.create(
            user=order.consumer,
            order=order,
            notification_type='counter_offer',
            title='Counter Offer Received',
            message=f'Counter offer for {order.vegetable_name}: ${counter_price}'
        )
    
    order.save()
    
    return Response({
        'success': True,
        'status': order.status,
        'message': f'Order {action}ed successfully'
    })
