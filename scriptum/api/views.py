from rest_framework import generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import User, Book, Review, Chapter, Character, Place
from .utils import require_token
from .serializers import UserSerializer, LoginSerializer, BookSerializer, BookReadSerializer, ReviewSerializer, ChapterSerializer, CharacterSerializer, PlaceSerializer
from .pagination import BookPagination
from .filters import BookFilter


# PARTIE UTILISATEUR

# POST register/ pour inscrire un utilisateur
class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

#POST login/ pour connecter un utilisateur
class UserLoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            pseudo = serializer.validated_data['pseudo']
            password = serializer.validated_data['password']

            try:
                user = User.objects.get(pseudo=pseudo)
            except User.DoesNotExist:
                return Response({'error': 'Utilisateur non trouvé'}, status=status.HTTP_404_NOT_FOUND)
        
            if user.check_password(password):
                return Response({
                    'pseudo': user.pseudo,
                    'token': str(user.token)
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Mot de passe incorrect'}, status=status.HTTP_401_UNAUTHORIZED)
        
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#DELETE delete/ pour supprimer un compte utilisateur
class UserDeleteView(APIView):
    @require_token
    def delete(self, request):
        user = request.user
        user.delete()
        return Response({"message": "Compte supprimé"}, status=status.HTTP_204_NO_CONTENT)

# POST getinfo/ pour récupérer toutes les données d'un utilisateur
class UserRetrieveView(APIView):
    @require_token
    def post(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

# PUT updateinfo/ pour modifier les données d'un utilisateur
class UserUpdateView(APIView):
    @require_token
    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

# PARTIE ROMAN

# POST createbook/ pour créer un nouveau roman
class BookCreateView(APIView):
    parser_classes = [MultiPartParser]

    @require_token
    def post(self, request):
        serializer = BookSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            book = serializer.save()  # pas besoin de passer author, il est déjà dans create()
            return Response(BookReadSerializer(book).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
# GET getbookinfo/ pour récupérer les données d'un livre
class BookRetrieveView(APIView):
    def get(self, request, slug):
        try:
            book = Book.objects.get(slug=slug)
        except Book.DoesNotExist:
            return Response({'error': 'Livre non trouvé'}, status=status.HTTP_404_NOT_FOUND)

        serializer = BookReadSerializer(book, context={'request': request})
        return Response(serializer.data)

# GET getallbook/ pour récupérer tous les livres
class BookListAllView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookReadSerializer
    pagination_class = BookPagination

    # Ajout des filtres de recherche
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BookFilter

    # Recherche textuelle
    search_fields = ["title", "description", "author__author_name", "tome_name"]

    # Tri
    ordering_fields = ["release_date", "rating", "title"]
    ordering = ["-release_date", "-rating", "title"] #ordre par défaut

# PUT editbook/ pour modifier des éléments du livre
class BookUpdateView(APIView):
    parser_classes = [MultiPartParser, JSONParser]

    @require_token
    def patch(self, request,slug):
        try:
            book = Book.objects.get(slug=slug)
        except Book.DoesNotExist:
            return Response({'error': 'Livre non trouvé'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BookSerializer(book, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(BookReadSerializer(book).data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
# POST createreview/ pour créer une nouvelle review
class ReviewCreateView(APIView):
    @require_token

    def post(self, request, *args, **kwargs):
        serializer = ReviewSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# GET getallbookreviews/ pour récupérer toutes les reviews d'un livre
class ReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        return Review.objects.filter(book__slug=slug).order_by('-publication_date')
    

# PARTIE CHAPITRE

# POST createchapter/ pour créer un nouveau chapitre
class ChapterCreateView(APIView):
    @require_token

    def post(self, request, *args, **kwargs):
        serializer = ChapterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# GET getchapterinfo/ pour récupérer les données d'un chapitre
class ChapterRetrieveView(APIView):
    def get(self, request, slug_book, slug_chapter):
        chapter = get_object_or_404(Chapter, book__slug=slug_book, slug=slug_chapter)
        serializer = ChapterSerializer(chapter, context={'request': request})
        return Response(serializer.data)
    
# GET getallchapters/ pour récupérer tous les chapitres d'un livre
class ChapterListView(generics.ListAPIView):
    serializer_class = ChapterSerializer

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        return Chapter.objects.filter(book__slug=slug).order_by('sort_order')
    
# PUT editchapter/ pour modifier des éléments du chapitre
class ChapterUpdateView(APIView):
    @require_token
    def patch(self, request, slug_book, slug_chapter): 
        chapter = get_object_or_404(Chapter, book__slug=slug_book, slug=slug_chapter)
        serializer = ChapterSerializer(chapter, data=request.data, partial=True)

        if chapter.book.author != request.user:
            return Response({'error': 'Permission refusée'}, status=status.HTTP_403_FORBIDDEN)

        if serializer.is_valid():
            serializer.save()
            return Response(ChapterSerializer(chapter).data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
# DELETE deletechapter/ pour supprimer un chapitre
class ChapterDeleteView(APIView):
    @require_token
    def delete(self, request, slug_book, slug_chapter):
        chapter = get_object_or_404(Chapter, book__slug=slug_book, slug=slug_chapter)

        if chapter.book.author != request.user:
            return Response({"error": "non autorisé"}, status=status.HTTP_403_FORBIDDEN)
        
        chapter.delete()
        return Response({"message": "Chapitre supprimé"}, status=status.HTTP_204_NO_CONTENT)
    
    
# PARTIE PERSONNAGE
        
# POST createcharacter/ pour créer un nouveau personnage
class CharacterCreateView(APIView):
    parser_classes = [MultiPartParser]
    @require_token

    def post(self, request, *args, **kwargs):
        serializer = CharacterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# PUT updatecharacter/ pour modifier les infos d'un personnage
class CharacterUpdateView(APIView):
    parser_classes = [MultiPartParser, JSONParser]

    @require_token

    def patch(self, request, slug_book, slug_character):
        character = get_object_or_404(Character, book__slug=slug_book, slug=slug_character)
        serializer = CharacterSerializer(character, data=request.data, partial=True)

        if character.book.author != request.user:
            return Response({'error': 'Permission refusée'}, status=status.HTTP_403_FORBIDDEN)

        if serializer.is_valid():
            serializer.save()
            return Response(CharacterSerializer(character).data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
# GET getallcharacters/ pour afficher tous les personnages d'un livre
class CharacterListView(generics.ListAPIView):
    serializer_class = CharacterSerializer

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        return Character.objects.filter(book__slug=slug).order_by('name')
    
# GET getcharacterinfo/ pour afficher toutes les informations d'un personnage
class CharactRetrieveView(APIView):
    def get(self, request, slug_book, slug_character):
        character = get_object_or_404(Character, book__slug=slug_book, slug=slug_character)
        serializer = CharacterSerializer(character, context={'request': request})
        return Response(serializer.data)
    
#DELETE deletecharacter/ pour supprimer un compte utilisateur
class CharacterDeleteView(APIView):
    @require_token
    def delete(self, request, slug_book, slug_character):  
        character = get_object_or_404(Character, book__slug=slug_book, slug=slug_character)

        if character.book.author != request.user:
            return Response({"error": "non autorisé"}, status=status.HTTP_403_FORBIDDEN)
        
        character.delete()
        return Response({"message": "Personnage supprimé"}, status=status.HTTP_204_NO_CONTENT)
    

# PARTIE LIEUX

# POST createplace/ pour créer un lieu d'un roman
class PlaceCreateView(APIView):
    parser_classes = [MultiPartParser]
    @require_token
    def post(self, request, *args, **kwargs):
        serializer = PlaceSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# GET getallplaces/ pour afficher tous les lieux d'un livre
class PlaceListView(generics.ListAPIView):
    serializer_class = PlaceSerializer

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        return Place.objects.filter(book__slug=slug).order_by('name')
    
# GET getinfoplace/ pour obtenir le détail d'un lieu
class PlaceRetrieveView(APIView):
    def get(self, request, slug_book, slug_place):
        place = get_object_or_404(Place, book__slug=slug_book, slug=slug_place)
        serializer = PlaceSerializer(place, context={"request": request})
        return Response(serializer.data)
    
# PUT updateplace/ pour modifier un lieu d'un roman
class PlaceUpdateView(APIView):
    parser_classes = [MultiPartParser, JSONParser]
    @require_token

    def patch(self, request, slug_book, slug_place):
        place = get_object_or_404(Place, book__slug=slug_book, slug=slug_place)
        serializer = PlaceSerializer(place, data=request.data, partial=True)

        if place.book.author != request.user:
            return Response({"error": "Permission refusée"}, status=status.HTTP_403_FORBIDDEN)
        
        if serializer.is_valid():
            serializer.save()
            return Response(PlaceSerializer(place).data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# DELETE deleteplace/ pour supprimer un lieu d'un roman
class PlaceDeleteView(APIView):
    @require_token

    def delete(self, request, slug_book, slug_place):
        place = get_object_or_404(Place, book__slug=slug_book, slug=slug_place)
        
        if place.book.author != request.user:
            return Response({'error': 'Permission refusée'}, status=status.HTTP_403_FORBIDDEN)
        
        place.delete()
        return Response({"message": "Lieu supprimé"}, status=status.HTTP_204_NO_CONTENT)