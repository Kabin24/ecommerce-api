"""
Core app URLs.
"""
from django.urls import path
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def health_check(request):
    return Response({'status': 'healthy'})

app_name = 'core'

urlpatterns = [
    path('health/', health_check, name='health-check'),
]
