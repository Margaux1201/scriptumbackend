# API Backend Scriptum

API Backend pour Scriptum, une plateforme d'écriture de livres construite avec Django et PostgreSQL.

## 🛠 Stack Technique

- Django 5.2.4
- PostgreSQL
- Django REST Framework
- Python-dotenv
- Cloudinary (pour le stockage des médias)

## 📋 Prérequis

- Python 3.x
- PostgreSQL
- pip

## 🚀 Installation

1. Cloner le dépôt
```bash
git clone <url-du-dépôt>
cd backend/scriptum
```

2. Créer un environnement virtuel
```bash
python -m venv venv
source venv/Scripts/activate  # Sur Windows
```

3. Installer les dépendances
```bash
pip install -r requirements.txt
```

4. Créer le fichier .env dans scriptum/scriptum/
```
SECRET_KEY=votre_clé_secrète
DEBUG=True
DB_NAME=scriptum_db
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=5432
CLOUDINARY_CLOUD_NAME=votre_nom_cloud
CLOUDINARY_API_KEY=votre_clé_api
CLOUDINARY_API_SECRET=votre_secret_api
```

5. Exécuter les migrations
```bash
python manage.py migrate
```

6. Démarrer le serveur de développement
```bash
python manage.py runserver
```

## 📚 Points de Terminaison API

1. 🧑‍💼 PARTIE UTILISATEUR
    - `POST /api/register/`: Créer un nouvel utilisateur
    - `POST /api/login/`: Connecter l'utilisateur
    - `DELETE /api/delete/`: Supprimer l'utilisateur
    - `POST /api/getinfo/`: Récupérer les informations de l'utilisateur (à adapter en GET avec le token en params)
    - `PUT /api/updateinfo/`: Modifier les informations de l'utilisateur

2. 📖 PARTIE LIVRE
    - `POST /api/createbook/`: Créer un nouveau livre
    - `GET /api/getbookinfo/<slug:slug>/`: Récupérer les données du livre, à partir de son slug
    - `GET /api/getallbook/`: Récupérer tous les livres stockés dans la base de données
    - `PATCH /api/editbook/<slug:slug>/`: Modifier les informations d'un livre, à partir de son slug
    - `GET /api/<uuid:token>/getallauthorbook/`: Récupérer tous les livres d'un auteur, à partir de son token utilisateur
    - `DELETE /api/deletebook/<slug:slug>/`: Supprimer un livre, à partir de son slug

3. ⭐ PARTIE REVIEW
    - `POST /api/createreview/`: Créer une nouvelle review
    - `GET /api/getallbookreviews/<slug:slug>`: Récupérer les reviews d'un livre, à partir de son slug
    
4. 📃 PARTIE CHAPITRE
    - `POST /api/createchapter/`: Créer un nouveau chapitre
    - `GET /api/<slug:slug_book>/getchapterinfo/<slug:slug_chapter>/`: Récupérer les données d'un chapitre, à partir de son slug et du slug du livre
    - `GET /api/<slug:slug>/getallchapters/`: Récupérer tous les chapitres d'un livre, à partir de son slug
    - `PATCH /api/<slug:slug_book>/editchapter/<slug:slug_chapter>/`: Modifier les informations d'un chapitre, à partir de son slug et du slug du livre
    - `DELETE /api/<slug:slug_book>/deletechapter/<slug:slug_chapter>/`: Supprimer un chapitre, à partir de son slug et du slug du livre

5. 🦸 PARTIE PERSONNAGE
    - `POST /api/createcharacter/`: Créer un nouveau personnage
    - `GET /api/<slug:slug_book>/getcharacterinfo/<slug:slug_character>/`: Récupérer les données d'un personnage, à partir de son slug et du slug du livre
    - `GET /api/<slug:slug>/getallcharacters/`: Récupérer tous les personnages d'un livre, à partir de son slug
    - `PATCH /api/<slug:slug_book>/updatecharacter/<slug:slug_character>/`: Modifier les informations d'un personnage, à partir de son slug et du slug du livre
    - `DELETE /api/<slug:slug_book>/deletecharacter/<slug:slug_character>/`: Supprimer un personnage, à partir de son slug et du slug du livre

6. 🗺️ PARTIE LIEU
    - `POST /api/createplace/`: Créer un nouveau lieu
    - `GET /api/<slug:slug_book>/getinfoplace/<slug:slug_place>/`: Récupérer les données d'un lieu, à partir de son slug et du slug du livre
    - `GET /api/<slug:slug>/getallplaces/`: Récupérer tous les lieux d'un livre, à partir de son slug
    - `PATCH /api/<slug:slug_book>/updateplace/<slug:slug_place>/`: Modifier les informations d'un lieu, à partir de son slug et du slug du livre
    - `DELETE /api/<slug:slug_book>/deleteplace/<slug:slug_place>/`: Supprimer un lieu, à partir de son slug et du slug du livre

7. 🐉 PARTIE CREATURE
    - `POST /api/createcreature/`: Créer une nouvelle créature
    - `GET /api/<slug:slug_book>/getinfocreature/<slug:slug_creature>/`: Récupérer les données d'une créature, à partir de son slug et du slug du livre
    - `GET /api/<slug:slug_book>/getallcreatures/`: Récupérer toutes les créatures d'un livre, à partir de son slug
    - `PATCH /api/<slug:slug_book>/updatecreature/<slug:slug_creature>/`: Modifier les informations d'une créature, à partir de son slug et du slug du livre
    - `DELETE /api/<slug:slug_book>/deletecreature/<slug:slug_creature>/`: Supprimer une créature, à partir de son slug et du slug du livre

8. ❤️ PARTIE FAVORI
    - `POST /api/newfavorite/`: Créer un nouveau favori
    - `GET /api/getallfavorite/<uuid:token>/`: Récupérer tous les favoris d'un utilisateur, à partir de son token
    - `DELETE /api/deletefavorite/<slug:slug_book>/`: Supprimer un favori, à partir du slug du livre mis en favori

9. ✏️ PARTIE AUTEUR SUIVI
    - `POST /api/newfollowedauthor/`: Créer un nouveau auteur suivi
    - `GET /api/getallfollowedauthors/<uuid:token>/`: Récupérer tous les suivis d'auteur d'un utilisateur, à partir de son token
    - `DELETE /api/deletefollowedauthor/<str:author_name>/`: Supprimer un auteur suivi, à partir de son nom d'auteur

## 🔒 Variables d'Environnement

| Variable | Description |
|----------|-------------|
| SECRET_KEY | Clé secrète Django |
| DEBUG | Mode débogage (True/False) |
| DB_NAME | Nom de la base de données PostgreSQL |
| DB_USER | Nom d'utilisateur de la base |
| DB_PASSWORD | Mot de passe de la base |
| DB_HOST | Hôte de la base |
| DB_PORT | Port de la base |
| CLOUDINARY_* | Identifiants Cloudinary |

## 📁 Structure du Projet

```
scriptum/
├── api/              # Application API principale
├── scriptum/         # Paramètres du projet
├── manage.py         # Script de gestion Django
├── requirements.txt  # Dépendances du projet
└── README.md        # Ce fichier
```
