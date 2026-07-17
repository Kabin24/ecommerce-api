"""
Orders app admin configuration.
"""
from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    """Inline admin for order items."""
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price_at_purchase', 'created_at')
    can_delete = False


class OrderStatusHistoryInline(admin.TabularInline):
    """Inline admin for order status history."""
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ('from_status', 'to_status', 'note', 'created_at')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin for Order model."""
    list_display = (
        'id', 'get_user', 'status', 'total_amount',
        'item_count', 'created_at'
    )
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('user__email', 'id', 'tracking_number')
    readonly_fields = ('created_at', 'updated_at', 'item_count')
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    
    fieldsets = (
        ('Order Info', {'fields': ('user', 'status', 'item_count')}),
        ('Shipping', {
            'fields': (
                'shipping_address', 'shipping_city',
                'shipping_postal_code', 'shipping_country'
            )
        }),
        ('Financial', {'fields': ('subtotal', 'shipping_cost', 'tax', 'total_amount')}),
        ('Tracking', {'fields': ('tracking_number',)}),
        ('Notes', {'fields': ('notes',)}),
        ('Metadata', {'fields': ('created_at', 'updated_at')}),
    )
    
    def get_user(self, obj):
        return obj.user.email
    get_user.short_description = 'User'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin for OrderItem model."""
    list_display = ('get_product', 'get_order', 'quantity', 'price_at_purchase', 'get_subtotal')
    list_filter = ('created_at', 'product__category')
    search_fields = ('product__name', 'order__id')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_product(self, obj):
        return obj.product.name
    get_product.short_description = 'Product'
    
    def get_order(self, obj):
        return f"Order #{obj.order.id}"
    get_order.short_description = 'Order'
    
    def get_subtotal(self, obj):
        return f"${obj.subtotal:.2f}"
    get_subtotal.short_description = 'Subtotal'


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    """Admin for OrderStatusHistory model."""
    list_display = ('get_order', 'from_status', 'to_status', 'created_at')
    list_filter = ('to_status', 'created_at')
    search_fields = ('order__id', 'note')
    readonly_fields = ('created_at',)
    
    def get_order(self, obj):
        return f"Order #{obj.order.id}"
    get_order.short_description = 'Order'
