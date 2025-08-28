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
]