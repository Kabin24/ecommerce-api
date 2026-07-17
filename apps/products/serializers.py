"""
Products app serializers.
"""
from rest_framework import serializers
from .models import Product, ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for product images."""
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'display_order']
        read_only_fields = ['id']


class ProductListSerializer(serializers.ModelSerializer):
    """
    Serializer for product list view.
    Includes computed fields but minimal nested data for performance.
    """
    stock_status = serializers.CharField(read_only=True)
    discount_percentage = serializers.CharField(read_only=True)
    display_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    primary_image = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price', 'discount_price', 'display_price',
            'discount_percentage', 'stock_quantity', 'stock_status',
            'category', 'category_name', 'primary_image', 'created_at'
        ]
        read_only_fields = [
            'id', 'slug', 'stock_status', 'discount_percentage',
            'display_price', 'created_at'
        ]
    
    def get_primary_image(self, obj):
        """Get primary image URL."""
        primary = obj.images.filter(is_primary=True).first()
        if primary:
            return primary.image.url
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for product detail view.
    Includes all fields with nested image data.
    """
    images = ProductImageSerializer(many=True, read_only=True)
    stock_status = serializers.CharField(read_only=True)
    discount_percentage = serializers.CharField(read_only=True)
    display_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_breadcrumb = serializers.CharField(
        source='category.breadcrumb', read_only=True
    )
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'discount_price',
            'display_price', 'discount_percentage', 'stock_quantity', 'stock_status',
            'category', 'category_name', 'category_breadcrumb', 'sku', 'is_active',
            'images', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'slug', 'stock_status', 'discount_percentage',
            'display_price', 'created_at', 'updated_at'
        ]


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating products (admin only).
    """
    images = ProductImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'discount_price',
            'stock_quantity', 'category', 'sku', 'is_active', 'images'
        ]
        read_only_fields = ['id', 'slug', 'images']
    
    def validate_discount_price(self, value):
        """Validate discount price is less than regular price."""
        if value and value >= self.initial_data.get('price'):
            raise serializers.ValidationError(
                'Discount price must be less than regular price.'
            )
        return value
    
    def validate_stock_quantity(self, value):
        """Validate stock quantity is non-negative."""
        if value < 0:
            raise serializers.ValidationError('Stock quantity cannot be negative.')
        return value
