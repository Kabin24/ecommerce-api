"""
Cart app models - Shopping cart for authenticated users.
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from apps.core.models import TimeStampedModel
from apps.products.models import Product


class Cart(TimeStampedModel):
    """
    Shopping cart tied to an authenticated user.
    One active cart per user.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Cart for {self.user.email}"
    
    @property
    def subtotal(self):
        """Calculate subtotal of all items."""
        return sum(item.get_total() for item in self.items.all())
    
    @property
    def total_items(self):
        """Get total number of items in cart."""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_quantity(self):
        """Get total quantity of items."""
        return self.total_items
    
    def clear(self):
        """Remove all items from cart."""
        self.items.all().delete()


class CartItem(TimeStampedModel):
    """
    Individual item in shopping cart.
    Links product to cart with quantity.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text='Quantity must be at least 1'
    )
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['cart', 'product']
        indexes = [
            models.Index(fields=['cart', 'product']),
        ]
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity} in {self.cart.user.email}'s cart"
    
    def get_total(self):
        """Calculate total price for this item (quantity * unit price)."""
        return self.product.display_price * self.quantity
    
    def save(self, *args, **kwargs):
        """Validate quantity against stock."""
        if self.quantity > self.product.stock_quantity:
            raise ValueError(
                f'Cannot add {self.quantity} items. Only {self.product.stock_quantity} in stock.'
            )
        super().save(*args, **kwargs)
