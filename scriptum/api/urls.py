from django.urls import path
from .views import UserCreateView, UserLoginView, UserDeleteView, UserRetrieveView, UserUpdateView, BookCreateView, BookRetrieveView, BookListAllView, BookUpdateView, ReviewCreateView, ReviewListView
urlpatterns = [
    # PARTIE USER
    path('register/', UserCreateView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('delete/', UserDeleteView.as_view(), name='user-delete'),
    path('getinfo/', UserRetrieveView.as_view(), name='user-getinfo'),
    path('updateinfo/', UserUpdateView.as_view(), name='user-updateinfo'),
    # PARTIE BOOK
    path('createbook/', BookCreateView.as_view(), name='book-create'),
    path('getbookinfo/<slug:slug>/', BookRetrieveView.as_view(), name='book-getinfo'),
    path('getallbook/', BookListAllView.as_view(), name='book-getall'),
    path('editbook/<slug:slug>/', BookUpdateView.as_view(), name='book-update'),
    # PARTIE REVIEW
    path('createreview/', ReviewCreateView.as_view(), name='review-create'),
    path('getallbookreviews/<slug:slug>/', ReviewListView.as_view(), name='review-getall')
]