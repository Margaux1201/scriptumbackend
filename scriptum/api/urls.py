from django.urls import path
from .views import UserCreateView, UserLoginView, UserDeleteView, UserRetrieveView, UserUpdateView, BookCreateView, BookRetrieveView, BookListAllView

urlpatterns = [
    # PARTIE USER
    path('register/', UserCreateView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('delete/', UserDeleteView.as_view(), name='user-delete'),
    path('getinfo/', UserRetrieveView.as_view(), name='user-getinfo'),
    path('updateinfo/', UserUpdateView.as_view(), name='user-updateinfo'),
    # PARTIE BOOK
    path('createbook/', BookCreateView.as_view(), name='book-create'),
    path('getbookinfo/', BookRetrieveView.as_view(), name='book-getinfo'),
    path('getallbook/', BookListAllView.as_view(), name='book-getall')
]