"""
Categories app serializers.
"""
from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for category with nested children.
    Provides category details with recursive child categories.
    """
    breadcrumb = serializers.CharField(read_only=True)
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description',
            'parent', 'is_active', 'breadcrumb',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'breadcrumb']


class CategoryNestedSerializer(serializers.ModelSerializer):
    """
    Serializer for category with nested children details.
    Used for tree-like category display.
    """
    children = serializers.SerializerMethodField()
    breadcrumb = serializers.CharField(read_only=True)
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description',
            'parent', 'is_active', 'breadcrumb', 'children',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'breadcrumb']
    
    def get_children(self, obj):
        """Get nested children recursively."""
        children = obj.children.filter(is_active=True)
        if children.exists():
            return CategoryNestedSerializer(children, many=True).data
        return []
