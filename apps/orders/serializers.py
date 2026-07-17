"""
Orders app serializers.
"""
from rest_framework import serializers
from decimal import Decimal
from .models import Order, OrderItem, OrderStatusHistory
from apps.products.serializers import ProductListSerializer
from apps.cart.models import Cart


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items."""
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True, required=False)
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_id', 'quantity',
            'price_at_purchase', 'subtotal', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'subtotal']
    
    def get_subtotal(self, obj):
        """Get item subtotal."""
        return float(obj.subtotal)


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer for order status history."""
    
    class Meta:
        model = OrderStatusHistory
        fields = ['id', 'from_status', 'to_status', 'note', 'created_at']
        read_only_fields = ['id', 'created_at']


class OrderListSerializer(serializers.ModelSerializer):
    """Serializer for order list view."""
    item_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'status', 'total_amount', 'item_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'item_count', 'created_at', 'updated_at']


class OrderDetailSerializer(serializers.ModelSerializer):
    """Serializer for order detail view."""
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    item_count = serializers.IntegerField(read_only=True)
    can_cancel = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'status', 'shipping_address', 'shipping_city',
            'shipping_postal_code', 'shipping_country', 'subtotal',
            'shipping_cost', 'tax', 'total_amount', 'tracking_number',
            'notes', 'items', 'status_history', 'item_count',
            'can_cancel', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'items', 'status_history', 'item_count',
            'can_cancel', 'created_at', 'updated_at'
        ]
    
    def get_can_cancel(self, obj):
        """Check if order can be cancelled."""
        return obj.can_cancel()


class CheckoutSerializer(serializers.Serializer):
    """
    Serializer for checkout (convert cart to order).
    """
    shipping_address = serializers.CharField(max_length=255)
    shipping_city = serializers.CharField(max_length=100)
    shipping_postal_code = serializers.CharField(max_length=20)
    shipping_country = serializers.CharField(max_length=100)
    shipping_cost = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def validate(self, data):
        """Validate user has items in cart."""
        user = self.context['request'].user
        
        try:
            cart = Cart.objects.get(user=user)
            if not cart.items.exists():
                raise serializers.ValidationError('Cart is empty. Cannot checkout.')
        except Cart.DoesNotExist:
            raise serializers.ValidationError('Cart not found.')
        
        return data


class OrderUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating order (admin only)."""
    
    class Meta:
        model = Order
        fields = ['status', 'tracking_number', 'notes']
