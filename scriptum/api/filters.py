import django_filters
from .models import Book

class BookFilter(django_filters.FilterSet):
    public_type = django_filters.CharFilter(field_name="public_type", lookup_expr="iexact")
    state =django_filters.CharFilter(field_name="state", lookup_expr="iexact")
    genre = django_filters.CharFilter(field_name="genres__name", lookup_expr="icontains")
    theme = django_filters.CharFilter(field_name="themes__name", lookup_expr="icontains")
    is_saga = django_filters.BooleanFilter(field_name="is_saga")
    min_rating = django_filters.NumberFilter(field_name="rating", lookup_expr="gte")
    
    class Meta:
        model = Book
        fields = ["public_type", "state", "genre", "theme", "min_rating", "is_saga"]