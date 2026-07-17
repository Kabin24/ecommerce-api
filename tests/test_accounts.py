"""
Tests for accounts app - User registration, authentication, and profile.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from apps.accounts.models import EmailVerificationToken, UserProfile

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user(db):
    """Create a test user."""
    user = User.objects.create_user(
        email='test@example.com',
        username='testuser',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )
    UserProfile.objects.create(user=user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """Get authentication headers for test user."""
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(test_user)
    return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}


@pytest.mark.django_db
class TestUserRegistration:
    """Test user registration endpoint."""
    
    def test_register_success(self, api_client):
        """Test successful user registration."""
        data = {
            'email': 'newuser@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone_number': '+1234567890',
            'password': 'securepass123',
            'password_confirm': 'securepass123'
        }
        
        response = api_client.post('/api/auth/register/', data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        assert User.objects.filter(email='newuser@example.com').exists()
    
    def test_register_password_mismatch(self, api_client):
        """Test registration with mismatched passwords."""
        data = {
            'email': 'newuser@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'securepass123',
            'password_confirm': 'differentpass123'
        }
        
        response = api_client.post('/api/auth/register/', data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False
    
    def test_register_duplicate_email(self, api_client, test_user):
        """Test registration with duplicate email."""
        data = {
            'email': test_user.email,
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'securepass123',
            'password_confirm': 'securepass123'
        }
        
        response = api_client.post('/api/auth/register/', data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserLogin:
    """Test user login endpoint."""
    
    def test_login_success(self, api_client, test_user):
        """Test successful login."""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        response = api_client.post('/api/auth/login/', data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'access' in response.data['data']
        assert 'refresh' in response.data['data']
    
    def test_login_invalid_email(self, api_client):
        """Test login with invalid email."""
        data = {
            'email': 'nonexistent@example.com',
            'password': 'testpass123'
        }
        
        response = api_client.post('/api/auth/login/', data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_invalid_password(self, api_client, test_user):
        """Test login with invalid password."""
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        
        response = api_client.post('/api/auth/login/', data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserProfile:
    """Test user profile endpoints."""
    
    def test_get_profile(self, api_client, test_user, auth_headers):
        """Test retrieving user profile."""
        response = api_client.get('/api/auth/profile/', **auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['email'] == test_user.email
    
    def test_update_profile(self, api_client, test_user, auth_headers):
        """Test updating user profile."""
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '+9876543210'
        }
        
        response = api_client.put('/api/auth/profile/', data, format='json', **auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify changes
        test_user.refresh_from_db()
        assert test_user.first_name == 'Updated'


@pytest.mark.django_db
class TestChangePassword:
    """Test password change endpoint."""
    
    def test_change_password_success(self, api_client, test_user, auth_headers):
        """Test successful password change."""
        data = {
            'old_password': 'testpass123',
            'new_password': 'newpass456',
            'new_password_confirm': 'newpass456'
        }
        
        response = api_client.post('/api/auth/change-password/', data, format='json', **auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify password changed
        test_user.refresh_from_db()
        assert test_user.check_password('newpass456')
    
    def test_change_password_wrong_old(self, api_client, test_user, auth_headers):
        """Test password change with wrong old password."""
        data = {
            'old_password': 'wrongpass',
            'new_password': 'newpass456',
            'new_password_confirm': 'newpass456'
        }
        
        response = api_client.post('/api/auth/change-password/', data, format='json', **auth_headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestTokenRefresh:
    """Test token refresh endpoint."""
    
    def test_refresh_token(self, api_client, test_user):
        """Test refreshing access token."""
        from rest_framework_simplejwt.tokens import RefreshToken
        
        refresh = RefreshToken.for_user(test_user)
        data = {'refresh': str(refresh)}
        
        response = api_client.post('/api/auth/refresh/', data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data['data']
