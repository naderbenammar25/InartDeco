from django.contrib import admin
from .models import (
    Categorie, Marque, Fournisseur, Produit, ImageProduit,
    ProfilClient, Commande, LigneCommande, CodePromo, Avis
)

# Configuration de l'admin principal
admin.site.site_header = "InArtDeco - Administration"
admin.site.site_title = "InArtDeco Admin"
admin.site.index_title = "Gestion du site e-commerce"

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'parent', 'get_niveau', 'active')
    list_filter = ('active', 'parent')
    search_fields = ('nom', 'description')
    list_editable = ('active',)
    
    def get_niveau(self, obj):
        return f"Niveau {obj.niveau}"
    get_niveau.short_description = "Niveau"

@admin.register(Marque)
class MarqueAdmin(admin.ModelAdmin):
    list_display = ('nom', 'active')
    search_fields = ('nom', 'description')
    list_filter = ('active',)

@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'email', 'telephone', 'active', 'delai_livraison')
    list_filter = ('active', 'delai_livraison')
    search_fields = ('nom', 'email', 'telephone')
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'description', 'active')
        }),
        ('Contact', {
            'fields': ('email', 'telephone', 'adresse', 'ville', 'code_postal', 'pays')
        }),
        ('Conditions commerciales', {
            'fields': ('conditions_paiement', 'delai_livraison')
        })
    )

class ImageProduitInline(admin.TabularInline):
    model = ImageProduit
    extra = 2
    fields = ('image', 'alt_text', 'ordre')

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'reference', 'prix', 'prix_promo', 'stock', 'categorie', 'marque', 'active', 'featured')
    list_filter = ('active', 'featured', 'nouveau', 'categorie', 'marque', 'etat')
    search_fields = ('nom', 'reference', 'description', 'sku')
    list_editable = ('prix', 'stock', 'active', 'featured')
    inlines = [ImageProduitInline]
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('nom', 'description', 'reference', 'sku', 'image_principale')
        }),
        ('Prix et stock', {
            'fields': ('prix', 'prix_promo', 'stock', 'seuil_stock'),
            'classes': ('wide',)
        }),
        ('Classification', {
            'fields': ('categorie', 'marque', 'fournisseur')
        }),
        ('Caractéristiques techniques', {
            'fields': ('couleur', 'materiau', 'dimensions', 'poids', 'code_barre', 'etat'),
            'classes': ('collapse',)
        }),
        ('Statuts et visibilité', {
            'fields': ('active', 'featured', 'nouveau')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.reference:
            # Générer automatiquement une référence si elle n'existe pas
            obj.reference = f"REF{obj.pk or ''}{obj.nom[:3].upper()}"
        super().save_model(request, obj, form, change)

@admin.register(ProfilClient)
class ProfilClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'telephone', 'date_naissance', 'newsletter')
    list_filter = ('newsletter', 'date_naissance')
    search_fields = ('user__username', 'user__email', 'telephone')

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('numero_commande', 'client', 'statut', 'total', 'date_commande')
    list_filter = ('statut', 'date_commande')
    search_fields = ('numero_commande', 'client__user__username', 'client__user__email')
    readonly_fields = ('numero_commande', 'total', 'date_commande')
    date_hierarchy = 'date_commande'

@admin.register(CodePromo)
class CodePromoAdmin(admin.ModelAdmin):
    list_display = ('code', 'type_reduction', 'valeur', 'date_debut', 'date_fin', 'active', 'est_valide')
    list_filter = ('type_reduction', 'active', 'date_debut', 'date_fin')
    search_fields = ('code', 'description')
    
    def est_valide(self, obj):
        return obj.est_valide
    est_valide.boolean = True
    est_valide.short_description = "Valide"

@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin):
    list_display = ('produit', 'client', 'note', 'titre', 'date_creation', 'approuve')
    list_filter = ('note', 'approuve', 'date_creation')
    search_fields = ('produit__nom', 'client__user__username', 'titre')
    list_editable = ('approuve',)
    readonly_fields = ('date_creation',)