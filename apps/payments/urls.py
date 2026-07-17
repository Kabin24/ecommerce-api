"""
Payments app URLs.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, stripe_webhook

router = DefaultRouter()
router.register('', PaymentViewSet, basename='payment')

app_name = 'payments'

urlpatterns = [
    path('', include(router.urls)),
    path('webhook/stripe/', stripe_webhook, name='stripe-webhook'),
]
