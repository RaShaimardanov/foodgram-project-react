import os

from dotenv import load_dotenv
from rest_framework.pagination import PageNumberPagination

load_dotenv()


class CustomPagination(PageNumberPagination):
    """Пагинатор проекта."""
    page_size = os.getenv('PAGE_SIZE', 6)
    page_size_query_param = 'limit'
