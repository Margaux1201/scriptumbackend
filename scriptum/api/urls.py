from django.urls import path
from .views import UserCreateView, UserLoginView, UserDeleteView, UserRetrieveView, UserUpdateView, BookCreateView, BookRetrieveView, BookListAllView, BookUpdateView, ReviewCreateView, ReviewListView, ChapterCreateView, ChapterRetrieveView, ChapterListView, ChapterUpdateView, CharacterCreateView, CharacterUpdateView, CharacterListView, CharactRetrieveView, CharacterDeleteView, ChapterDeleteView
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
    path('getallbookreviews/<slug:slug>/', ReviewListView.as_view(), name='review-getall'),
    # PARTIE CHAPTER
    path('createchapter/', ChapterCreateView.as_view(), name='chapter-create'),
    path('<slug:slug_book>/getchapterinfo/<slug:slug_chapter>/', ChapterRetrieveView.as_view(), name='chapter-getinfo'),
    path('<slug:slug>/getallchapters/', ChapterListView.as_view(), name='chapter-getall'),
    path('<slug:slug_book>/editchapter/<slug:slug_chapter>/', ChapterUpdateView.as_view(), name='chapter-update'),
    path('<slug:slug_book>/deletechapter/<slug:slug_chapter>/', ChapterDeleteView.as_view(), name='chapter-delete'),
    # PARTIE CHARACTER
    path('createcharacter/', CharacterCreateView.as_view(), name='character-create'),
    path('<slug:slug_book>/updatecharacter/<slug:slug_character>/', CharacterUpdateView.as_view(), name='character-update'),
    path('<slug:slug>/getallcharacters/', CharacterListView.as_view(), name='character-getall'),
    path('<slug:slug_book>/getcharacterinfo/<slug:slug_character>/', CharactRetrieveView.as_view(), name='character-getinfo'),
    path('deletecharacter/<slug:slug_character>/', CharacterDeleteView.as_view(), name='character-delete')
]