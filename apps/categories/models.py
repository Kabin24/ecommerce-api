"""
Categories app models.
"""
from django.db import models
from django.utils.text import slugify
from apps.core.models import TimeStampedModel


class Category(TimeStampedModel):
    """
    Product category model with support for nested (parent-child) categories.
    
    Features:
    - Auto-generated slug for URL-friendly names
    - Self-referencing parent field for hierarchy
    - Active/inactive status for visibility control
    """
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
            models.Index(fields=['parent']),
        ]
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-generate slug if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_ancestors(self):
        """Get all parent categories in the hierarchy."""
        ancestors = []
        parent = self.parent
        while parent is not None:
            ancestors.append(parent)
            parent = parent.parent
        return ancestors
    
    def get_descendants(self):
        """Get all child categories recursively."""
        descendants = []
        for child in self.children.all():
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants
    
    @property
    def breadcrumb(self):
        """Get breadcrumb path as string (e.g., 'Electronics > Phones')."""
        ancestors = self.get_ancestors()
        ancestors.reverse()
        breadcrumb_list = [cat.name for cat in ancestors] + [self.name]
        return ' > '.join(breadcrumb_list)
