"""
Products app models.
"""
from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from apps.core.models import TimeStampedModel
from apps.categories.models import Category


class Product(TimeStampedModel):
    """
    Product model with inventory management.
    
    Features:
    - Auto-generated slug for URL-friendly names
    - Category relationship with FK
    - Pricing with optional discount
    - Stock quantity tracking
    - Active/inactive status
    - SKU (Stock Keeping Unit) for inventory systems
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text='Leave empty if no discount. Must be less than price.'
    )
    
    # Inventory
    stock_quantity = models.IntegerField(default=0)
    sku = models.CharField(max_length=100, unique=True, help_text='Stock Keeping Unit')
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
            models.Index(fields=['sku']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-generate slug and validate pricing."""
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Validate discount price
        if self.discount_price and self.discount_price >= self.price:
            raise ValidationError({
                'discount_price': 'Discount price must be less than regular price.'
            })
        
        super().save(*args, **kwargs)
    
    @property
    def stock_status(self):
        """Computed property for stock status."""
        if self.stock_quantity <= 0:
            return 'out_of_stock'
        elif self.stock_quantity <= 5:
            return 'low_stock'
        return 'in_stock'
    
    @property
    def display_price(self):
        """Get price to display (discount if available, else regular)."""
        return self.discount_price if self.discount_price else self.price
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage if discount is applied."""
        if self.discount_price:
            discount = (self.price - self.discount_price) / self.price * 100
            return round(discount, 2)
        return 0
    
    def reduce_stock(self, quantity):
        """Reduce stock by quantity. Raises validation error if insufficient stock."""
        if quantity > self.stock_quantity:
            raise ValidationError({
                'stock_quantity': f'Insufficient stock. Available: {self.stock_quantity}, Requested: {quantity}'
            })
        self.stock_quantity -= quantity
        self.save()
    
    def increase_stock(self, quantity):
        """Increase stock by quantity."""
        self.stock_quantity += quantity
        self.save()


class ProductImage(TimeStampedModel):
    """
    Product image model for storing multiple images per product.
    
    Features:
    - Multiple images per product
    - Primary image designation
    - Automatic image validation and optimization
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/%Y/%m/%d/')
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    display_order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['display_order', '-created_at']
        indexes = [
            models.Index(fields=['product', 'is_primary']),
        ]
    
    def __str__(self):
        return f"Image for {self.product.name}"
    
    def save(self, *args, **kwargs):
        """
        Validate image file and set only one primary image per product.
        """
        from apps.core.utils import validate_image_file
        
        # Validate image
        is_valid, error_msg = validate_image_file(self.image)
        if not is_valid:
            raise ValidationError({'image': error_msg})
        
        # Ensure only one primary image per product
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        
        super().save(*args, **kwargs)
