"""
Tests for cart app - Shopping cart operations.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from apps.cart.models import Cart, CartItem
from apps.products.models import Product
from apps.categories.models import Category

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user(db):
    """Create a test user."""
    return User.objects.create_user(
        email='user@example.com',
        username='testuser',
        password='testpass123'
    )


@pytest.fixture
def auth_headers(test_user):
    """Get authentication headers."""
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(test_user)
    return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}


@pytest.fixture
def category(db):
    """Create a test category."""
    return Category.objects.create(
        name='Test Category',
        slug='test-category'
    )


@pytest.fixture
def product(db, category):
    """Create a test product."""
    return Product.objects.create(
        name='Test Product',
        slug='test-product',
        description='Test',
        price=99.99,
        stock_quantity=10,
        sku='TEST001',
        category=category
    )


@pytest.mark.django_db
class TestCartOperations:
    """Test shopping cart operations."""
    
    def test_view_empty_cart(self, api_client, test_user, auth_headers):
        """Test viewing empty cart."""
        response = api_client.get('/api/cart/', **auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data']['total_items'] == 0
    
    def test_add_product_to_cart(self, api_client, product, auth_headers):
        """Test adding product to cart."""
        data = {
            'product_id': product.id,
            'quantity': 2
        }
        
        response = api_client.post('/api/cart/add/', data, format='json', **auth_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['data']['total_items'] == 2
    
    def test_add_insufficient_stock(self, api_client, product, auth_headers):
        """Test adding more items than available stock."""
        data = {
            'product_id': product.id,
            'quantity': 20  # More than available stock
        }
        
        response = api_client.post('/api/cart/add/', data, format='json', **auth_headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False


@pytest.mark.django_db
class TestCartItemManagement:
    """Test cart item management."""
    
    def test_update_item_quantity(self, api_client, test_user, product, auth_headers):
        """Test updating cart item quantity."""
        # Add item first
        cart = Cart.objects.get_or_create(user=test_user)[0]
        cart_item = CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=2
        )
        
        # Update quantity
        data = {'quantity': 5}
        response = api_client.put(
            f'/api/cart/items/{cart_item.id}/',
            data,
            format='json',
            **auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        cart_item.refresh_from_db()
        assert cart_item.quantity == 5
    
    def test_remove_item_from_cart(self, api_client, test_user, product, auth_headers):
        """Test removing item from cart."""
        # Add item first
        cart = Cart.objects.get_or_create(user=test_user)[0]
        cart_item = CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=2
        )
        
        # Remove item
        response = api_client.delete(
            f'/api/cart/items/{cart_item.id}/',
            **auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert not CartItem.objects.filter(id=cart_item.id).exists()
    
    def test_clear_cart(self, api_client, test_user, product, auth_headers):
        """Test clearing entire cart."""
        # Add items first
        cart = Cart.objects.get_or_create(user=test_user)[0]
        CartItem.objects.create(cart=cart, product=product, quantity=2)
        
        # Clear cart
        response = api_client.delete('/api/cart/clear/', **auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        assert cart.items.count() == 0


@pytest.mark.django_db
class TestCartTotals:
    """Test cart calculation."""
    
    def test_cart_subtotal(self, test_user, product):
        """Test cart subtotal calculation."""
        cart = Cart.objects.get_or_create(user=test_user)[0]
        CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=2
        )
        
        expected_subtotal = product.display_price * 2
        assert float(cart.subtotal) == float(expected_subtotal)
    
    def test_cart_total_items(self, test_user, product):
        """Test cart total items count."""
        cart = Cart.objects.get_or_create(user=test_user)[0]
        CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=3
        )
        
        assert cart.total_items == 3
