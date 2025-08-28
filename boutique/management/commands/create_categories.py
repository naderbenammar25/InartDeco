# Remplacer le contenu de boutique/management/commands/create_categories.py
from django.core.management.base import BaseCommand
from boutique.models import Categorie

class Command(BaseCommand):
    help = 'Crée la hiérarchie complète des catégories'
    
    def handle(self, *args, **options):
        """Créer toute la hiérarchie de catégories"""
        
        # Supprimer toutes les catégories existantes
        count_before = Categorie.objects.count()
        if count_before > 0:
            self.stdout.write(f"Suppression de {count_before} catégories existantes...")
            Categorie.objects.all().delete()
        
        # Catégories principales (niveau 1)
        categories_principales = [
            {'nom': 'Cuisine & Préparation', 'icone': 'fas fa-utensils', 'ordre': 1},
            {'nom': 'Art de la table', 'icone': 'fas fa-wine-glass', 'ordre': 2},
            {'nom': 'Rangement & Organisation (Cuisine)', 'icone': 'fas fa-box', 'ordre': 3},
            {'nom': 'Petit électroménager (Cuisine)', 'icone': 'fas fa-blender', 'ordre': 4},
            {'nom': 'Salle de bain', 'icone': 'fas fa-bath', 'ordre': 5},
            {'nom': 'Chambre & Literie', 'icone': 'fas fa-bed', 'ordre': 6},
            {'nom': 'Salon & Séjour', 'icone': 'fas fa-couch', 'ordre': 7},
            {'nom': 'Décoration & Ambiance', 'icone': 'fas fa-palette', 'ordre': 8},
            {'nom': 'Linge de maison', 'icone': 'fas fa-tshirt', 'ordre': 9},
            {'nom': 'Rangement & Organisation (Maison)', 'icone': 'fas fa-archive', 'ordre': 10},
            {'nom': 'Buanderie & Entretien', 'icone': 'fas fa-broom', 'ordre': 11},
            {'nom': 'Extérieur, Jardin & Balcon', 'icone': 'fas fa-seedling', 'ordre': 12},
            {'nom': 'Plage', 'icone': 'fas fa-umbrella-beach', 'ordre': 13},
            {'nom': 'Enfants & Bébé (Maison)', 'icone': 'fas fa-baby', 'ordre': 14},
            {'nom': 'Animaux domestiques (Maison)', 'icone': 'fas fa-paw', 'ordre': 15},
            {'nom': 'Quincaillerie légère & Électricité', 'icone': 'fas fa-tools', 'ordre': 16},
        ]
        
        # Créer les catégories principales
        cats_principales = {}
        for cat_data in categories_principales:
            cat = Categorie.objects.create(**cat_data)
            cats_principales[cat.nom] = cat
            self.stdout.write(f"✅ Créé: {cat.nom}")
        
        # Sous-catégories niveau 2 avec noms uniques
        sous_categories = {
            'Cuisine & Préparation': [
                'Batterie de cuisine',
                'Cuisson au four (Bakeware)',
                'Ustensiles & Outils',
                'Couteaux & Aiguisage',
                'Préparation & Mesure',
                'Protection & Maniement',
            ],
            'Art de la table': [
                'Vaisselle',
                'Verres & Carafes',
                'Couverts',
                'Service & Buffet',
                'Nappage & Linge de table',
            ],
            'Rangement & Organisation (Cuisine)': [
                'Conservation alimentaire',
                'Organisation placards/tiroirs',
                'Évier & Vaisselle',
                'Films & papiers',
            ],
            'Petit électroménager (Cuisine)': [
                'Petit-déjeuner',
                'Préparation culinaire',
                'Cuisson & Snack',
                'Boissons & Froid',
            ],
            'Salle de bain': [
                'Accessoires salle de bain',  # Renommé pour éviter le doublon
                'Textiles & Confort',
                'Rangement salle de bain',    # Renommé pour éviter le doublon
                'WC & Entretien',
            ],
            'Chambre & Literie': [
                'Literie',
                'Protection literie',
                'Meubles de chambre',
                'Décoration chambre',
            ],
            'Salon & Séjour': [
                'Meubles salon',              # Renommé pour éviter le doublon
                'Textiles déco',
                'Tapis salon',                # Renommé pour éviter le doublon
                'Multimédia & accessoires',
            ],
            'Décoration & Ambiance': [
                'Décoration murale',
                'Éclairage intérieur',
                'Vases & Plantes',
                'Senteurs & Bien-être',
            ],
            'Linge de maison': [
                'Linge de lit',
                'Linge de bain',
                'Linge de table',
                'Rideaux & Housses',
            ],
            'Rangement & Organisation (Maison)': [
                'Dressing & placards',
                'Boîtes & paniers',
                'Chaussures & Accessoires',
                'Entrée & Bureau',
            ],
            'Buanderie & Entretien': [
                'Lessive & Soin du linge',
                'Repassage',
                'Nettoyage maison',
            ],
            'Extérieur, Jardin & Balcon': [
                'Mobilier d\'extérieur',
                'Confort & Protection extérieur',  # Renommé
                'Barbecue & Pique-nique',
                'Éclairage & Plantes extérieur',   # Renommé
            ],
            'Plage': [
                'Accessoires plage',              # Renommé pour éviter le doublon
                'Mobilier & Confort plage',       # Renommé
                'Jeux & Loisirs',
                'Froid & Hydratation',
            ],
            'Enfants & Bébé (Maison)': [
                'Repas enfant',
                'Chambre enfant',
                'Rangement enfant',
            ],
            'Animaux domestiques (Maison)': [
                'Repas & Eau animaux',            # Renommé
                'Confort & Couchage animaux',     # Renommé
                'Toilettage & Propreté',
            ],
            'Quincaillerie légère & Électricité': [
                'Fixation & Protection',
                'Électricité pratique',
            ],
        }
        
        # Créer les sous-catégories niveau 2
        cats_niveau2 = {}
        for parent_nom, sous_cats in sous_categories.items():
            parent = cats_principales[parent_nom]
            for i, sous_cat_nom in enumerate(sous_cats):
                sous_cat = Categorie.objects.create(
                    nom=sous_cat_nom,
                    parent=parent,
                    ordre=i + 1
                )
                cats_niveau2[sous_cat_nom] = sous_cat
                self.stdout.write(f"  ✅ Créé: {parent_nom} > {sous_cat_nom}")
        
        # Sous-catégories niveau 3 (quelques exemples)
        sous_sous_categories = {
            'Batterie de cuisine': [
                'Casseroles, poêles, faitouts',
                'Woks, tajines, couscoussiers',
                'Couvercles, dessous-de-plat',
            ],
            'Cuisson au four (Bakeware)': [
                'Moules (cake, tarte, muffins)',
                'Plats à four & cocottes',
                'Tapis/papiers de cuisson, grilles',
            ],
            'Ustensiles & Outils': [
                'Spatules, fouets, louches',
                'Éplucheurs, râpes, presse-purée',
                'Passoires, entonnoirs, écumoires',
            ],
            'Couteaux & Aiguisage': [
                'Couteaux chef, office, pain',
                'Blocs/porte-couteaux, aimants',
                'Fusils & aiguiseurs',
            ],
            'Préparation & Mesure': [
                'Bols/mélange, saladiers',
                'Verres doseurs, balances',
                'Minuteries, thermomètres',
            ],
            'Protection & Maniement': [
                'Maniques & gants',
                'Tabliers & torchons',
                'Dessous-plats & anti-chaleur',
            ],
            'Vaisselle': [
                'Assiettes (plates, creuses, dessert)',
                'Bols & saladiers vaisselle',
                'Plats de service & saucières',
            ],
            'Verres & Carafes': [
                'Verres à eau, à vin, à bière',
                'Flûtes & coupes',
                'Carafes & pichets',
            ],
            'Couverts': [
                'Ménagères complètes',
                'Couverts de service',
                'Couteaux à steak',
            ],
            'Service & Buffet': [
                'Plateaux, présentoirs, cloches',
                'Plateaux à fromage',
                'Salières/poivrières, huiliers/vinaigriers',
            ],
            'Nappage & Linge de table': [
                'Nappes & chemins de table',
                'Sets de table & dessous de verre',
                'Serviettes de table & ronds',
            ],
            'Conservation alimentaire': [
                'Boîtes hermétiques',
                'Bocaux & pots à épices',
                'Sacs réutilisables & sous-vide',
            ],
            'Organisation placards/tiroirs': [
                'Range-épices, séparateurs',
                'Plateaux tournants (lazy Susan)',
                'Range-couverts & porte-couvercles',
            ],
            'Évier & Vaisselle': [
                'Égouttoirs & tapis d\'égouttage',
                'Porte-éponge & brosses',
                'Distributeurs de liquide vaisselle',
            ],
            'Films & papiers': [
                'Film alimentaire, alu',
                'Papier cuisson, papillotes',
                'Rouleaux & dévidoirs',
            ],
            'Petit-déjeuner': [
                'Bouilloires, théières électriques',
                'Cafetières (filtre, italienne), moulins',
                'Grille-pain',
            ],
            'Préparation culinaire': [
                'Mixeurs plongeants & blenders',
                'Robots, hachoirs, batteurs',
                'Râpes/spiralizers électriques',
            ],
            'Cuisson & Snack': [
                'Friteuses, air-fryers',
                'Mini-fours & grills',
                'Crêpières, gaufriers',
            ],
            'Boissons & Froid': [
                'Presse-agrumes, extracteurs',
                'Sodas/infuseurs',
                'Machines à glaçons',
            ],
            'Accessoires salle de bain': [
                'Porte-savon, distributeurs, gobelets',
                'Porte-brosses, boîtes coton, vanity',
                'Poubelles de salle de bain',
            ],
            'Textiles & Confort': [
                'Serviettes & draps de bain',
                'Peignoirs, gants, tapis antidérapants',
                'Rideaux de douche & barres',
            ],
            'Rangement salle de bain': [
                'Étagères & colonnes',
                'Porte-serviettes & patères',
                'Paniers à linge & organisateurs',
            ],
            'WC & Entretien': [
                'Brosses & porte-brosses',
                'Abattants & caches-rouleaux',
                'Diffuseurs d\'odeur',
            ],
            'Literie': [
                'Draps, housses, taies',
                'Couettes & couvertures',
                'Oreillers & traversins',
            ],
            'Protection literie': [
                'Protège-matelas & alèses',
                'Protège-oreillers',
                'Housses anti-acariens',
            ],
            'Meubles de chambre': [
                'Lits & têtes de lit',
                'Tables de chevet, commodes',
                'Armoires & penderies',
            ],
            'Décoration chambre': [
                'Lampes de chevet',
                'Miroirs & cadres chambre',
                'Tapis de chambre',
            ],
        }
        
        # Créer les sous-sous-catégories niveau 3
        for parent_nom, sous_sous_cats in sous_sous_categories.items():
            if parent_nom in cats_niveau2:
                parent = cats_niveau2[parent_nom]
                for i, sous_sous_cat_nom in enumerate(sous_sous_cats):
                    try:
                        Categorie.objects.create(
                            nom=sous_sous_cat_nom,
                            parent=parent,
                            ordre=i + 1
                        )
                        self.stdout.write(f"    ✅ Créé: {parent.parent.nom} > {parent_nom} > {sous_sous_cat_nom}")
                    except Exception as e:
                        self.stdout.write(f"    ❌ Erreur: {sous_sous_cat_nom} - {str(e)}")
        
        total = Categorie.objects.count()
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 {total} catégories créées avec succès!')
        )