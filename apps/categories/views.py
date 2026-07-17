"""
Categories app views.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.core.permissions import IsAdminOrReadOnly
from .models import Category
from .serializers import CategorySerializer, CategoryNestedSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product categories.
    
    Features:
    - Nested category support (parent-child relationships)
    - List with nested children
    - Search and filter capabilities
    - Admin-only write operations
    """
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['parent', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        """Use nested serializer for list view."""
        if self.action == 'list':
            return CategoryNestedSerializer
        return self.serializer_class
    
    def get_queryset(self):
        """Filter active categories, or all for admin."""
        if self.request.user.is_staff:
            return Category.objects.all()
        return Category.objects.filter(is_active=True)
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """
        Get categories as a tree structure (nested).
        Only includes root categories (parent=None) and their descendants.
        """
        root_categories = Category.objects.filter(
            parent__isnull=True,
            is_active=True
        ).order_by('name')
        
        serializer = CategoryNestedSerializer(root_categories, many=True)
        return Response({
            'success': True,
            'message': 'Category tree retrieved successfully',
            'data': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def children(self, request, slug=None):
        """Get direct children of a specific category."""
        category = self.get_object()
        children = category.children.filter(is_active=True)
        
        serializer = self.get_serializer(children, many=True)
        return Response({
            'success': True,
            'message': f'Children of {category.name}',
            'data': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def ancestors(self, request, slug=None):
        """Get all parent categories of a specific category."""
        category = self.get_object()
        ancestors = category.get_ancestors()
        
        serializer = self.get_serializer(ancestors, many=True)
        return Response({
            'success': True,
            'message': f'Ancestors of {category.name}',
            'data': serializer.data
        })
