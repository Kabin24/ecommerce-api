"""
Pytest configuration for Django E-Commerce Backend.
"""
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_backend.settings.dev')

# Setup Django
django.setup()

def pytest_configure():
    """Configure pytest with Django test settings."""
    settings.DEBUG = True
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
