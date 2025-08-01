import uuid
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


# Modèle pour créer la table utilisateur
class User(models.Model):
    pseudo = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    author_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    birth_date = models.DateField()
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # Fonction pour créer le mot de passe
    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    # Fonction pour vérifier le mot de passe
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

# Modèle pour stocker les genres d'un livre
class Genre(models.Model):
    name = models.CharField(max_length=30, unique=True)

# Modèle pour stocker les thèmes d'un livre
class Theme(models.Model):
    name = models.CharField(max_length=30, unique=True)

# Modèle pour créer la table livre
class Book(models.Model):
    # Variable pour les choix du type de public
    PUBLIC_CHOICES = [
        ('jeunesse', 'Jeunesse'),
        ('young_adult', 'Young Adult'),
        ('adulte', 'Adulte'),
    ]

    title = models.CharField(max_length=50)
    release_date = models.DateField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='books')
    description = models.TextField()
    public_type = models.CharField(max_length=20, choices=PUBLIC_CHOICES) # Type de public avec la variable PUBLIC_CHOICES
    genres = models.ManyToManyField(Genre, related_name='books')
    themes = models.ManyToManyField(Theme, related_names='books')
    image = models.ImageField(upload_to='book_images/')
    state = models.CharField(max_length=20, default='En cours')
    is_saga = models.BooleanField(default=False)
    tome_name = models.CharField(max_length=30, null=True, blank=True)
    tome_number = models.IntegerField(null=True, blank=True)
    rating = models.FloatField(default=0.0)

    def clean(self):
        # Vérifie que le nom et numéro du tome sont cohérents avec le statut de saga
        if not self.is_saga and (self.tome_name or self.tome_number):
            raise ValidationError("Le nom et le numéro du tome ne doivent pas être renseignés si ce n'est pas une saga.")
        if self.is_saga and (not self.tome_name or not self.tome_number):
            raise ValidationError("Le nom et le numéro du tome doivent être renseignés pour une saga.")
        # Vérifie que le nombre de genres et de thèmes ne dépasse pas les limites
        if self.genres.count() > 5:
            raise ValidationError("Un livre ne peut pas avoir plus de 5 genres.")
        if self.themes.count() > 10:
            raise ValidationError("Un livre ne peut pas avoir plus de 10 thèmes")
    
    # Met à jour la note du livre en fonction de toutes ses scores de reviews associées
    def update_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            total = sum([review.score for review in reviews])
            self.rating = round(total / reviews.count(), 1)
        else:
            self.rating = 0.0
        self.save()

