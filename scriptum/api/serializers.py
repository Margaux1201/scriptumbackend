from rest_framework import serializers
from django.conf import settings
from .models import User, Genre, Theme, Book, Review, Chapter
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
    genres = serializers.ListField(child=serializers.CharField())
    themes = serializers.ListField(child=serializers.CharField(), required=False)
    warnings = serializers.JSONField(required=False)
    is_saga = serializers.BooleanField()

    class Meta:
        model = Book
        fields = "__all__"
        read_only_fields = ["author", "slug", "release_date", "rating"]

    def to_internal_value(self, data):
        # Convertir is_saga en booléen si besoin
        if "is_saga" in data:
            value = data["is_saga"]
            if isinstance(value, str):
                data["is_saga"] = value.lower() in ["true", "1", "yes"]
        return super().to_internal_value(data)

    # Fonction pour créer le roman à a partir du token
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['author'] = user
       
        # Extraction des listes de genres / thèmes
        genre_names = validated_data.pop('genres', [])
        theme_names = validated_data.pop('themes', [])

        # Extraire warnings
        warnings_data = self.initial_data.get("warnings")
        if warnings_data:
            validated_data['warnings'] = json.loads(warnings_data)


        # Création du livre
        book = Book(**validated_data)
        print("image:", validated_data['image'])
        book.save()

        # Associer ou créer automatiquement
        genres = [Genre.objects.get_or_create(name=name)[0] for name in genre_names]
        themes = [Theme.objects.get_or_create(name=name)[0] for name in theme_names]

        book.genres.set(genres)
        book.themes.set(themes)

        book.update_rating()

        return book
    
    def update(self, instance, validated_data):

        # Extraire warnings
        warnings_data = self.initial_data.get("warnings")
        if warnings_data:
            validated_data['warnings'] = json.loads(warnings_data)


        # Mettre à jour les champs simples
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # 🔑 Ne mettre à jour que si présent dans la requête
        if 'genres' in self.initial_data:
            genre_names = validated_data.get('genres', [])
            genres = [Genre.objects.get_or_create(name=name)[0] for name in genre_names]
            instance.genres.set(genres)

        if 'themes' in self.initial_data:
            theme_names = validated_data.get('themes', [])
            themes = [Theme.objects.get_or_create(name=name)[0] for name in theme_names]
            instance.themes.set(themes)

        return instance

    
class BookReadSerializer(serializers.ModelSerializer):
    genres = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
    themes = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
    author_name = serializers.CharField(source="author.author_name", read_only=True)

    class Meta:
        model = Book
        fields = "__all__"

class ReviewSerializer(serializers.ModelSerializer):
    book = serializers.SlugRelatedField(
        queryset=Book.objects.all(),
        slug_field='slug'
    )
    book_title = serializers.CharField(source='book.title', read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    user_pseudo = serializers.CharField(source='user.pseudo', read_only=True)

    class Meta:
        model = Review
        fields = "__all__"
        read_only_fields = ['publication_date', 'user']

class ChapterSerializer(serializers.ModelSerializer):
    book = serializers.SlugRelatedField(
        queryset=Book.objects.all(),
        slug_field='slug'
    )
    book_title = serializers.CharField(source='book.title', read_only=True)

    class Meta:
        model = Chapter
        fields = "__all__"
        read_only_fields = ['slug', 'sort_order']