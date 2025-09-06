from django.urls import path
from . import views

app_name = 'boutique'

urlpatterns = [
    # Page d'accueil temporaire
    path('', views.accueil, name='accueil'),
    path('produits/', views.liste_produits, name='liste_produits'),
    path('produit/<int:pk>/', views.detail_produit, name='detail_produit'),
    path('recherche/', views.recherche, name='recherche'),
    path('recherche-avancee/', views.recherche_avancee, name='recherche_avancee'),
    path('api/categories/', views.get_categories_tree, name='categories_tree'),
    path('api/categories-dropdown/', views.categories_dropdown, name='categories_dropdown'),
    path('panier/ajouter/<int:produit_id>/', views.ajouter_au_panier, name='ajouter_panier'),
    path('panier/', views.voir_panier, name='voir_panier'),
    path('panier/modifier/<int:produit_id>/', views.modifier_quantite_panier, name='modifier_panier'),
    path('panier/supprimer/<int:produit_id>/', views.supprimer_du_panier, name='supprimer_panier'),
    path('panier/count/', views.count_panier, name='count_panier'),
    path('panier/vider/', views.vider_panier, name='vider_panier'),
    path('produit/<int:pk>/', views.detail_produit, name='detail_produit'),


]