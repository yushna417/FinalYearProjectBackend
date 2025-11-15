from .models import User, Order, Notification
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
    

@api_view(['POST'])
def create_order(request):
    data = request.data
    
    # Create order
    order = Order.objects.create(
        consumer=request.user,
        vegetable_name=data['vegetable_name'],
        quantity=data['quantity'],
        proposed_price=data['proposed_price'],
        location=data['location']
    )
    
    vendors = User.objects.filter(role='vendor')
    
    for vendor in vendors:
        # Create notification for each vendor
        Notification.objects.create(
            user=vendor,
            order=order,
            notification_type='new_order',
            title='New Vegetable Order',
            message=f'New order for {order.vegetable_name} - {order.quantity}'
        )
        
        # Send push notification (you'll implement this)
        send_push_notification(vendor, 'New Order!', f'{order.vegetable_name} - {order.quantity}')
    
    return Response({
        'success': True,
        'order_id': order.id,
        'message': 'Order created and vendors notified'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    """Get detailed information about a specific order"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.user.role == 'consumer' and order.consumer != request.user:
        return Response({'error': 'Not authorized to view this order'}, status=403)
    elif request.user.role == 'vendor' and order.vendor != request.user and order.status == 'pending':
        return Response({'error': 'Not authorized to view this order'}, status=403)
    
    order_data = {
        'id': order.id,
        'vegetable_name': order.vegetable_name,
        'quantity': order.quantity,
        'proposed_price': str(order.proposed_price),
        'counter_price': str(order.counter_price) if order.counter_price else None,
        'final_price': str(order.final_price) if order.final_price else None,
        'location': order.location,
        'status': order.status,
        'consumer_name': order.consumer.username,
        'vendor_name': order.vendor.username if order.vendor else None,
        'created_at': order.created_at,
        'updated_at': order.updated_at
    }
    
    return Response({'order': order_data})