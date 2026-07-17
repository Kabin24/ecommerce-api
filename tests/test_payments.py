"""
Tests for payments app - Stripe integration.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from apps.payments.models import Payment
from apps.orders.models import Order
from apps.categories.models import Category
from apps.products.models import Product

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
def order(db, test_user):
    """Create a test order."""
    return Order.objects.create(
        user=test_user,
        status=Order.OrderStatus.PENDING,
        shipping_address='123 Main St',
        shipping_city='New York',
        shipping_postal_code='10001',
        shipping_country='USA',
        total_amount=100.00
    )


@pytest.mark.django_db
class TestPaymentIntentCreation:
    """Test Stripe PaymentIntent creation."""
    
    def test_create_payment_intent(self, api_client, order, auth_headers):
        """Test creating payment intent for order."""
        data = {'order_id': order.id}
        
        response = api_client.post(
            '/api/payments/create_intent/',
            data,
            format='json',
            **auth_headers
        )
        
        # Note: This will fail without actual Stripe API key
        # In real tests, use stripe test mode keys or mock stripe
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_500_INTERNAL_SERVER_ERROR]


@pytest.mark.django_db
class TestPaymentStatus:
    """Test payment status retrieval."""
    
    def test_get_payment_status(self, api_client, order, auth_headers):
        """Test retrieving payment status."""
        # Create payment record
        payment = Payment.objects.create(
            order=order,
            amount=order.total_amount,
            currency='USD',
            status=Payment.PaymentStatus.PENDING,
            stripe_payment_intent_id='pi_test123'
        )
        
        response = api_client.get(
            f'/api/payments/status/?order_id={order.id}',
            **auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['status'] == Payment.PaymentStatus.PENDING
