"""
Cart app views - Shopping cart management.
"""
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from apps.products.models import Product
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer


class CartViewSet(viewsets.ViewSet):
    """
    ViewSet for shopping cart management.
    
    Features:
    - View user's cart
    - Add/remove items
    - Update quantities
    - Clear cart
    - Stock validation
    """
    permission_classes = [IsAuthenticated]
    
    def get_user_cart(self, user):
        """Get or create cart for user."""
        cart, created = Cart.objects.get_or_create(user=user)
        return cart
    
    def list(self, request):
        """Get current user's cart."""
        cart = self.get_user_cart(request.user)
        serializer = CartSerializer(cart)
        return Response({
            'success': True,
            'message': 'Cart retrieved successfully',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def add(self, request):
        """
        Add product to cart.
        
        Request body:
        - product_id: ID of product to add (required)
        - quantity: Number of items to add (default: 1)
        """
        cart = self.get_user_cart(request.user)
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        
        if not product_id:
            return Response(
                {'success': False, 'message': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                return Response(
                    {'success': False, 'message': 'Quantity must be at least 1'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return Response(
                {'success': False, 'message': 'Invalid quantity value'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response(
                {'success': False, 'message': 'Product not found or inactive'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check stock
        if product.stock_quantity < quantity:
            return Response({
                'success': False,
                'message': f'Insufficient stock. Available: {product.stock_quantity}',
                'data': {'available': product.stock_quantity}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Add or update cart item
        try:
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product
            )
            
            if not created:
                # Update quantity if item already in cart
                new_quantity = cart_item.quantity + quantity
                if new_quantity > product.stock_quantity:
                    return Response({
                        'success': False,
                        'message': f'Cannot add more items. Total would exceed stock.',
                        'data': {'available': product.stock_quantity}
                    }, status=status.HTTP_400_BAD_REQUEST)
                cart_item.quantity = new_quantity
            
            cart_item.save()
            serializer = CartSerializer(cart)
            return Response({
                'success': True,
                'message': 'Item added to cart' if created else 'Item quantity updated',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        
        except ValueError as e:
            return Response(
                {'success': False, 'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['put'], url_path='items/(?P<item_id>[^/.]+)')
    def update_item(self, request, item_id=None):
        """
        Update quantity of cart item.
        
        Request body:
        - quantity: New quantity (required)
        """
        cart = self.get_user_cart(request.user)
        quantity = request.data.get('quantity')
        
        if not quantity:
            return Response(
                {'success': False, 'message': 'Quantity is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                return Response(
                    {'success': False, 'message': 'Quantity must be at least 1'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return Response(
                {'success': False, 'message': 'Invalid quantity value'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        # Check stock
        if quantity > cart_item.product.stock_quantity:
            return Response({
                'success': False,
                'message': f'Insufficient stock. Available: {cart_item.product.stock_quantity}',
                'data': {'available': cart_item.product.stock_quantity}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        cart_item.quantity = quantity
        cart_item.save()
        
        serializer = CartSerializer(cart)
        return Response({
            'success': True,
            'message': 'Item quantity updated',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['delete'], url_path='items/(?P<item_id>[^/.]+)')
    def remove_item(self, request, item_id=None):
        """Remove item from cart."""
        cart = self.get_user_cart(request.user)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        cart_item.delete()
        
        serializer = CartSerializer(cart)
        return Response({
            'success': True,
            'message': 'Item removed from cart',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """Clear all items from cart."""
        cart = self.get_user_cart(request.user)
        cart.clear()
        
        serializer = CartSerializer(cart)
        return Response({
            'success': True,
            'message': 'Cart cleared successfully',
            'data': serializer.data
        })
