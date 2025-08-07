from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User
from .utils import require_token
from .serializers import UserSerializer, LoginSerializer

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