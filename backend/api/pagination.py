
"""Creating the paginator."""

from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Creating the paginator inherited from PageNumberPagination."""

    page_size = 6
    page_size_query_param = 'limit'