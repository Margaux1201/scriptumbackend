from django.urls import path
from .views import UserCreateView, UserLoginView, UserDeleteView, UserRetrieveView, UserUpdateView, BookCreateView, BookRetrieveView, BookListAllView, BookUpdateView, ReviewCreateView, ReviewListView, ChapterCreateView, ChapterRetrieveView, ChapterListView, ChapterUpdateView, CharacterCreateView, CharacterUpdateView, CharacterListView, CharactRetrieveView, CharacterDeleteView, ChapterDeleteView, PlaceCreateView, PlaceListView, PlaceRetrieveView, PlaceUpdateView, PlaceDeleteView, CreatureCreateView, CreatureListView, CreatureRetrieveView, CreatureUpdateView, CreatureDeleteView, BookListByAuthorView, BookDeleteView, FavoriteCreateView, FavoriteDeleteView, FavoriteListView, FollowedAuthorCreateView, FollowedAuthorDeleteView, FollowedAuthorListView
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
    path('<uuid:token>/getallauthorbook/', BookListByAuthorView.as_view(), name='book-getallbyauthor'),
    path('deletebook/<slug:slug>/', BookDeleteView.as_view(), name='book-delete'),
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
    path('<slug:slug_book>/deletecharacter/<slug:slug_character>/', CharacterDeleteView.as_view(), name='character-delete'),
    # PARTIE PLACE
    path('createplace/', PlaceCreateView.as_view(), name='place-create'),
    path('<slug:slug_book>/updateplace/<slug:slug_place>/', PlaceUpdateView.as_view() , name="place-update"),
    path('<slug:slug_book>/getallplaces/', PlaceListView.as_view(), name='place-getall'),
    path('<slug:slug_book>/getinfoplace/<slug:slug_place>/', PlaceRetrieveView.as_view(), name='place-getinfo'),
    path('<slug:slug_book>/deleteplace/<slug:slug_place>/', PlaceDeleteView.as_view(), name='place-delete'),
    # PARTIE CREATURE
    path('createcreature/', CreatureCreateView.as_view(), name='creature-create'),
    path('<slug:slug_book>/updatecreature/<slug:slug_creature>/', CreatureUpdateView.as_view() , name="creature-update"),
    path('<slug:slug_book>/getallcreatures/', CreatureListView.as_view(), name='creature-getall'),
    path('<slug:slug_book>/getinfocreature/<slug:slug_creature>/', CreatureRetrieveView.as_view(), name='creature-getinfo'),
    path('<slug:slug_book>/deletecreature/<slug:slug_creature>/', CreatureDeleteView.as_view(), name='creature-delete'),
    # PARTIE FAVORITE
    path('newfavorite/', FavoriteCreateView.as_view(), name='favorite-create'),
    path('deletefavorite/<slug:slug_book>/', FavoriteDeleteView.as_view(), name='favorite-delete'),
    path('getallfavorite/<uuid:token>/', FavoriteListView.as_view(), name='favorite-getall'),
    # PARTIE AUTEUR SUIVI
    path('newfollowedauthor/', FollowedAuthorCreateView.as_view(), name='followedauthor-create'),
    path('deletefollowedauthor/<str:author_name>/', FollowedAuthorDeleteView.as_view(), name='followedauthor-delete'),
    path('getallfollowedauthors/<uuid:token>/', FollowedAuthorListView.as_view(), name='followedauthor-getall')
]