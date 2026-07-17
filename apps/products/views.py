"""
Products app views.
"""
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.core.permissions import IsAdminOrReadOnly
from .models import Product, ProductImage
from .serializers import (
    ProductListSerializer, ProductDetailSerializer,
    ProductCreateUpdateSerializer, ProductImageSerializer
)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing products.
    
    Features:
    - List with pagination, filtering, and search
    - Detailed product view with all info and images
    - Image upload and management
    - Stock management
    - Admin-only create/update/delete
    """
    queryset = Product.objects.filter(is_active=True).select_related('category')
    serializer_class = ProductListSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['-created_at']
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        """Return different serializer based on action."""
        if self.action == 'retrieve':
            return ProductDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductListSerializer
    
    def get_queryset(self):
        """Filter based on user permissions."""
        queryset = Product.objects.select_related('category')
        
        # Admins can see all, others see only active
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        
        # Price range filtering
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        return queryset
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_image(self, request, slug=None):
        """
        Upload image for product.
        
        Query params:
        - is_primary: Boolean to mark as primary image (optional, default: False)
        """
        product = self.get_object()
        
        if 'image' not in request.FILES:
            return Response(
                {'success': False, 'message': 'No image file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        is_primary = request.data.get('is_primary', False)
        alt_text = request.data.get('alt_text', '')
        
        try:
            product_image = ProductImage.objects.create(
                product=product,
                image=request.FILES['image'],
                alt_text=alt_text,
                is_primary=is_primary
            )
            
            serializer = ProductImageSerializer(product_image)
            return Response(
                {'success': True, 'message': 'Image uploaded successfully', 'data': serializer.data},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'success': False, 'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['delete'])
    def delete_image(self, request, slug=None):
        """Delete product image by ID."""
        image_id = request.query_params.get('image_id')
        
        if not image_id:
            return Response(
                {'success': False, 'message': 'image_id query parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = self.get_object()
            image = product.images.get(id=image_id)
            image.delete()
            
            return Response(
                {'success': True, 'message': 'Image deleted successfully'}
            )
        except ProductImage.DoesNotExist:
            return Response(
                {'success': False, 'message': 'Image not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def reduce_stock(self, request, slug=None):
        """
        Reduce product stock by specified quantity.
        
        Request body:
        - quantity: Number to reduce (required)
        """
        product = self.get_object()
        quantity = request.data.get('quantity')
        
        if not quantity:
            return Response(
                {'success': False, 'message': 'Quantity is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                return Response(
                    {'success': False, 'message': 'Quantity must be positive'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            product.reduce_stock(quantity)
            return Response({
                'success': True,
                'message': f'Stock reduced by {quantity}',
                'data': {'new_stock': product.stock_quantity}
            })
        except ValueError:
            return Response(
                {'success': False, 'message': 'Invalid quantity value'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'success': False, 'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def increase_stock(self, request, slug=None):
        """Increase product stock by specified quantity."""
        product = self.get_object()
        quantity = request.data.get('quantity')
        
        if not quantity:
            return Response(
                {'success': False, 'message': 'Quantity is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                return Response(
                    {'success': False, 'message': 'Quantity must be positive'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            product.increase_stock(quantity)
            return Response({
                'success': True,
                'message': f'Stock increased by {quantity}',
                'data': {'new_stock': product.stock_quantity}
            })
        except ValueError:
            return Response(
                {'success': False, 'message': 'Invalid quantity value'},
                status=status.HTTP_400_BAD_REQUEST
            )
