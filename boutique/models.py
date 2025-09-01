from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import os

# Dans boutique/models.py, ajouter les nouveaux champs
class Categorie(models.Model):
    """Modèle pour les catégories de produits"""
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='sous_categories')
    
    # Nouveaux champs
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icone = models.CharField(max_length=50, blank=True, help_text="Classe CSS Font Awesome")
    ordre = models.PositiveIntegerField(default=0, help_text="Ordre d'affichage")
    
    active = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['ordre', 'nom']
    
    def __str__(self):
        return self.nom
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

class Marque(models.Model):
    """Modèle pour les marques de produits"""
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='marques/', blank=True, null=True)
    site_web = models.URLField(blank=True)
    active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Marque"
        verbose_name_plural = "Marques"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom


class Fournisseur(models.Model):
    """Modèle pour les fournisseurs"""
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.TextField(blank=True)
    site_web = models.URLField(blank=True)
    contact_principal = models.CharField(max_length=100, blank=True)
    conditions_paiement = models.CharField(max_length=200, blank=True)
    delai_livraison = models.PositiveIntegerField(blank=True, null=True, help_text="Délai de livraison en jours")
    active = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom


class Produit(models.Model):
    """Modèle principal pour les produits"""
    ETAT_CHOICES = [
        ('neuf', 'Neuf'),
        ('occasion', 'Occasion'),
        ('reconditionne', 'Reconditionné'),
    ]
    
    nom = models.CharField(max_length=200)
    description = models.TextField()
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    prix_promo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    seuil_stock = models.PositiveIntegerField(default=5)
    
    # Relations
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='produits')
    marque = models.ForeignKey(Marque, on_delete=models.SET_NULL, null=True, blank=True)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.SET_NULL, null=True, blank=True, related_name='produits')
    
    # Caractéristiques du produit
    reference = models.CharField(max_length=50, unique=True, blank=True, null=True, help_text="Référence unique du produit")  # Optionnel au début
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True)  # Référence interne (optionnel)
    code_barre = models.CharField(max_length=50, blank=True)
    poids = models.DecimalField(max_digits=8, decimal_places=2, help_text="Poids en kg", blank=True, null=True)
    dimensions = models.CharField(max_length=100, blank=True, help_text="L x l x h en cm")
    couleur = models.CharField(max_length=50, blank=True)
    materiau = models.CharField(max_length=100, blank=True)
    etat = models.CharField(max_length=20, choices=ETAT_CHOICES, default='neuf')
    
    # Images
    image_principale = models.ImageField(upload_to='produits/')
    
    # Statuts
    active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False, verbose_name="Produit vedette")
    nouveau = models.BooleanField(default=False)
    
    # Dates
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    # SEO
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    
    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['-date_creation']
    
    def __str__(self):
        return self.nom
    
    def get_absolute_url(self):
        return reverse('produit_detail', kwargs={'pk': self.pk})
    
    @property
    def prix_final(self):
        """Retourne le prix promotionnel s'il existe, sinon le prix normal"""
        return self.prix_promo if self.prix_promo else self.prix
    
    @property
    def en_promotion(self):
        """Vérifie si le produit est en promotion"""
        return self.prix_promo is not None and self.prix_promo < self.prix
    
    @property
    def stock_faible(self):
        """Vérifie si le stock est faible"""
        return self.stock <= self.seuil_stock
    
    @property
    def disponible(self):
        """Vérifie si le produit est disponible"""
        return self.stock > 0 and self.active
    
    @property
    def chemin_categorie(self):
        """Retourne le chemin complet de la catégorie du produit"""
        return self.categorie.chemin_complet
    
    @property
    def economie(self):
        """Calcule l'économie réalisée avec la promotion"""
        if self.prix_promo and self.prix_promo < self.prix:
            return float(self.prix) - float(self.prix_promo)
        return 0
    
    @property
    def pourcentage_reduction(self):
        """Calcule le pourcentage de réduction"""
        if self.prix_promo and self.prix_promo < self.prix:
            return round(((float(self.prix) - float(self.prix_promo)) / float(self.prix)) * 100)
        return 0


class ImageProduit(models.Model):
    """Modèle pour les images supplémentaires des produits"""
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='produits/gallery/')
    alt_text = models.CharField(max_length=100, blank=True)
    ordre = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = "Image de produit"
        verbose_name_plural = "Images de produits"
        ordering = ['ordre']
    
    def __str__(self):
        return f"Image de {self.produit.nom}"


