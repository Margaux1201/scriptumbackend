from rest_framework import generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import User, Book, Review, Chapter, Character, Place, Creature, Favorite, FollowedAuthor
from .utils import require_token
from .serializers import UserSerializer, LoginSerializer, BookSerializer, BookReadSerializer, ReviewSerializer, ChapterSerializer, CharacterSerializer, PlaceSerializer, CreatureSerializer, FavoriteSerializer, FollowedAuthorSerializer
from .pagination import BookPagination
from .filters import BookFilter
from django.db import IntegrityError
from django.http import JsonResponse


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
            try:
                serializer.save()
                return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
            except IntegrityError as e:
                return Response({'error': "Ce pseudo ou cet email est déjà utilisé."}, status=status.HTTP_400_BAD_REQUEST)
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
    ordering = ["-rating", "-release_date", "title"] #ordre par défaut

# GET getallauthorbook/ pour récupérer tous les livres d'un auteur
class BookListByAuthorView(generics.ListAPIView):
    serializer_class = BookReadSerializer
    pagination_class = None

    def get_queryset(self):
        token = self.kwargs.get('token')
        return Book.objects.filter(author__token=token)


# PUT editbook/ pour modifier des éléments du livre
class BookUpdateView(APIView):
    parser_classes = [MultiPartParser, JSONParser]

    @require_token
    def patch(self, request,slug):
        try:
            book = Book.objects.get(slug=slug)
        except Book.DoesNotExist:
            return Response({'error': 'Livre non trouvé'}, status=status.HTTP_404_NOT_FOUND)
        
         # 🔑 convertir request.data en dict mutable
        mutable_data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        
        serializer = BookSerializer(book, data=mutable_data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(BookReadSerializer(book).data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
              
# DELETE deletebook/ pour supprimer un livre
class BookDeleteView(APIView):
    @require_token

    def delete(self, request, slug):
        book = get_object_or_404(Book, slug=slug)

        if book.author != request.user:
            return Response({"error": "Vous devez être l'auteur de ce livre pour le supprimer"}, status=status.HTTP_403_FORBIDDEN)

        book.delete()
        return Response({"message": "Le livre a été supprimé"}, status=status.HTTP_204_NO_CONTENT)   

# PARTIE REVIEW
        
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
    pagination_class = None

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        return Chapter.objects.filter(book__slug=slug).order_by('sort_order', 'chapter_number')
    
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
    pagination_class = None

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
    pagination_class = None

    def get_queryset(self):
        slug = self.kwargs.get('slug_book')
        return Place.objects.filter(book__slug=slug)
    
# GET getinfoplace/ pour obtenir le détail d'un lieu
class PlaceRetrieveView(APIView):
    def get(self, request, slug_book, slug_place):
        place = get_object_or_404(Place, book__slug=slug_book, slug=slug_place)
        serializer = PlaceSerializer(place, context={"request": request})
        return Response(serializer.data)
    
# PATCH updateplace/ pour modifier un lieu d'un roman
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
    

# PARTIE CREATURE


# POST createcreature/ pour créer une créature
class CreatureCreateView(APIView):
    parser_classes = [MultiPartParser]
    @require_token

    def post(self, request, *args, **kwargs):
        serializer = CreatureSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# GET getallcreatures/ pour afficher toutes les créatures d'un livre
class CreatureListView(generics.ListAPIView):
    serializer_class = CreatureSerializer
    pagination_class = None

    def get_queryset(self):
        slug = self.kwargs.get('slug_book')
        return Creature.objects.filter(book__slug=slug)

# GET getinfocreature/ pour récupérer les détails d'une créature
class CreatureRetrieveView(APIView):

    def get(self, request, slug_book, slug_creature):
        creature = get_object_or_404(Creature, book__slug=slug_book, slug=slug_creature)
        serializer = CreatureSerializer(creature, context={"request": request})
        return Response(serializer.data)
    
# PATCH updatecreature/ pour modifier une créature
class CreatureUpdateView(APIView):
    parser_classes=[MultiPartParser, JSONParser]
    @require_token

    def patch(self, request, slug_book, slug_creature):
        creature = get_object_or_404(Creature, book__slug=slug_book, slug=slug_creature)
        serializer = CreatureSerializer(creature, data=request.data, partial=True)

        if creature.book.author != request.user:
            return Response({"error": "utilisateur non autorisé"}, status=status.HTTP_403_FORBIDDEN)
        
        if serializer.is_valid():
            serializer.save()
            return Response(CreatureSerializer(creature).data, status=status.HTTP_200_OK)
        else :
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# DELETE deletecreature/ pour supprimer une créature
class CreatureDeleteView(APIView):
    @require_token

    def delete(self, request, slug_book, slug_creature):
        creature = get_object_or_404(Creature, book__slug=slug_book, slug=slug_creature)

        if creature.book.author != request.user:
            return Response({"error": "utilisateur non autorisé"}, status=status.HTTP_403_FORBIDDEN)
        
        creature.delete()
        return Response({"message": "créature supprimée"}, status=status.HTTP_204_NO_CONTENT)
    

# PARTIE FAVORITE

# POST newfavorite/ pour créer un nouveau favori d'un utilisateur
class FavoriteCreateView(APIView):
    @require_token

    def post(self, request, *args, **kwargs):
        serializer = FavoriteSerializer(data=request.data)

        if serializer.is_valid():

            # Récupérer le livre choisi par le slug
            book = serializer.validated_data["book"]

            if Favorite.objects.filter(user=request.user, book=book).exists():
                return Response(
                    {"error": "Ce livre est déjà dans vos favoris."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# DELETE deletefavorite/ pour supprimer un favori d'un utilisateur
class FavoriteDeleteView(APIView):
    @require_token

    def delete(self, request, slug_book, *args, **kwargs):
        favorite_book = get_object_or_404(Favorite, user=request.user, book__slug=slug_book)

        favorite_book.delete()
        return Response({"message": "Le livre a été supprimé des favoris de l'utilisateur"}, status=status.HTTP_204_NO_CONTENT)
    
# GET getallfavorite/ pour récupérer tous les favoris d'un utilisateur
class FavoriteListView(generics.ListAPIView):
    serializer_class = FavoriteSerializer
    pagination_class = None

    def get_queryset(self):
        token = self.kwargs.get('token')
        user = get_object_or_404(User, token=token)
        return Favorite.objects.filter(user=user)
    

# PARTIE AUTEUR SUIVI

# POST newfollowedauthor/ pour créer le suivi d'un auteur par un utilisateur
class FollowedAuthorCreateView(APIView):
    @require_token

    def post(self, request, *args, **kwargs):
        serializer= FollowedAuthorSerializer(data=request.data)

        if serializer.is_valid():

            author = serializer.validated_data["author"]

            if FollowedAuthor.objects.filter(user=request.user, author=author).exists():
                return Response({"error": "Cet auteur est déjà dans vos suivis."}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# DELETE deletefollowedauthor/ pour supprimer le suivi d'un auteur par un utilisateur
class FollowedAuthorDeleteView(APIView):
    @require_token

    def delete(self, request, author_name, *args, **kwargs):
        followed_author  = get_object_or_404(FollowedAuthor, user=request.user, author__author_name=author_name)

        followed_author .delete()
        return Response({"message": f"{author_name} a été supprimé des suivis de l'utilisateurs"}, status=status.HTTP_204_NO_CONTENT)
    
# GET getallfollowedauthors/ pour récupérer tous les auteurs suivis de l'utilisateurs
class FollowedAuthorListView(generics.ListAPIView):
    serializer_class = FollowedAuthorSerializer
    pagination_class = None

    def get_queryset(self):
        token = self.kwargs.get('token')
        user = get_object_or_404(User, token=token)
        return FollowedAuthor.objects.filter(user=user)
    

# TEST REQUETE DEPLOIEMENT

def healthcheck(request):
    try:
        count = Chapter.objects.count()
        return JsonResponse({"ok": True, "chapters_in_db": count})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)})