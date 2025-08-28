# InArtDeco - Boutique en ligne d'équipements maison

Site e-commerce spécialisé dans la vente d'équipements pour la maison.

## 🚀 Installation

1. Cloner le repository
```bash
git clone https://github.com/naderbenammar25/InartDeco.git
cd InartDeco
```

2. Créer un environnement virtuel
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. Installer les dépendances
```bash
pip install -r requirements.txt
```

4. Configurer la base de données PostgreSQL
```bash
# Créer une base de données PostgreSQL nommée 'inartdeco'
python manage.py makemigrations
python manage.py migrate
```

5. Créer les catégories
```bash
python manage.py create_categories
```

6. Lancer le serveur
```bash
python manage.py runserver
```

## 🌐 Accès

Ouvrir http://127.0.0.1:8000/ dans votre navigateur

## 🛠️ Technologies

- Django 5.0
- PostgreSQL
- Bootstrap 5
- Font Awesome

## 📁 Structure du projet

```
inartdeco/
├── boutique/           # App principale
├── templates/          # Templates HTML
├── static/            # Fichiers statiques (CSS, JS, images)
├── media/             # Fichiers uploadés
└── requirements.txt   # Dépendances Python
```

## 🎯 Fonctionnalités

- ✅ Catalogue avec mega menu hiérarchique
- ✅ Slider automatique sur la page d'accueil
- ✅ Navbar blanche responsive
- ✅ Recherche avancée
- ✅ Système de catégories à 3 niveaux
- 🔄 Panier d'achat (en développement)
- 🔄 Système de commandes (en développement)
- 🔄 Authentification utilisateur (en développement)

## 👨‍💻 Développeur

Nader Ben Ammar - [@naderbenammar25](https://github.com/naderbenammar25)