class ProfilClient(models.Model):
    """Extension du modèle User pour les clients"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telephone = models.CharField(max_length=20, blank=True)
    date_naissance = models.DateField(blank=True, null=True)
    newsletter = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Profil client"
        verbose_name_plural = "Profils clients"
    
    def __str__(self):
        return f"Profil de {self.user.username}"


class Adresse(models.Model):
    """Modèle pour les adresses des clients"""
    TYPE_CHOICES = [
        ('facturation', 'Facturation'),
        ('livraison', 'Livraison'),
    ]
    
    client = models.ForeignKey(ProfilClient, on_delete=models.CASCADE, related_name='adresses')
    type_adresse = models.CharField(max_length=20, choices=TYPE_CHOICES)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    entreprise = models.CharField(max_length=100, blank=True)
    adresse1 = models.CharField(max_length=200)
    adresse2 = models.CharField(max_length=200, blank=True)
    ville = models.CharField(max_length=100)
    code_postal = models.CharField(max_length=10)
    pays = models.CharField(max_length=100, default='France')
    telephone = models.CharField(max_length=20, blank=True)
    par_defaut = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Adresse"
        verbose_name_plural = "Adresses"
    
    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.ville}"


class Commande(models.Model):
    """Modèle pour les commandes"""
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirmee', 'Confirmée'),
        ('preparee', 'Préparée'),
        ('expediee', 'Expédiée'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
        ('retournee', 'Retournée'),
    ]
    
    STATUT_PAIEMENT_CHOICES = [
        ('en_attente', 'En attente'),
        ('paye', 'Payé'),
        ('echec', 'Échec'),
        ('rembourse', 'Remboursé'),
    ]
    
    # Identification
    numero_commande = models.CharField(max_length=20, unique=True)
    client = models.ForeignKey(ProfilClient, on_delete=models.CASCADE, related_name='commandes')
    
    # Statuts
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    statut_paiement = models.CharField(max_length=20, choices=STATUT_PAIEMENT_CHOICES, default='en_attente')
    
    # Montants
    sous_total = models.DecimalField(max_digits=10, decimal_places=2)
    frais_livraison = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Adresses
    adresse_facturation = models.ForeignKey(Adresse, on_delete=models.PROTECT, related_name='commandes_facturation')
    adresse_livraison = models.ForeignKey(Adresse, on_delete=models.PROTECT, related_name='commandes_livraison')
    
    # Dates
    date_commande = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    date_livraison_prevue = models.DateTimeField(blank=True, null=True)
    date_livraison = models.DateTimeField(blank=True, null=True)
    
    # Notes
    notes_client = models.TextField(blank=True)
    notes_admin = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-date_commande']
    
    def __str__(self):
        return f"Commande {self.numero_commande}"
    
    def save(self, *args, **kwargs):
        if not self.numero_commande:
            # Génération automatique du numéro de commande
            import datetime
            now = datetime.datetime.now()
            self.numero_commande = f"CMD{now.strftime('%Y%m%d')}{self.pk or ''}"
        super().save(*args, **kwargs)


class LigneCommande(models.Model):
    """Modèle pour les lignes de commande"""
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = "Ligne de commande"
        verbose_name_plural = "Lignes de commande"
    
    def __str__(self):
        return f"{self.quantite} x {self.produit.nom}"
    
    @property
    def sous_total(self):
        return self.quantite * self.prix_unitaire


class Panier(models.Model):
    """Modèle pour le panier temporaire"""
    client = models.ForeignKey(ProfilClient, on_delete=models.CASCADE, related_name='paniers')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)
    date_ajout = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Panier"
        verbose_name_plural = "Paniers"
        unique_together = ['client', 'produit']
    
    def __str__(self):
        return f"{self.client.user.username} - {self.produit.nom} (x{self.quantite})"
    
    @property
    def sous_total(self):
        return self.quantite * self.produit.prix_final


class ModeLivraison(models.Model):
    """Modèle pour les modes de livraison"""
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    delai_min = models.PositiveIntegerField(help_text="Délai minimum en jours")
    delai_max = models.PositiveIntegerField(help_text="Délai maximum en jours")
    active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Mode de livraison"
        verbose_name_plural = "Modes de livraison"
    
    def __str__(self):
        return self.nom


class CodePromo(models.Model):
    """Modèle pour les codes promotionnels"""
    TYPE_CHOICES = [
        ('pourcentage', 'Pourcentage'),
        ('montant', 'Montant fixe'),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200)
    type_reduction = models.CharField(max_length=20, choices=TYPE_CHOICES)
    valeur = models.DecimalField(max_digits=10, decimal_places=2)
    montant_minimum = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nombre_utilisations_max = models.PositiveIntegerField(blank=True, null=True)
    nombre_utilisations = models.PositiveIntegerField(default=0)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Code promo"
        verbose_name_plural = "Codes promo"
    
    def __str__(self):
        return self.code
    
    @property
    def est_valide(self):
        from django.utils import timezone
        now = timezone.now()
        return (
            self.active and
            self.date_debut <= now <= self.date_fin and
            (self.nombre_utilisations_max is None or self.nombre_utilisations < self.nombre_utilisations_max)
        )


class Avis(models.Model):
    """Modèle pour les avis clients sur les produits"""
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='avis')
    client = models.ForeignKey(ProfilClient, on_delete=models.CASCADE)
    note = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    titre = models.CharField(max_length=200)
    commentaire = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    approuve = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Avis"
        verbose_name_plural = "Avis"
        unique_together = ['produit', 'client']
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Avis de {self.client.user.username} sur {self.produit.nom}"
