"""
Orders app models - Order management and fulfillment.
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from apps.core.models import TimeStampedModel
from apps.products.models import Product


class Order(TimeStampedModel):
    """
    Order model representing a customer purchase.
    
    Features:
    - Order status tracking (pending, paid, shipped, delivered, cancelled)
    - Shipping address storage
    - Total amount calculation
    - Automatic status history logging
    """
    
    class OrderStatus(models.TextChoices):
        """Order status choices."""
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING
    )
    
    # Shipping information
    shipping_address = models.TextField(help_text='Full shipping address')
    shipping_city = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100)
    
    # Financial
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Tracking
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Order #{self.id} by {self.user.email}"
    
    @property
    def item_count(self):
        """Get total number of items in order."""
        return sum(item.quantity for item in self.items.all())
    
    def can_cancel(self):
        """Check if order can be cancelled."""
        return self.status in [self.OrderStatus.PENDING]
    
    def cancel(self):
        """Cancel order and return items to stock."""
        if not self.can_cancel():
            raise ValueError(f'Cannot cancel order with status: {self.status}')
        
        # Return stock for all items
        for item in self.items.all():
            item.product.increase_stock(item.quantity)
        
        self.status = self.OrderStatus.CANCELLED
        self.save()
        
        # Log status change
        OrderStatusHistory.objects.create(
            order=self,
            from_status=None,
            to_status=self.OrderStatus.CANCELLED,
            note='Order cancelled'
        )


class OrderItem(TimeStampedModel):
    """
    Individual item in an order.
    Stores product snapshot at time of purchase (price_at_purchase).
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order']),
        ]
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity} in Order #{self.order.id}"
    
    @property
    def subtotal(self):
        """Get item subtotal."""
        return self.price_at_purchase * self.quantity


class OrderStatusHistory(TimeStampedModel):
    """
    Track order status changes over time.
    Provides audit trail for order lifecycle.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    from_status = models.CharField(max_length=20, null=True, blank=True)
    to_status = models.CharField(max_length=20)
    note = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Order Status Histories'
    
    def __str__(self):
        return f"Order #{self.order.id}: {self.from_status or 'Created'} → {self.to_status}"
