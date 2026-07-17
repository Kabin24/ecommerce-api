"""
Accounts app URLs.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet

router = DefaultRouter()
router.register('', AuthViewSet, basename='auth')

app_name = 'accounts'

urlpatterns = [
    path('', include(router.urls)),
]
