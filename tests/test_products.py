"""
Tests for products app - Product CRUD and inventory.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from apps.products.models import Product, ProductImage
from apps.categories.models import Category

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    return User.objects.create_superuser(
        email='admin@example.com',
        username='admin',
        password='adminpass123'
    )


@pytest.fixture
def category(db):
    """Create a test category."""
    return Category.objects.create(
        name='Electronics',
        slug='electronics',
        description='Electronic devices'
    )


@pytest.fixture
def product(db, category):
    """Create a test product."""
    return Product.objects.create(
        name='Test Product',
        slug='test-product',
        description='A test product',
        price=99.99,
        stock_quantity=10,
        sku='TEST001',
        category=category
    )


@pytest.fixture
def admin_auth_headers(admin_user):
    """Get authentication headers for admin user."""
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(admin_user)
    return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}


@pytest.mark.django_db
class TestProductList:
    """Test product listing and filtering."""
    
    def test_list_products(self, api_client, product):
        """Test listing products."""
        response = api_client.get('/api/products/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
    
    def test_list_filter_by_category(self, api_client, product, category):
        """Test filtering products by category."""
        response = api_client.get(f'/api/products/?category={category.id}')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_list_filter_by_price(self, api_client, product):
        """Test filtering by price range."""
        response = api_client.get('/api/products/?min_price=50&max_price=150')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_search_products(self, api_client, product):
        """Test product search."""
        response = api_client.get('/api/products/?search=test')
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestProductDetail:
    """Test product detail view."""
    
    def test_get_product_detail(self, api_client, product):
        """Test retrieving product details."""
        response = api_client.get(f'/api/products/{product.slug}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['name'] == product.name
        assert response.data['data']['stock_status'] == 'in_stock'


@pytest.mark.django_db
class TestProductCreate:
    """Test product creation (admin only)."""
    
    def test_create_product_admin(self, api_client, admin_user, category, admin_auth_headers):
        """Test creating product as admin."""
        data = {
            'name': 'New Product',
            'description': 'A new product',
            'price': '49.99',
            'stock_quantity': 20,
            'sku': 'NEW001',
            'category': category.id
        }
        
        response = api_client.post(
            '/api/products/',
            data,
            format='json',
            **admin_auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Product.objects.filter(sku='NEW001').exists()
    
    def test_create_product_non_admin(self, api_client, category):
        """Test creating product as non-admin (should fail)."""
        data = {
            'name': 'New Product',
            'description': 'A new product',
            'price': '49.99',
            'stock_quantity': 20,
            'sku': 'NEW001',
            'category': category.id
        }
        
        response = api_client.post('/api/products/', data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestProductStockManagement:
    """Test stock reduction and increase."""
    
    def test_reduce_stock(self, api_client, product, admin_auth_headers):
        """Test reducing product stock."""
        initial_stock = product.stock_quantity
        
        data = {'quantity': 3}
        response = api_client.post(
            f'/api/products/{product.slug}/reduce_stock/',
            data,
            format='json',
            **admin_auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        product.refresh_from_db()
        assert product.stock_quantity == initial_stock - 3
    
    def test_increase_stock(self, api_client, product, admin_auth_headers):
        """Test increasing product stock."""
        initial_stock = product.stock_quantity
        
        data = {'quantity': 5}
        response = api_client.post(
            f'/api/products/{product.slug}/increase_stock/',
            data,
            format='json',
            **admin_auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        product.refresh_from_db()
        assert product.stock_quantity == initial_stock + 5


@pytest.mark.django_db
class TestProductStockStatus:
    """Test stock status computation."""
    
    def test_stock_status_in_stock(self, db, category):
        """Test in_stock status."""
        product = Product.objects.create(
            name='In Stock Product',
            slug='in-stock',
            description='Test',
            price=99.99,
            stock_quantity=10,
            sku='INSTOCK',
            category=category
        )
        
        assert product.stock_status == 'in_stock'
    
    def test_stock_status_low_stock(self, db, category):
        """Test low_stock status."""
        product = Product.objects.create(
            name='Low Stock Product',
            slug='low-stock',
            description='Test',
            price=99.99,
            stock_quantity=3,
            sku='LOWSTOCK',
            category=category
        )
        
        assert product.stock_status == 'low_stock'
    
    def test_stock_status_out_of_stock(self, db, category):
        """Test out_of_stock status."""
        product = Product.objects.create(
            name='Out of Stock Product',
            slug='out-of-stock',
            description='Test',
            price=99.99,
            stock_quantity=0,
            sku='OUTOFSTOCK',
            category=category
        )
        
        assert product.stock_status == 'out_of_stock'


@pytest.mark.django_db
class TestProductPricing:
    """Test product pricing and discounts."""
    
    def test_product_without_discount(self, product):
        """Test product pricing without discount."""
        assert product.display_price == product.price
        assert product.discount_percentage == 0
    
    def test_product_with_discount(self, db, category):
        """Test product pricing with discount."""
        product = Product.objects.create(
            name='Discounted Product',
            slug='discounted',
            description='Test',
            price=100.00,
            discount_price=75.00,
            stock_quantity=5,
            sku='DISCOUNT',
            category=category
        )
        
        assert product.display_price == 75.00
        assert product.discount_percentage == 25.0
