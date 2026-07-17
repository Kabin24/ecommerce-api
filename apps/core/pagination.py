"""
Custom pagination for REST Framework.
"""
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination for list views.
    Uses ?page= query parameter.
    """
    page_size_query_param = 'page_size'
    max_page_size = 100
