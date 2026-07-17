"""
Core app URLs.
"""
from django.urls import path

app_name = 'core'

urlpatterns = [
    # Health check endpoint
    path('health/', lambda request: None, name='health-check'),
]
