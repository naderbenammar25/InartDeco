1. Cloner le repository
```bash
git clone https://github.com/votre-username/inartdeco.git
cd inartdeco
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

4. Configurer la base de données
```bash
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