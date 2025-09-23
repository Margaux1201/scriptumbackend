from rest_framework import serializers
from django.conf import settings
from .models import User, Genre, Theme, Book, Review, Chapter, Character, Place, Creature, Favorite, FollowedAuthor
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
        print(self.initial_data)
        print(validated_data)
        # Créer un dict standard à partir de initial_data
        data = dict(self.initial_data)  # 🔑 dict Python standard

        # Genres
        genre_names = data.get("genres")
        if genre_names:
            if isinstance(genre_names, list):
                genres_list = genre_names
            else:
                # Si FormData, genre_names peut être une string ou QueryDict lists
                genres_list = self.initial_data.getlist("genres")
            genres = [Genre.objects.get_or_create(name=name)[0] for name in genres_list]
            instance.genres.set(genres)

        # Themes
        theme_names = data.get("themes")
        if theme_names:
            if isinstance(theme_names, list):
                themes_list = theme_names
            else:
                themes_list = self.initial_data.getlist("themes")
            themes = [Theme.objects.get_or_create(name=name)[0] for name in themes_list]
            instance.themes.set(themes)

        # Champs simples
        m2m_fields = ['genres', 'themes']
        for attr, value in validated_data.items():
            if attr in m2m_fields:
                continue  # déjà géré avec .set()
            setattr(instance, attr, value)

        instance.save()
        return instance
    
class BookReadSerializer(serializers.ModelSerializer):
    genres = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
    themes = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
    author_name = serializers.CharField(source="author.author_name", read_only=True)
    author_token = serializers.CharField(source="author.token", read_only=True)

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

class CharacterSerializer(serializers.ModelSerializer):
    book = serializers.SlugRelatedField(
        queryset=Book.objects.all(),
        slug_field='slug'
    )
    zodiac_sign = serializers.ReadOnlyField()
    job = serializers.JSONField(required=False)
    traits = serializers.JSONField(required=False)
    languages = serializers.JSONField(required=False)
    studies = serializers.JSONField(required=False)
    family = serializers.JSONField(required=False)
    addictions = serializers.JSONField(required=False)
    fears = serializers.JSONField(required=False)
    talents = serializers.JSONField(required=False)

    class Meta:
        model = Character
        fields = "__all__"
        read_only_fields = ['slug', 'book']

class PlaceSerializer(serializers.ModelSerializer):
    book = serializers.SlugRelatedField(
        queryset=Book.objects.all(),
        slug_field='slug'
    )
    class Meta:
        model = Place
        fields = "__all__"
        read_only_fields = ['book', 'slug']

class CreatureSerializer(serializers.ModelSerializer):
    book = serializers.SlugRelatedField(
        queryset=Book.objects.all(),
        slug_field='slug'
    )
    class Meta:
        model = Creature
        fields = "__all__"
        read_only_fields = ['book', 'slug']

class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    book = serializers.SlugRelatedField(queryset=Book.objects.all(), slug_field='slug')
    user_pseudo = serializers.CharField(source='user.pseudo', read_only=True)
    book_image = serializers.ImageField(source='book.image', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_state = serializers.CharField(source='book.state', read_only=True)
    book_author = serializers.CharField(source='book.author.author_name', read_only=True)
    book_rating = serializers.FloatField(source='book.rating', read_only=True)

    class Meta:
        model = Favorite
        fields = "__all__"


class AuthorWithBooksSerializer(serializers.ModelSerializer):
    books = BookReadSerializer(many=True, read_only=True)

    class Meta:
        model= User
        fields = ["author_name", "books"]

class FollowedAuthorSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    author = AuthorWithBooksSerializer(read_only=True)

    author_name = serializers.SlugRelatedField(
        slug_field="author_name",
        queryset=User.objects.all(),
        source="author",
        write_only=True
    )

    class Meta:
        model = FollowedAuthor
        fields = "__all__"