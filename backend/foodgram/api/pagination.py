from foodgram.settings import PAGE_SIZE
from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Кастомный класс пагинации."""
    page_size_query_param = 'limit'
    page_size = PAGE_SIZE
