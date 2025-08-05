from rest_framework import serializers
from .models import User

# Serializer pour créer un utilisateur dans Postgre
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'pseudo', 'first_name', 'last_name', 'author_name', 'email', 'password', 'birth_date', 'token']
        extra_kwargs = {
            'password': {'write_only': True},
            'token': {'read_only': True},
        }
    
    def create(self, validated_data):
        user = User(
            pseudo=validated_data['pseudo'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            author_name=validated_data.get('author_name'),
            email=validated_data['email'],
            birth_date=validated_data['birth_date']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
# Serializer pour la connexion d'un utilisateur
class LoginSerializer(serializers.Serializer):
    # pas de ModelSerializer car on n'enregistre rien dans la BDD => valide seulement les données de connexion
    pseudo = serializers.CharField()
    password = serializers.CharField(write_only=True)