"""
Payments app admin configuration.
"""
from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin for Payment model."""
    list_display = (
        'get_order', 'amount', 'currency', 'status',
        'stripe_payment_intent_id', 'created_at'
    )
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('stripe_payment_intent_id', 'order__id', 'order__user__email')
    readonly_fields = ('created_at', 'updated_at', 'stripe_payment_intent_id', 'stripe_charge_id')
    
    fieldsets = (
        ('Order & Payment', {'fields': ('order', 'amount', 'currency')}),
        ('Stripe Info', {
            'fields': ('stripe_payment_intent_id', 'stripe_charge_id', 'status')
        }),
        ('Error Handling', {'fields': ('error_message',)}),
        ('Metadata', {'fields': ('created_at', 'updated_at')}),
    )
    
    def get_order(self, obj):
        return f"Order #{obj.order.id}"
    get_order.short_description = 'Order'
