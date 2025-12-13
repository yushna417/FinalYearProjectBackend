from .models import User, Order, Notification, FCMDevice, Veg, VendorResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from firebase_config import send_push_notification  

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Added permission decorator
def create_order(request):
    data = request.data
    
    # Validate required fields
    required_fields = ['vegetable_id', 'quantity', 'proposed_price', 'location', 'payment_Method']
    for field in required_fields:
        if field not in data:
            return Response({'error': f'{field} is required'}, status=400)
    
    # Get the vegetable object from the ID
    try:
        vegetable = Veg.objects.get(id=data['vegetable_id'])
    except Veg.DoesNotExist:
        return Response({'error': 'Vegetable not found'}, status=404)
    
    # Create order with correct field names
    order = Order.objects.create(
        customer=request.user,  # Changed from 'costumer' to 'customer'
        vegetable=vegetable,
        quantity=data['quantity'],
        proposed_price=data['proposed_price'],
        location=data['location'],
        payment_Method=data['payment_Method'],
        order_Status='pending',  # Add initial status
        delivery_charge=data.get('delivery_charge', 0),  # Optional field
    )
    notification_ids = []
    # Notify vendors (you might want to filter by location/availability)
    vendors = User.objects.filter(role='vendor')
    
    for vendor in vendors:
        # Create notification for each vendor
        notification = Notification.objects.create(
            user=vendor,
            order=order,
            notification_type='new_order',
            title='New Vegetable Order',
            message=f' {vegetable.name} - {order.quantity} kg'  # Use vegetable.name
        )

        notification_ids.append(notification.id)
        
        # Send push notifications
        devices = FCMDevice.objects.filter(user=vendor)
        
        for device in devices:
            send_push_notification(
                device.token,
                "New Vegetable Order",
                f"{vegetable.name} - {order.quantity}kg available"
            )
            
    return Response({
        'success': True,
        'order_id': order.id,
        'notification_ids': notification_ids, 
        'message': 'Order created and vendors notified',
        'data': {
            'id': order.id,
            'customer_id': order.customer.id,
            'vegetable_id': order.vegetable.id,
            'vegetable_name': order.vegetable.name,
            'quantity': order.quantity,
            'proposed_price': str(order.proposed_price),
            'status': order.order_Status
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    """Get detailed information about a specific order"""
    order = get_object_or_404(Order, id=order_id)
    
    # Authorization logic updated for multi-vendor system
    if request.user.role == 'consumer':
        # Consumer can only view their own orders
        if order.customer != request.user:
            return Response({'error': 'Not authorized to view this order'}, status=403)
    
    elif request.user.role == 'vendor':
        # Vendor can view:
        # 1. Pending orders (to potentially respond)
        # 2. Orders they have responded to (for tracking)
        
        # Check if vendor has responded to this order
        has_responded = VendorResponse.objects.filter(
            order=order, 
            vendor=request.user
        ).exists()
        
        # Vendor can view if:
        # 1. Order is pending (they might want to respond)
        # 2. They have responded to it (to see their response)
        # 3. They are the selected vendor (for completed orders)
        
        # can_view = (
        #     order.order_Status == 'pending' or
        #     has_responded or
        #     order.selected_vendor == request.user
        # )
        
        # if not can_view:
        #     return Response({'error': 'Not authorized to view this order'}, status=403)
    
    else:
        # Other roles (admin, etc.)
        return Response({'error': 'Not authorized'}, status=403)
    
    # Check if current vendor has responded and get their response
    vendor_response = None
    vendor_has_responded = False
    if request.user.role == 'vendor':
        vendor_response = VendorResponse.objects.filter(
            order=order, 
            vendor=request.user
        ).first()
        vendor_has_responded = vendor_response is not None
    
    # Get response count (how many vendors have responded)
    response_count = VendorResponse.objects.filter(order=order).exclude(
        response_type='rejected'
    ).count()
    
    # Check if this vendor is selected
    is_selected_vendor = order.selected_vendor == request.user if request.user.role == 'vendor' else False
    
    # Get all vendor responses (for customer view or selected vendor)
    vendor_responses = []
    if request.user.role == 'consumer' or is_selected_vendor:
        responses = VendorResponse.objects.filter(order=order).select_related('vendor')
        vendor_responses = [
            {
                'vendor_id': r.vendor.id,
                'vendor_name': r.vendor.full_name,
                'vendor_phone': r.vendor.phone,
                'response_type': r.response_type,
                'counter_price': str(r.counter_price) if r.counter_price else None,
                'counter_delivery_charge': str(r.counter_delivery_charge) if r.counter_delivery_charge else None,
                'responded_at': r.created_at,
            }
            for r in responses
        ]
    
    # Build response data
    order_data = {
        'id': order.id,
        'vegetable': {
            'id': order.vegetable.id if order.vegetable else None,
            'name': order.vegetable.name if order.vegetable else None,
            'unit': str(order.vegetable.unit) if order.vegetable else None,
        } if order.vegetable else None,
        'quantity': order.quantity,
        'proposed_price': str(order.proposed_price),
        'delivery_charge': str(order.delivery_charge) if order.delivery_charge else None,
        'original_total': str(float(order.proposed_price or 0) + float(order.delivery_charge or 0)),
        'location': order.location,
        'status': order.order_Status,
        'payment_method': order.payment_Method,
        'customer_id': order.customer.id if order.customer else None,
        'customer_name': order.customer.full_name if order.customer else None,
        'customer_phone': order.customer.phone if order.customer else None,
        'selected_vendor_id': order.selected_vendor.id if order.selected_vendor else None,
        'selected_vendor_name': order.selected_vendor.full_name if order.selected_vendor else None,
        'final_price': str(order.final_price) if order.final_price else None,
        'final_delivery_charge': str(order.final_delivery_charge) if order.final_delivery_charge else None,
        'final_total': str(float(order.final_price or 0) + float(order.final_delivery_charge or 0)) if order.final_price else None,
        'created_at': order.created_at,
        'updated_at': order.updated_at,
        
        # Vendor-specific data
        'has_responded': vendor_has_responded,
        'my_response_type': vendor_response.response_type if vendor_response else None,
        'my_counter_price': str(vendor_response.counter_price) if vendor_response and vendor_response.counter_price else None,
        'my_counter_delivery_charge': str(vendor_response.counter_delivery_charge) if vendor_response and vendor_response.counter_delivery_charge else None,
        'my_response_id': vendor_response.id if vendor_response else None,
        'is_selected_vendor': is_selected_vendor,
        
        # Response statistics
        'response_count': response_count,
        'total_vendor_responses': VendorResponse.objects.filter(order=order).count(),
        
        # All vendor responses (for customer or selected vendor)
        'vendor_responses': vendor_responses if vendor_responses else None,
    }
    
    return Response({
        'success': True,
        'order': order_data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_vendor_responses(request, order_id):
    """Get all vendor responses for a specific order"""
    order = get_object_or_404(Order, id=order_id)
    
    # Check permissions
    if request.user.role == 'vendor':
        # Vendor can only see their own response and if they're selected
        if order.selected_vendor != request.user:
            return Response({'error': 'Not authorized'}, status=403)
    elif request.user.role == 'consumer':
        # Customer can see all responses to their order
        if order.customer != request.user:
            return Response({'error': 'Not authorized'}, status=403)
    else:
        return Response({'error': 'Not authorized'}, status=403)
    
    responses = VendorResponse.objects.filter(
        order=order
    ).select_related('vendor').order_by('-created_at')
    
    responses_data = []
    for response in responses:
        responses_data.append({
            'vendor_id': response.vendor.id,
            'vendor_name': response.vendor.full_name,
            'vendor_phone': response.vendor.phone,
            'response_type': response.response_type,
            'counter_price': str(response.counter_price) if response.counter_price else None,
            'counter_delivery_charge': str(response.counter_delivery_charge) if response.counter_delivery_charge else None,
            'total': str(float(response.counter_price or 0) + float(response.counter_delivery_charge or 0)),
            'created_at': response.created_at,
            'updated_at': response.updated_at,
        })
    
    return Response({
        'order_id': order.id,
        'order_status': order.order_Status,
        'selected_vendor_id': order.selected_vendor.id if order.selected_vendor else None,
        'responses': responses_data,
        'count': len(responses_data)
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def save_fcm_token(request):
    token = request.data.get("token")

    if not token:
        return Response({"error": "Token missing"}, status=400)

    FCMDevice.objects.update_or_create(
        user=request.user,
        defaults={'token': token}  # Added defaults parameter
    )

    return Response({"success": True})