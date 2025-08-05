from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User
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