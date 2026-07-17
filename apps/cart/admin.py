"""
Cart app admin configuration.
"""
from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    """Inline admin for cart items."""
    model = CartItem
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin for Cart model."""
    list_display = ('get_user', 'total_items', 'subtotal', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__email',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CartItemInline]
    
    def get_user(self, obj):
        return obj.user.email
    get_user.short_description = 'User'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin for CartItem model."""
    list_display = ('get_product', 'get_user', 'quantity', 'get_total', 'created_at')
    list_filter = ('created_at', 'product__category')
    search_fields = ('product__name', 'cart__user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_product(self, obj):
        return obj.product.name
    get_product.short_description = 'Product'
    
    def get_user(self, obj):
        return obj.cart.user.email
    get_user.short_description = 'User'
    
    def get_total(self, obj):
        return f"${obj.get_total():.2f}"
    get_total.short_description = 'Total'
