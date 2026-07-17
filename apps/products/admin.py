"""
Products app admin configuration.
"""
from django.contrib import admin
from .models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    """Inline admin for product images."""
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'is_primary', 'display_order')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin for Product model."""
    list_display = ('name', 'sku', 'category', 'price', 'discount_price', 'stock_status', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'sku')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at', 'stock_status', 'display_price')
    inlines = [ProductImageInline]
    
    fieldsets = (
        ('Basic Info', {'fields': ('name', 'slug', 'description', 'category')}),
        ('Pricing', {'fields': ('price', 'discount_price', 'display_price')}),
        ('Inventory', {'fields': ('sku', 'stock_quantity', 'stock_status')}),
        ('Status', {'fields': ('is_active',)}),
        ('Metadata', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Admin for ProductImage model."""
    list_display = ('get_product', 'image', 'is_primary', 'display_order', 'created_at')
    list_filter = ('is_primary', 'created_at', 'product')
    search_fields = ('product__name', 'alt_text')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_product(self, obj):
        return obj.product.name
    get_product.short_description = 'Product'
