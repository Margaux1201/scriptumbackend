from rest_framework.pagination import PageNumberPagination

class BookPagination(PageNumberPagination):
    page_size = 5 # valeur par défaut
    page_size_query_param = "size" # ex: ?size=20
    max_page_size = 100