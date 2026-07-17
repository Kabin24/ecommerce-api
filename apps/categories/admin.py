"""
Categories app admin configuration.
"""
from django.contrib import admin
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin for Category model."""
    list_display = ('name', 'slug', 'get_parent', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'parent')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at', 'breadcrumb')
    ordering = ('name',)
    
    fieldsets = (
        ('Basic Info', {'fields': ('name', 'slug', 'description')}),
        ('Hierarchy', {'fields': ('parent',)}),
        ('Status', {'fields': ('is_active',)}),
        ('Metadata', {'fields': ('breadcrumb', 'created_at', 'updated_at')}),
    )
    
    def get_parent(self, obj):
        """Display parent category name."""
        return obj.parent.name if obj.parent else '—'
    get_parent.short_description = 'Parent Category'
