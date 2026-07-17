"""
Cart app serializers.
"""
from rest_framework import serializers
from .models import Cart, CartItem
from apps.products.serializers import ProductListSerializer


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for cart items with product details."""
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'total', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_total(self, obj):
        """Get item total price."""
        return float(obj.get_total())


class CartSerializer(serializers.ModelSerializer):
    """Serializer for shopping cart with items and totals."""
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'subtotal', 'total_items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_subtotal(self, obj):
        """Get cart subtotal."""
        return float(obj.subtotal)
    
    def get_total_items(self, obj):
        """Get total items in cart."""
        return obj.total_items
