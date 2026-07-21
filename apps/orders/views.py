"""
Orders app views - Order management and checkout.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.shortcuts import get_object_or_404
from decimal import Decimal

from apps.cart.models import Cart, CartItem
from apps.core.permissions import IsOwnerOrAdmin
from apps.products.models import Product
from .models import Order, OrderItem, OrderStatusHistory
from .serializers import (
    OrderListSerializer, OrderDetailSerializer, CheckoutSerializer,
    OrderUpdateSerializer, OrderStatusHistorySerializer
)


class OrderViewSet(viewsets.ViewSet):
    """
    ViewSet for order management.
    
    Features:
    - List user's orders
    - Retrieve order details
    - Checkout (convert cart to order) with transaction safety
    - Admin order management
    - Order status tracking
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get orders for authenticated user."""
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)
    
    def list(self, request):
        """Get user's orders."""
        orders = self.get_queryset()
        serializer = OrderListSerializer(orders, many=True)
        
        return Response({
            'success': True,
            'message': 'Orders retrieved successfully',
            'data': serializer.data,
            'count': orders.count()
        })
    
    def retrieve(self, request, pk=None):
        """Get order details."""
        order = get_object_or_404(self.get_queryset(), id=pk)
        serializer = OrderDetailSerializer(order)
        
        return Response({
            'success': True,
            'message': 'Order retrieved successfully',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """
        Checkout: Convert cart items to order.
        
        Features:
        - Atomic transaction (all or nothing)
        - Stock reduction
        - Order creation with items
        - Cart clearing
        
        Request body:
        - shipping_address: Full address
        - shipping_city: City
        - shipping_postal_code: Postal code
        - shipping_country: Country
        - shipping_cost: (optional) Shipping cost
        - tax: (optional) Tax amount
        """
        serializer = CheckoutSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Checkout failed',
                'data': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Use database transaction to ensure atomicity
            with transaction.atomic():
                # Get user cart
                cart = Cart.objects.get(user=request.user)
                
                if not cart.items.exists():
                    return Response({
                        'success': False,
                        'message': 'Cart is empty'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Calculate totals
                subtotal = Decimal(str(cart.subtotal))
                shipping_cost = Decimal(str(serializer.validated_data.get('shipping_cost', 0)))
                tax = Decimal(str(serializer.validated_data.get('tax', 0)))
                total_amount = subtotal + shipping_cost + tax
                
                # Create order
                order = Order.objects.create(
                    user=request.user,
                    status=Order.OrderStatus.PENDING,
                    shipping_address=serializer.validated_data['shipping_address'],
                    shipping_city=serializer.validated_data['shipping_city'],
                    shipping_postal_code=serializer.validated_data['shipping_postal_code'],
                    shipping_country=serializer.validated_data['shipping_country'],
                    subtotal=subtotal,
                    shipping_cost=shipping_cost,
                    tax=tax,
                    total_amount=total_amount
                )
                
                # Create order items and reduce stock
                for cart_item in cart.items.select_related('product').all():
                    product = Product.objects.select_for_update().get(id=cart_item.product_id)
                    
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=cart_item.quantity,
                        price_at_purchase=product.display_price
                    )
                    
                    # Reduce product stock
                    product.reduce_stock(cart_item.quantity)
                
                # Log order creation
                OrderStatusHistory.objects.create(
                    order=order,
                    from_status=None,
                    to_status=Order.OrderStatus.PENDING,
                    note='Order created'
                )
                
                # Clear cart
                cart.clear()
                
                serializer = OrderDetailSerializer(order)
                return Response({
                    'success': True,
                    'message': 'Order created successfully',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
        
        except Cart.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User cart not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Checkout failed: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path='(?P<order_id>[^/.]+)/update-status')
    def update_status(self, request, order_id=None):
        """
        Update order status (admin only).
        
        Request body:
        - status: New status (pending, paid, shipped, delivered, cancelled)
        - note: Optional note about status change
        """
        if not request.user.is_staff:
            return Response({
                'success': False,
                'message': 'Only admin can update order status'
            }, status=status.HTTP_403_FORBIDDEN)
        
        order = get_object_or_404(Order, id=order_id)
        new_status = request.data.get('status')
        note = request.data.get('note', '')
        
        if not new_status:
            return Response({
                'success': False,
                'message': 'Status is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate status
        valid_statuses = [choice[0] for choice in Order.OrderStatus.choices]
        if new_status not in valid_statuses:
            return Response({
                'success': False,
                'message': f'Invalid status. Valid options: {", ".join(valid_statuses)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        old_status = order.status
        order.status = new_status
        order.save()
        
        # Log status change
        OrderStatusHistory.objects.create(
            order=order,
            from_status=old_status,
            to_status=new_status,
            note=note
        )
        
        serializer = OrderDetailSerializer(order)
        return Response({
            'success': True,
            'message': 'Order status updated',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['post'], url_path='(?P<order_id>[^/.]+)/cancel')
    def cancel_order(self, request, order_id=None):
        """Cancel an order (if still pending)."""
        order = get_object_or_404(self.get_queryset(), id=order_id)
        
        if not order.can_cancel():
            return Response({
                'success': False,
                'message': f'Cannot cancel order with status: {order.status}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            order.cancel()
            serializer = OrderDetailSerializer(order)
            return Response({
                'success': True,
                'message': 'Order cancelled successfully',
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Failed to cancel order: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='(?P<order_id>[^/.]+)/status-history')
    def status_history(self, request, order_id=None):
        """Get order status change history."""
        order = get_object_or_404(self.get_queryset(), id=order_id)
        history = order.status_history.all()
        
        serializer = OrderStatusHistorySerializer(history, many=True)
        return Response({
            'success': True,
            'message': 'Order status history retrieved',
            'data': serializer.data
        })
