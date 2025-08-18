from rest_framework import serializers
from django.conf import settings
from .models import User, Genre, Theme, Book
import json

# Serializer pour créer un utilisateur dans Postgre
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'pseudo', 'first_name', 'last_name', 'author_name', 'email', 'password', 'birth_date', 'token']
        extra_kwargs = {
            'password': {'write_only': True},
            'token': {'read_only': True},
        }
    
    pseudo = serializers.CharField(required=True, allow_blank=False)
    first_name = serializers.CharField(required=True, allow_blank=False)
    last_name = serializers.CharField(required=True, allow_blank=False)
    email = serializers.EmailField(required=True, allow_blank=False)
    birth_date = serializers.DateField(required=True, allow_null=False)
    password = serializers.CharField(write_only=True, required=True, allow_blank=False)

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


# Serializer pour la création d'un livre dans Postgre
class BookSerializer(serializers.ModelSerializer):
    # Définit le typage des données en request
    genres = serializers.CharField(required=True)
    themes = serializers.CharField(required=False, allow_blank=True)
    warnings = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Book
        fields = ['token', 'title', 'description', 'public_type', 'genres', 'themes', 'image', 'state', 'is_saga', 'tome_name', 'tome_number', 'rating', 'warnings']
        read_only_fields = ['rating']


    # Fonction pour créer le roman à a partir du token
    def create(self, validated_data):
        user = self.context['request'].user
        
        # Conversion des M2M et JSON + mise à l'écart de ces données
        genres_data = json.loads(validated_data.pop('genres'))
        themes_data = []
        if 'themes' in validated_data and validated_data['themes']:
            themes_data = json.loads(validated_data.pop('themes'))
        warnings_data = None
        if 'warnings' in validated_data and validated_data['warnings']:
            warnings_data = json.loads(validated_data.pop('warnings'))

        # Création du livre
        book = Book.objects.create(
            author=user,
            warnings=warnings_data,
            **validated_data
            )

        # Ajout des données mise à l'écart en M2M
        genre_objs = [Genre.objects.get_or_create(name=name)[0] for name in genres_data]
        book.genres.set(genre_objs)

        if themes_data:
            theme_objs = [Theme.objects.get_or_create(name=name)[0] for name in themes_data]
            book.themes.set(theme_objs)

        book.update_rating()

        return book