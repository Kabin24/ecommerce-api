"""
Tests for orders app - Order creation and management.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from apps.orders.models import Order, OrderItem
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
class TestCheckout:
    """Test order checkout."""
    
    def test_checkout_success(self, api_client, test_user, product, auth_headers):
        """Test successful checkout."""
        # Add items to cart
        cart = Cart.objects.get_or_create(user=test_user)[0]
        CartItem.objects.create(cart=cart, product=product, quantity=2)
        
        # Checkout
        data = {
            'shipping_address': '123 Main St',
            'shipping_city': 'New York',
            'shipping_postal_code': '10001',
            'shipping_country': 'USA',
            'shipping_cost': 10.00,
            'tax': 5.50
        }
        
        response = api_client.post(
            '/api/orders/checkout/',
            data,
            format='json',
            **auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        
        # Verify order created
        assert Order.objects.filter(user=test_user).exists()
        
        # Verify cart cleared
        cart.refresh_from_db()
        assert cart.items.count() == 0
    
    def test_checkout_empty_cart(self, api_client, test_user, auth_headers):
        """Test checkout with empty cart."""
        data = {
            'shipping_address': '123 Main St',
            'shipping_city': 'New York',
            'shipping_postal_code': '10001',
            'shipping_country': 'USA'
        }
        
        response = api_client.post(
            '/api/orders/checkout/',
            data,
            format='json',
            **auth_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestOrderList:
    """Test order listing."""
    
    def test_list_user_orders(self, api_client, test_user, auth_headers):
        """Test listing user's orders."""
        # Create an order
        Order.objects.create(
            user=test_user,
            status=Order.OrderStatus.PENDING,
            shipping_address='123 Main St',
            shipping_city='New York',
            shipping_postal_code='10001',
            shipping_country='USA',
            total_amount=100.00
        )
        
        response = api_client.get('/api/orders/', **auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1


@pytest.mark.django_db
class TestOrderDetail:
    """Test order detail view."""
    
    def test_get_order_detail(self, api_client, test_user, auth_headers):
        """Test retrieving order details."""
        order = Order.objects.create(
            user=test_user,
            status=Order.OrderStatus.PENDING,
            shipping_address='123 Main St',
            shipping_city='New York',
            shipping_postal_code='10001',
            shipping_country='USA',
            total_amount=100.00
        )
        
        response = api_client.get(f'/api/orders/{order.id}/', **auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['id'] == order.id


@pytest.mark.django_db
class TestOrderCancellation:
    """Test order cancellation."""
    
    def test_cancel_pending_order(self, api_client, test_user, product, auth_headers):
        """Test cancelling a pending order."""
        # Create order with items
        order = Order.objects.create(
            user=test_user,
            status=Order.OrderStatus.PENDING,
            shipping_address='123 Main St',
            shipping_city='New York',
            shipping_postal_code='10001',
            shipping_country='USA',
            total_amount=100.00
        )
        
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=2,
            price_at_purchase=product.price
        )
        
        initial_stock = product.stock_quantity
        
        # Cancel order
        response = api_client.post(
            f'/api/orders/{order.id}/cancel/',
            {},
            format='json',
            **auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify stock restored
        product.refresh_from_db()
        assert product.stock_quantity == initial_stock + 2


@pytest.mark.django_db
class TestOrderStockReduction:
    """Test stock reduction on checkout."""
    
    def test_stock_reduced_on_checkout(self, api_client, test_user, product, auth_headers):
        """Test that product stock is reduced when order is created."""
        initial_stock = product.stock_quantity
        
        # Add to cart and checkout
        cart = Cart.objects.get_or_create(user=test_user)[0]
        CartItem.objects.create(cart=cart, product=product, quantity=3)
        
        data = {
            'shipping_address': '123 Main St',
            'shipping_city': 'New York',
            'shipping_postal_code': '10001',
            'shipping_country': 'USA'
        }
        
        api_client.post('/api/orders/checkout/', data, format='json', **auth_headers)
        
        # Verify stock reduced
        product.refresh_from_db()
        assert product.stock_quantity == initial_stock - 3