# Modèle pour stocker toutes les reviews des livres
class Review(models.Model):
    book = models.ForeignKey(Book, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    comment = models.TextField(blank=True)

# Modèle pour créer la table de Chapitre
class Chapter(models.Model):
    # Variable pour les choix du type de chapitre
    TYPE_CHOICES = [
        ('prologue', 'Prologue'),
        ('chapitre', 'Chapitre'),
        ('epilogue', 'Epilogue'),
    ]

    book = models.ForeignKey(Book, related_names='chapters', on_delete=models.CASCADE)
    title = models.CharField(max_length=50, blank=True, null=True)
    content = models.TextField()
    type = models.CharField(max_length=10, choices=TYPE_CHOICES) # Type de chapitre avec la variable TYPE_CHOICES
    chapter_number = models.IntegerField(null=True, blank=True)

    # Vérifie la cohérence du type de chapitre et du numéro de chapitre
    def clean(self):
        if self.type == 'chapitre' and self.chapter_number is None:
            raise ValidationError("Le numéro de chapitre doit être renseigné pour un chapitre.")
        if self.type != 'chapitre' and self.chapter_number is not None:
            raise ValidationError("L'épilogue et le prologue ne doivent pas avoir de numéro de chapitre.")

# Modèle pour stocker les commentaires des utilisateurs sur les chapitres
class ChapterComment(models.Model):
    chapter = models.ForeignKey(Chapter, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    publication_date = models.DateTimeField(auto_now_add=True)
    content = models.TextField(max_length=500)

# Modèle pour stocker les favoris des utilisateurs
class Favorite(models.Model):
    user = models.ForeignKey(User, related_name='favorites', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='favorites', on_delete=models.CASCADE)

# Modèle pour stocker les auteurs suivis par les utilisateurs
class FollowedAuthor(models.Model):
    user = models.ForeignKey(User, related_name='followed_authors', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)

    # Vérifie que l'utilisateur ne se suit pas lui-même
    def clean(self):
        if self.user == self.author:
            raise ValidationError("Un utilisateur ne peut pas se suivre lui-même")

# Modèle pour créer la table de Lieux
class Place(models.Model):
    name = models.CharField(max_length=30)
    image = models.ImageField(upload_to='place_images/')
    content = models.TextField(max_length=1000)
    book = models.ForeignKey(Book, related_name='places', on_delete=models.CASCADE)

# Modèle pour créer la table de Créatures
class Creature(models.Model):
    name = models.CharField(max_length=30)
    image = models.ImageField(upload_to='creature_images/')
    content = models.TextField(max_length=1000)
    book = models.ForeignKey(Book, related_name='creatures', on_delete=models.CASCADE)

# Modèle pour créer la table de Personnages
class Character(models.Model):
    ROLE_CHOICES = [
        ('protagoniste', 'Protagoniste'),
        ('antagoniste', 'Antagoniste'),
        ('allié', 'Allié'),
        ('adversaire', 'Adversaire'),
        ('neutre', 'Neutre')
    ]
    SEXE_CHOICES = [
        ('masculin', 'Masculin'),
        ('féminin', 'Féminin'),
        ('autre', 'Autre')
    ]
    RELATION_CHOICES = [
        ('célibataire', 'Célibataire'),
        ('en couple', 'En couple'),
        ('fiancé.e', 'Fiancé.e'),
        ('marié.e', 'Marié.e'),
        ('divorcé.e', 'Divorcé.e'),
        ('veuf.ve', 'Veuf.ve')
    ]

    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    image = models.ImageField(upload_to='character_images/')
    age = models.IntegerField()
    sexe = models.CharField(max_length=10, choices=SEXE_CHOICES)
    height = models.CharField(max_length=10)
    background = models.TextField(max_length=1000)
    book = models.ForeignKey(Book, related_name='characters', on_delete=models.CASCADE)
    species = models.CharField(max_length=30, default='Humain')
    is_there_race = models.BooleanField(default=False)
    race = models.CharField(max_length=30, blank=True, null=True)
    character_trait = models.JSONField(blank=True, null=True)
    day_birth = models.IntegerField(blank=True, null=True)
    month_birth =  models.IntegerField(blank=True, null=True)
    hometown = models.CharField(max_length=30, blank=True, null=True)
    language = models.CharField(max_length=30, blank=True, null=True)
    study = models.JSONField(blank=True, null=True)
    job = models.JSONField(blank=True, null=True)
    relation = models.CharField(blank=True, null=True, max_length=20, choices=RELATION_CHOICES)
    family = models.JSONField(blank=True, null=True)
    addiction = models.JSONField(blank=True, null=True)
    religion = models.CharField(max_length=30, blank=True, null=True)
    fear = models.CharField(max_length=30, blank=True, null=True)
    talent = models.CharField(max_length=30, blank=True, null=True)


    @property
    def zodiac_sign(self):
        if self.day_birth is None or self.month_birth is None:
            return None

        day = self.day_birth
        month = self.month_birth

        if (month == 1 and day >= 20) or (month == 2 and day <= 18):
            return "Verseau"
        elif (month == 2 and day >= 19) or (month == 3 and day <= 20):
            return "Poissons"
        elif (month == 3 and day >= 21) or (month == 4 and day <= 19):
            return "Bélier"
        elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
            return "Taureau"
        elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
            return "Gémeaux"
        elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
            return "Cancer"
        elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
            return "Lion"
        elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
            return "Vierge"
        elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
            return "Balance"
        elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
            return "Scorpion"
        elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
            return "Sagittaire"
        elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
            return "Capricorne"
        else:
            return None

    def clean(self):
        #Vérifie que les traits de cractère ne dépassent pas 10
        if self.character_trait and len(self.character_trait) > 10:
            raise ValidationError("Un personnage ne peut pas avoir plus de 10 traits de caractère.")
        # Vérifie la cohérence entre le nom de la race et le statut
        if self.is_there_race and not self.race:
            raise ValidationError("La race doit être renseignée")
        if not self.is_there_race and self.race:
            raise ValidationError("Le personnage n'a pas de race à renseigner")
        # Vérifie que le jour et le mois de naissance sont valides
        if self.day_birth and (self.day_birth < 1 or self.day_birth > 31):
            raise ValidationError("Le jour de naissance doit être compris entre 1 et 31.")
        if self.month_birth and (self.month_birth < 1 or self.month_birth > 12):
            raise ValidationError("Le mois de naissance doit être compris entre 1 et 12.")
    
