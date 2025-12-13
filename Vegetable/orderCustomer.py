from .models import Order, Notification, VendorResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customer_orders(request):
    """Get all orders for the current customer with vendor responses"""
    if request.user.role != 'consumer':
        return Response({'error': 'Only customers can access this'}, status=403)
    
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    
    orders_data = []
    for order in orders:
        # Get all vendor responses for this order
        vendor_responses = VendorResponse.objects.filter(
            order=order
        ).exclude(response_type='rejected').select_related('vendor')
        
        responses_data = []
        for response in vendor_responses:
            responses_data.append({
                'vendor_id': response.vendor.id,
                'vendor_name': response.vendor.full_name,
                'vendor_phone': response.vendor.phone,
                'response_type': response.response_type,
                'counter_price': str(response.counter_price) if response.counter_price else None,
                'counter_delivery_charge': str(response.counter_delivery_charge) if response.counter_delivery_charge else None,
                'total_price': str(float(response.counter_price or 0) + float(response.counter_delivery_charge or 0)),
                'responded_at': response.created_at,
            })
        
        # Determine if customer needs to take action
        needs_action = order.order_Status == 'vendor_accepted' and len(responses_data) > 0
        
        orders_data.append({
            'id': order.id,
            'vegetable': {
                'id': order.vegetable.id,
                'name': order.vegetable.name,
                'unit': order.vegetable.unit,
            },
            'quantity': order.quantity,
            'proposed_price': str(order.proposed_price),
            'delivery_charge': str(order.delivery_charge),
            'original_total': str(float(order.proposed_price or 0) + float(order.delivery_charge or 0)),
            'location': order.location,
            'status': order.order_Status,
            'payment_method': order.payment_Method,
            'vendor_responses': responses_data,
            'selected_vendor': order.selected_vendor.full_name if order.selected_vendor else None,
            'final_price': str(order.final_price) if order.final_price else None,
            'final_delivery_charge': str(order.final_delivery_charge) if order.final_delivery_charge else None,
            'final_total': str(float(order.final_price or 0) + float(order.final_delivery_charge or 0)) if order.final_price else None,
            'needs_customer_action': needs_action,
            'response_count': len(responses_data),
            'created_at': order.created_at,
            'updated_at': order.updated_at,
        })
    
    return Response({'orders': orders_data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def customer_response(request, order_id):
    """Customer accepts or rejects a specific vendor's offer"""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    vendor_id = request.data.get('vendor_id')
    action = request.data.get('action')  # 'accept', 'reject'
    
    if action not in ['accept', 'reject']:
        return Response({'error': 'Invalid action'}, status=400)
    
    # Get the vendor's response
    vendor_response = get_object_or_404(VendorResponse, order=order, vendor_id=vendor_id)
    
    # Check if order is in correct state
    if order.order_Status not in ['pending', 'vendor_accepted']:
        return Response({'error': 'Cannot respond to this order in current state'}, status=400)
    
    # Check if vendor response is valid for acceptance
    if vendor_response.response_type not in ['accepted', 'countered']:
        return Response({'error': 'Cannot accept this vendor response'}, status=400)
    
    if action == 'accept':
        # Accept the vendor's offer
        order.order_Status = 'completed'
        order.selected_vendor = vendor_response.vendor
        order.final_price = vendor_response.counter_price or order.proposed_price
        order.final_delivery_charge = vendor_response.counter_delivery_charge or order.delivery_charge
        
        # Update vendor response
        vendor_response.response_type = 'customer_accepted'
        vendor_response.save()
        
        # Reject all other vendor responses
        other_responses = VendorResponse.objects.filter(
            order=order
        ).exclude(vendor=vendor_response.vendor)
        
        for response in other_responses:
            response.response_type = 'customer_rejected'
            response.save()
            
            # Notify other vendors
            Notification.objects.create(
                user=response.vendor,
                order=order,
                notification_type='customer_rejected',
                title='Order Given to Another Vendor',
                message=f'The customer selected another vendor for order #{order.id}'
            )
        
        # Notify selected vendor
        total_price = float(order.final_price or 0) + float(order.final_delivery_charge or 0)
        Notification.objects.create(
            user=vendor_response.vendor,
            order=order,
            notification_type='order_completed',
            title='Order Confirmed!',
            message=f'Customer accepted your offer for {order.vegetable.name}. Total: Rs :  {total_price}'
        )
        
        # Notify customer
        Notification.objects.create(
            user=order.customer,
            order=order,
            notification_type='order_completed',
            title='Order Confirmed',
            message=f'You accepted {vendor_response.vendor.full_name}\'s offer for {order.vegetable.name}'
        )
        
    elif action == 'reject':
        # Reject this specific vendor's offer
        vendor_response.response_type = 'customer_rejected'
        vendor_response.save()
        
        # Check if all vendor responses are rejected
        active_responses = VendorResponse.objects.filter(
            order=order,
            response_type__in=['accepted', 'countered']
        ).count()
        
        if active_responses == 0:
            order.order_Status = 'customer_rejected'
        
        # Notify customer
        Notification.objects.create(
            user=order.customer,
            order=order,
            notification_type='vendor_rejected',
            title='Vendor Offer Rejected',
            message=f'You rejected {vendor_response.vendor.full_name}\'s offer'
        )
    
    order.save()
    
    return Response({
        'success': True,
        'status': order.order_Status,
        'selected_vendor': order.selected_vendor.id if order.selected_vendor else None,
        'final_price': str(order.final_price) if order.final_price else None,
        'final_delivery_charge': str(order.final_delivery_charge) if order.final_delivery_charge else None,
        'message': f'Offer {action}ed successfully'
    })


# views.py - Add customer_order_detail function
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customer_order_detail(request, order_id):
    """Get detailed order info with all vendor responses for customer"""
    if request.user.role != 'customer':
        return Response({'error': 'Only customers can access this'}, status=403)
    
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    # Get all vendor responses
    vendor_responses = VendorResponse.objects.filter(
        order=order
    ).select_related('vendor').order_by('-created_at')
    
    responses_data = []
    for response in vendor_responses:
        # Calculate total for each offer
        price = response.counter_price or order.proposed_price
        delivery = response.counter_delivery_charge or order.delivery_charge
        total = float(price or 0) + float(delivery or 0) if price else 0
        
        responses_data.append({
            'vendor_id': response.vendor.id,
            'vendor_name': response.vendor.full_name,
            'vendor_phone': response.vendor.phone,
            'response_type': response.response_type,
            'price': str(price) if price else None,
            'delivery_charge': str(delivery) if delivery else None,
            'total_price': str(total),
            'responded_at': response.created_at,
            'is_selected': order.selected_vendor == response.vendor if order.selected_vendor else False,
        })
    
    # Get the best offer (lowest total price among accepted/countered responses)
    best_offer = None
    if responses_data:
        valid_offers = [r for r in responses_data if r['response_type'] in ['accepted', 'countered']]
        if valid_offers:
            best_offer = min(valid_offers, key=lambda x: float(x['total_price']))
    
    order_data = {
        'id': order.id,
        'vegetable': {
            'id': order.vegetable.id,
            'name': order.vegetable.name,
            'unit': order.vegetable.unit,
        },
        'quantity': order.quantity,
        'proposed_price': str(order.proposed_price),
        'delivery_charge': str(order.delivery_charge),
        'original_total': str(float(order.proposed_price or 0) + float(order.delivery_charge or 0)),
        'location': order.location,
        'status': order.order_Status,
        'payment_method': order.payment_Method,
        'created_at': order.created_at,
        'updated_at': order.updated_at,
        
        # Vendor offers information
        'vendor_responses': responses_data,
        'response_count': len(responses_data),
        'best_offer': best_offer,
        'needs_action': order.order_Status == 'vendor_accepted' and len(responses_data) > 0,
        
        # Final selection if made
        'selected_vendor': {
            'id': order.selected_vendor.id,
            'name': order.selected_vendor.full_name,
            'phone': order.selected_vendor.phone,
        } if order.selected_vendor else None,
        'final_price': str(order.final_price) if order.final_price else None,
        'final_delivery_charge': str(order.final_delivery_charge) if order.final_delivery_charge else None,
        'final_total': str(float(order.final_price or 0) + float(order.final_delivery_charge or 0)) if order.final_price else None,
    }
    
    return Response({
        'success': True,
        'order': order_data
    })