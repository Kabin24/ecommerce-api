"""
Payments app models - Stripe payment processing.
"""
from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel
from apps.orders.models import Order


class Payment(TimeStampedModel):
    """
    Payment model storing Stripe payment information.
    
    Features:
    - Links to Order
    - Tracks payment status
    - Stores Stripe PaymentIntent ID for reference
    """
    
    class PaymentStatus(models.TextChoices):
        """Payment status choices."""
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        SUCCEEDED = 'succeeded', 'Succeeded'
        FAILED = 'failed', 'Failed'
        CANCELLED = 'cancelled', 'Cancelled'
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    
    # Stripe references
    stripe_payment_intent_id = models.CharField(
        max_length=255, unique=True,
        help_text='Stripe PaymentIntent ID'
    )
    stripe_charge_id = models.CharField(
        max_length=255, blank=True, null=True,
        help_text='Stripe Charge ID (after successful payment)'
    )
    
    # Error handling
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['status']),
            models.Index(fields=['stripe_payment_intent_id']),
        ]
    
    def __str__(self):
        return f"Payment for Order #{self.order.id} - {self.status}"
    
    @property
    def is_paid(self):
        """Check if payment is successful."""
        return self.status == self.PaymentStatus.SUCCEEDED
    
    def mark_as_succeeded(self, charge_id=None):
        """Mark payment as succeeded."""
        self.status = self.PaymentStatus.SUCCEEDED
        if charge_id:
            self.stripe_charge_id = charge_id
        self.save()
        
        # Update order status to paid
        self.order.status = Order.OrderStatus.PAID
        self.order.save()
    
    def mark_as_failed(self, error_message=None):
        """Mark payment as failed."""
        self.status = self.PaymentStatus.FAILED
        if error_message:
            self.error_message = error_message
        self.save()
