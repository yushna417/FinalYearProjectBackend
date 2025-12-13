from .models import Order, Notification, VendorResponse
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
    
    # Get pending orders where this vendor hasn't responded yet
    pending_orders = Order.objects.filter(
        order_Status='pending'
    ).exclude(
        vendor_responses__vendor=request.user  # Exclude orders this vendor has already responded to
    ).select_related('vegetable', 'customer')
    
    # Get orders where this vendor has responded (for tracking)
    my_responses = VendorResponse.objects.filter(
        vendor=request.user
    ).select_related('order', 'order__vegetable', 'order__customer')
    
    orders_data = []
    
    # New orders to respond to
    for order in pending_orders:
        # Count how many vendors have responded
        response_count = VendorResponse.objects.filter(order=order).count()
        
        orders_data.append({
            'type': 'new_order',
            'id': order.id,
            'vegetable': {
                'id': order.vegetable.id,
                'name': order.vegetable.name,
                'unit': order.vegetable.unit,
            },
            'quantity': order.quantity,
            'proposed_price': str(order.proposed_price),
            'delivery_charge': str(order.delivery_charge),
            'total_price': str(float(order.proposed_price or 0) + float(order.delivery_charge or 0)),
            'location': order.location,
            'customer': order.customer.full_name,
            'payment_method': order.payment_Method,
            'status': order.order_Status,
            'response_count': response_count,
            'created_at': order.created_at,
            'needs_action': True,
        })
    
    # My responses
    for response in my_responses:
        order = response.order
        orders_data.append({
            'type': 'my_response',
            'id': order.id,
            'vegetable': {
                'id': order.vegetable.id,
                'name': order.vegetable.name,
            },
            'quantity': order.quantity,
            'proposed_price': str(order.proposed_price),
            'delivery_charge': str(order.delivery_charge),
            'my_response_type': response.response_type,
            'my_counter_price': str(response.counter_price) if response.counter_price else None,
            'my_counter_delivery': str(response.counter_delivery_charge) if response.counter_delivery_charge else None,
            'customer': order.customer.full_name,
            'order_status': order.order_Status,
            'created_at': response.created_at,
            'updated_at': response.updated_at,
            'needs_action': False,
        })
    
    return Response({'orders': orders_data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def vendor_response(request, order_id):
    """Handle vendor response to an order - ONE customer, MULTIPLE vendors"""
    order = get_object_or_404(Order, id=order_id)
    action = request.data.get('action')  # 'accept', 'reject', 'counter'
    counter_price = request.data.get('counter_price')
    counter_delivery_charge = request.data.get('counter_delivery_charge')
    
    if request.user.role != 'vendor':
        return Response({'error': 'Only vendors can respond to orders'}, status=403)
    
    if action not in ['accept', 'reject', 'counter']:
        return Response({'error': 'Invalid action'}, status=400)
    
    # Check if order is still pending
    if order.order_Status not in ['pending', 'vendor_accepted']:
        return Response({'error': 'Order is no longer pending'}, status=400)
    
    # Check if vendor already responded
    existing_response = VendorResponse.objects.filter(order=order, vendor=request.user).first()
    if existing_response:
        return Response({'error': 'You have already responded to this order'}, status=400)
    
    # For counter action, validation
    if action == 'counter':
        if not counter_price:
            return Response({'error': 'Counter price is required'}, status=400)
        if counter_delivery_charge is None:
            counter_delivery_charge = order.delivery_charge
    
    # Create vendor response
    if action == 'accept':
        response_type = 'accepted'
        counter_price = order.proposed_price
        counter_delivery_charge = order.delivery_charge
        
    elif action == 'reject':
        response_type = 'rejected'
        
    elif action == 'counter':
        response_type = 'countered'
    
    # Create vendor response
    vendor_response = VendorResponse.objects.create(
        order=order,
        vendor=request.user,
        response_type=response_type,
        counter_price=counter_price,
        counter_delivery_charge=counter_delivery_charge
    )
    
    # Count responses
    total_responses = VendorResponse.objects.filter(order=order).count()
    valid_responses = VendorResponse.objects.filter(
        order=order,
        response_type__in=['accepted', 'countered']
    ).count()
    rejected_responses = VendorResponse.objects.filter(
        order=order,
        response_type='rejected'
    ).count()
    
    # Update order status if it's the first valid response
    if order.order_Status == 'pending' and action != 'reject' and valid_responses == 1:
        order.order_Status = 'vendor_accepted'
        order.save()
    
    # NOTIFICATION MANAGEMENT - SINGLE NOTIFICATION PER ORDER
    
    # Check if notification already exists for this order
    existing_notification = Notification.objects.filter(
        user=order.customer,
        order=order,
        notification_type__in=['vendor_responses', 'new_offers']
    ).order_by('-created_at').first()
    
    if existing_notification:
        # Update existing notification
        existing_notification.title = f'You have {valid_responses} offer(s) for your order'
        existing_notification.message = f'{valid_responses} vendor(s) have made offers. {rejected_responses} vendor(s) declined.'
        existing_notification.is_read = False
        existing_notification.save()
        
        # Also create a brief update notification (optional, can be skipped)
        # Notification.objects.create(
        #     user=order.customer,
        #     order=order,
        #     notification_type='vendor_response_update',
        #     title='New Vendor Response',
        #     message=f'{request.user.full_name} {action}ed your order.',
        #     related_vendor=request.user,
        #     is_read=True  # Mark as secondary/read
        # )
    else:
        # Create first notification for this order
        if action == 'reject':
            # For first response being a rejection
            notification_type = 'vendor_rejected'
            title = 'Vendor Declined Your Order'
            message = f'{request.user.full_name} declined your order.'
        else:
            # For first valid response
            notification_type = 'vendor_responses'
            title = f'You have {valid_responses} offer(s) for your order'
            message = f'{request.user.full_name} {action}ed your order.'
        
        Notification.objects.create(
            user=order.customer,
            order=order,
            notification_type=notification_type,
            title=title,
            message=message,
            related_vendor=request.user
        )
    
    # Notify vendor about their response
    Notification.objects.create(
        user=request.user,
        order=order,
        notification_type='response_sent',
        title='Response Recorded',
        message=f'Your {action} response has been recorded.',
        is_read=True
    )
    
    return Response({
        'success': True,
        'message': 'Response submitted successfully.',
        'response_id': vendor_response.id,
        'response_type': vendor_response.response_type,
        'offer_count': valid_responses,
        'total_responses': total_responses
    })
