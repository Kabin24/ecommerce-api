"""
Products app URLs.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet

router = DefaultRouter()
router.register('', ProductViewSet, basename='product')

app_name = 'products'

urlpatterns = [
    path('', include(router.urls)),
]
