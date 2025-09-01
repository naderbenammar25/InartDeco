# Dans boutique/management/commands/create_produits.py
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from boutique.models import Produit, Categorie, Marque
from django.db import models
import requests
from io import BytesIO
from PIL import Image
import random

class Command(BaseCommand):
    help = 'Crée un jeu de données de 10 produits avec images'
    
    def handle(self, *args, **options):
        """Créer 10 produits avec images"""
        
        # Vérifier que les catégories existent
        if not Categorie.objects.exists():
            self.stdout.write(self.style.ERROR('Aucune catégorie trouvée. Exécutez d\'abord: python manage.py create_categories'))
            return
            
        # Créer quelques marques si elles n'existent pas
        marques_data = [
            {'nom': 'KitchenAid', 'description': 'Électroménager haut de gamme américain'},
            {'nom': 'Ikea', 'description': 'Mobilier et décoration design suédois'},
            {'nom': 'Pyrex', 'description': 'Ustensiles de cuisine en verre depuis 1915'},
            {'nom': 'Le Creuset', 'description': 'Batterie de cuisine premium française'},
            {'nom': 'Maisons du Monde', 'description': 'Décoration et mobilier tendance'},
        ]
        
        marques = {}
        for marque_data in marques_data:
            marque, created = Marque.objects.get_or_create(
                nom=marque_data['nom'],
                defaults={'description': marque_data['description']}
            )
            marques[marque.nom] = marque
            if created:
                self.stdout.write(f"✅ Marque créée: {marque.nom}")
        
        # Récupérer les catégories - prendre les sous-catégories en priorité
        categories = list(Categorie.objects.filter(parent__isnull=False))
        if not categories:
            categories = list(Categorie.objects.all())
            
        # Données des produits avec URLs d'images
        produits_data = [
            {
                'nom': 'Robot pâtissier KitchenAid Artisan',
                'description': 'Robot pâtissier professionnel avec bol en inox de 4,8L. Idéal pour pétrir, fouetter et mélanger. Livré avec 3 accessoires: fouet, crochet pétrisseur et batteur plat.',
                'prix': 449.99,
                'prix_promo': 399.99,
                'stock': 15,
                'seuil_stock': 3,
                'reference': 'KA-ART-001',
                'sku': 'KITCHENAID-5KSM175PS',
                'marque': 'KitchenAid',
                'poids': 11.5,
                'dimensions': '37 x 24 x 36 cm',
                'couleur': 'Rouge Empire',
                'materiau': 'Métal moulé sous pression',
                'etat': 'neuf',
                'featured': True,
                'nouveau': True,
                'meta_title': 'Robot KitchenAid Artisan - Pâtisserie Professionnelle',
                'meta_description': 'Robot pâtissier KitchenAid Artisan 4,8L avec accessoires.',
                'image_url': 'https://unsplash.com/fr/photos/un-mixeur-avec-des-oeufs-et-dautres-ingredients-sur-une-table-IBsRf_p0tHI'  # Robot cuisine moderne
            },
            {
                'nom': 'Set de casseroles Le Creuset signature',
                'description': 'Set de 3 casseroles en fonte émaillée (16cm, 18cm, 20cm). Excellente rétention de chaleur, compatible tous feux y compris induction.',
                'prix': 299.99,
                'stock': 8,
                'seuil_stock': 2,
                'reference': 'LC-SET-001',
                'sku': 'LECREUSET-CASSET3',
                'marque': 'Le Creuset',
                'poids': 4.2,
                'dimensions': '20 x 20 x 12 cm',
                'couleur': 'Cerise',
                'materiau': 'Fonte émaillée',
                'etat': 'neuf',
                'featured': True,
                'nouveau': False,
                'meta_title': 'Set Casseroles Le Creuset - Fonte Émaillée',
                'meta_description': 'Set 3 casseroles Le Creuset en fonte émaillée.',
                'image_url': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&h=400&fit=crop&crop=center'
            },
            {
                'nom': 'Plat à gratin Pyrex rectangulaire 35cm',
                'description': 'Plat à gratin en verre borosilicate, résistant aux chocs thermiques de -40°C à +300°C.',
                'prix': 24.99,
                'stock': 25,
                'seuil_stock': 5,
                'reference': 'PY-GRAT-001',
                'sku': 'PYREX-GRAT35',
                'marque': 'Pyrex',
                'poids': 1.8,
                'dimensions': '35 x 23 x 6 cm',
                'couleur': 'Transparent',
                'materiau': 'Verre borosilicate',
                'etat': 'neuf',
                'featured': False,
                'nouveau': False,
                'meta_title': 'Plat Gratin Pyrex 35cm - Verre Borosilicate',
                'meta_description': 'Plat à gratin Pyrex 35cm en verre résistant.',
                'image_url': 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&h=400&fit=crop&crop=center'
            },
            {
                'nom': 'Canapé 3 places scandinave Björk',
                'description': 'Canapé confortable au design scandinave, revêtement en tissu gris chiné haute qualité. Structure en bois massif de hêtre.',
                'prix': 599.99,
                'prix_promo': 499.99,
                'stock': 5,
                'seuil_stock': 1,
                'reference': 'MDM-CAN-001',
                'sku': 'BJORK-3P-GREY',
                'marque': 'Maisons du Monde',
                'poids': 45.0,
                'dimensions': '190 x 85 x 78 cm',
                'couleur': 'Gris chiné',
                'materiau': 'Tissu polyester, structure hêtre',
                'etat': 'neuf',
                'featured': True,
                'nouveau': False,
                'meta_title': 'Canapé Scandinave 3 Places Björk',
                'meta_description': 'Canapé 3 places scandinave en tissu gris.',
                'image_url': 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400&h=400&fit=crop&crop=center'
            },
            {
                'nom': 'Table basse en chêne massif Woodland',
                'description': 'Table basse rectangulaire en chêne massif avec finition huile naturelle. Design intemporel et fabrication artisanale française.',
                'prix': 349.99,
                'stock': 12,
                'seuil_stock': 3,
                'reference': 'MDM-TAB-001',
                'sku': 'WOODLAND-TB120',
                'marque': 'Maisons du Monde',
                'poids': 28.5,
                'dimensions': '120 x 60 x 45 cm',
                'couleur': 'Chêne naturel',
                'materiau': 'Chêne massif, métal',
                'etat': 'neuf',
                'featured': False,
                'nouveau': True,
                'meta_title': 'Table Basse Chêne Massif Woodland',
                'meta_description': 'Table basse en chêne massif 120cm.',
                'image_url': 'https://images.unsplash.com/photo-1449247709967-d4461a6a6103?w=400&h=400&fit=crop&crop=center'
            },
            {
                'nom': 'Bibliothèque modulaire HEMNES blanc',
                'description': 'Bibliothèque 5 étagères en pin massif teinté blanc. Design épuré et moderne. Facile à monter.',
                'prix': 89.99,
                'stock': 20,
                'seuil_stock': 4,
                'reference': 'IK-BIB-001',
                'sku': 'HEMNES-LIB180',
                'marque': 'Ikea',
                'poids': 35.2,
                'dimensions': '90 x 37 x 180 cm',
                'couleur': 'Blanc',
                'materiau': 'Pin massif teinté',
                'etat': 'neuf',
                'featured': False,
                'nouveau': False,
                'meta_title': 'Bibliothèque HEMNES Blanc 180cm',
                'meta_description': 'Bibliothèque IKEA HEMNES 180cm en pin massif.',
                'image_url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=center'
            },
            {
                'nom': 'Mixer plongeant KitchenAid Cordless',
                'description': 'Mixer plongeant sans fil haute performance avec batterie lithium rechargeable. Vitesse variable et turbo.',
                'prix': 129.99,
                'stock': 18,
                'seuil_stock': 4,
                'reference': 'KA-MIX-001',
                'sku': 'KITCHENAID-KHBC212',
                'marque': 'KitchenAid',
                'poids': 0.9,
                'dimensions': '6 x 6 x 38 cm',
                'couleur': 'Noir onyx',
                'materiau': 'Plastique ABS, acier inoxydable',
                'etat': 'neuf',
                'featured': False,
                'nouveau': True,
                'meta_title': 'Mixer Plongeant KitchenAid Sans Fil',
                'meta_description': 'Mixer plongeant KitchenAid sans fil rechargeable.',
                'image_url': 'https://images.unsplash.com/photo-1585515656090-79dcac4e60b0?w=400&h=400&fit=crop&crop=center'
            },
            {
                'nom': 'Saladier en verre Pyrex XXL 4L',
                'description': 'Grand saladier en verre transparent de 4L avec bec verseur. Idéal pour préparer et servir de grandes quantités.',
                'prix': 19.99,
                'stock': 30,
                'seuil_stock': 8,
                'reference': 'PY-SAL-001',
                'sku': 'PYREX-SAL4L',
                'marque': 'Pyrex',
                'poids': 1.2,
                'dimensions': '28 x 28 x 15 cm',
                'couleur': 'Transparent',
                'materiau': 'Verre borosilicate',
                'etat': 'neuf',
                'featured': False,
                'nouveau': False,
                'meta_title': 'Saladier Pyrex 4L - Verre Transparent XXL',
                'meta_description': 'Grand saladier Pyrex 4L en verre transparent.',
                'image_url': 'https://images.unsplash.com/photo-1559181567-c3190ca9959b?w=400&h=400&fit=crop&crop=center'
            },
            {
                'nom': 'Luminaire suspension Bambou Design',
                'description': 'Suspension en métal noir mat avec abat-jour en bambou naturel tressé. Style bohème chic, parfait au-dessus d\'une table à manger.',
                'prix': 159.99,
                'prix_promo': 129.99,
                'stock': 7,
                'seuil_stock': 2,
                'reference': 'MDM-LUM-001',
                'sku': 'BAMBOO-SUSP150',
                'marque': 'Maisons du Monde',
                'poids': 2.8,
                'dimensions': 'Ø 45 x H 35 cm',
                'couleur': 'Bambou naturel/noir',
                'materiau': 'Bambou tressé, métal',
                'etat': 'neuf',
                'featured': True,
                'nouveau': False,
                'meta_title': 'Suspension Bambou Design - Luminaire Bohème',
                'meta_description': 'Suspension design en bambou naturel et métal noir.',
                'image_url': 'https://images.unsplash.com/photo-1524484485831-a92ffc0de03f?w=400&h=400&fit=crop&crop=center'
            },
            {
                'nom': 'Coussin décoratif velours côtelé 45x45',
                'description': 'Coussin décoratif en velours côtelé couleur terracotta. Dimensions 45x45cm. Housse amovible lavable en machine à 30°C.',
                'prix': 29.99,
                'stock': 40,
                'seuil_stock': 10,
                'reference': 'MDM-COU-001',
                'sku': 'VELOURS-45-TERRA',
                'marque': 'Maisons du Monde',
                'poids': 0.6,
                'dimensions': '45 x 45 x 12 cm',
                'couleur': 'Terracotta',
                'materiau': 'Velours côtelé polyester',
                'etat': 'neuf',
                'featured': False,
                'nouveau': True,
                'meta_title': 'Coussin Velours Côtelé 45x45 Terracotta',
                'meta_description': 'Coussin décoratif en velours côtelé terracotta.',
                'image_url': 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400&h=400&fit=crop&crop=center'
            },
        ]
        
        # Supprimer les produits existants
        count_before = Produit.objects.count()
        if count_before > 0:
            self.stdout.write(f"Suppression de {count_before} produits existants...")
            Produit.objects.all().delete()
        
        # Créer les produits
        for i, produit_data in enumerate(produits_data, 1):
            try:
                # Sélectionner une catégorie aléatoire
                categorie = random.choice(categories)
                marque = marques[produit_data['marque']]
                
                # Créer le produit
                produit = Produit.objects.create(
                    nom=produit_data['nom'],
                    description=produit_data['description'],
                    prix=produit_data['prix'],
                    prix_promo=produit_data.get('prix_promo'),
                    stock=produit_data['stock'],
                    seuil_stock=produit_data.get('seuil_stock', 5),
                    reference=produit_data['reference'],
                    sku=produit_data.get('sku'),
                    categorie=categorie,
                    marque=marque,
                    poids=produit_data.get('poids'),
                    dimensions=produit_data.get('dimensions'),
                    couleur=produit_data.get('couleur'),
                    materiau=produit_data.get('materiau'),
                    etat=produit_data.get('etat', 'neuf'),
                    featured=produit_data.get('featured', False),
                    nouveau=produit_data.get('nouveau', False),
                    meta_title=produit_data.get('meta_title'),
                    meta_description=produit_data.get('meta_description'),
                )
                
                # Télécharger et attacher l'image
                try:
                    self.stdout.write(f"📥 Téléchargement de l'image pour {produit.nom}...")
                    
                    response = requests.get(produit_data['image_url'], timeout=15)
                    if response.status_code == 200:
                        # Créer un nom de fichier
                        filename = f"produit_{produit.id}_{produit.reference}.jpg"
                        
                        # Redimensionner l'image
                        image = Image.open(BytesIO(response.content))
                        image = image.convert('RGB')
                        image.thumbnail((600, 600), Image.LANCZOS)
                        
                        # Sauvegarder l'image redimensionnée
                        output = BytesIO()
                        image.save(output, format='JPEG', quality=85)
                        output.seek(0)
                        
                        # Attacher à l'objet produit
                        produit.image_principale.save(
                            filename,
                            ContentFile(output.getvalue()),
                            save=True
                        )
                        
                        image_status = "🖼️ Avec image"
                    else:
                        image_status = "⚠️ Sans image (erreur téléchargement)"
                        
                except Exception as e:
                    image_status = f"⚠️ Sans image ({str(e)[:30]}...)"
                
                # Affichage avec informations sur le statut
                status_info = []
                if produit.featured:
                    status_info.append("⭐ Vedette")
                if produit.nouveau:
                    status_info.append("🆕 Nouveau")
                if produit.en_promotion:
                    status_info.append(f"💰 Promo -{produit.prix - produit.prix_promo}€")
                
                status_str = f" ({', '.join(status_info)})" if status_info else ""
                
                self.stdout.write(
                    f"✅ Produit {i}/10 créé: {produit.nom}{status_str}\n"
                    f"   📂 Catégorie: {categorie.nom} | 🏷️ {produit.reference} | "
                    f"💶 {produit.prix}€ | 📦 Stock: {produit.stock} | {image_status}"
                )
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Erreur création produit {i}: {str(e)}"))
        
        # Résumé détaillé
        total_produits = Produit.objects.count()
        produits_featured = Produit.objects.filter(featured=True).count()
        produits_nouveaux = Produit.objects.filter(nouveau=True).count()
        produits_promo = Produit.objects.filter(prix_promo__isnull=False).count()
        produits_avec_images = Produit.objects.exclude(image_principale='').count()
        
        if total_produits > 0:
            valeur_stock_total = sum(p.prix * p.stock for p in Produit.objects.all())
        else:
            valeur_stock_total = 0
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\n🎉 Création terminée avec succès !\n"
                f"📦 {total_produits} produits créés\n"
                f"⭐ {produits_featured} produits vedette (featured)\n"
                f"🆕 {produits_nouveaux} nouveaux produits\n"
                f"💰 {produits_promo} produits en promotion\n"
                f"🖼️ {produits_avec_images} produits avec images\n"
                f"💎 Valeur totale du stock: {valeur_stock_total:.2f}€\n"
                f"🏷️ Marques: {', '.join(marques.keys())}"
            )
        )