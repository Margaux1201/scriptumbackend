from rest_framework import generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Book
from .utils import require_token
from .serializers import UserSerializer, LoginSerializer, BookSerializer, BookReadSerializer
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
            return Response(serializer.data, status=status.HTTP_200_OK)
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
    serializer_class = BookSerializer
    pagination_class = BookPagination

    # Ajout des filtres de recherche
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BookFilter

    # Recherche textuelle
    search_fields = ["title", "description", "author__author_name"]

    # Tri
    ordering_fields = ["title", "release_date", "rating"]
    ordering = ["release_date"] #ordre par défaut