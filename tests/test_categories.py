"""
Tests for categories app - Category hierarchy and CRUD.
"""
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from apps.categories.models import Category


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def root_category(db):
    """Create a root category."""
    return Category.objects.create(
        name='Electronics',
        slug='electronics',
        description='Electronic devices'
    )


@pytest.fixture
def child_category(db, root_category):
    """Create a child category."""
    return Category.objects.create(
        name='Phones',
        slug='phones',
        description='Mobile phones',
        parent=root_category
    )


@pytest.mark.django_db
class TestCategoryList:
    """Test category listing."""
    
    def test_list_categories(self, api_client, root_category):
        """Test listing categories."""
        response = api_client.get('/api/categories/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
    
    def test_list_categories_tree(self, api_client, root_category, child_category):
        """Test listing categories as tree."""
        response = api_client.get('/api/categories/tree/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) > 0


@pytest.mark.django_db
class TestCategoryDetail:
    """Test category detail view."""
    
    def test_get_category_detail(self, api_client, root_category):
        """Test retrieving category details."""
        response = api_client.get(f'/api/categories/{root_category.slug}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['name'] == root_category.name


@pytest.mark.django_db
class TestCategoryHierarchy:
    """Test category hierarchy operations."""
    
    def test_get_children(self, api_client, root_category, child_category):
        """Test retrieving category children."""
        response = api_client.get(f'/api/categories/{root_category.slug}/children/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) > 0
    
    def test_get_ancestors(self, api_client, child_category):
        """Test retrieving category ancestors."""
        response = api_client.get(f'/api/categories/{child_category.slug}/ancestors/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) > 0


@pytest.mark.django_db
class TestCategoryBreadcrumb:
    """Test category breadcrumb functionality."""
    
    def test_breadcrumb_root(self, root_category):
        """Test breadcrumb for root category."""
        assert root_category.breadcrumb == 'Electronics'
    
    def test_breadcrumb_nested(self, child_category):
        """Test breadcrumb for nested category."""
        assert child_category.breadcrumb == 'Electronics > Phones'
