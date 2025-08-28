from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Produit, Categorie, Marque
from django.http import JsonResponse
from django.template.loader import render_to_string


def accueil(request):
    """Page d'accueil avec produits vedettes"""
    produits_vedettes = Produit.objects.filter(featured=True, active=True)[:8]
    produits_nouveaux = Produit.objects.filter(nouveau=True, active=True)[:8]
    categories = Categorie.objects.filter(active=True, parent__isnull=True)[:6]
    
    context = {
        'produits_vedettes': produits_vedettes,
        'produits_nouveaux': produits_nouveaux,
        'categories': categories,
    }
    return render(request, 'boutique/accueil.html', context)

def liste_produits(request):
    """Liste des produits avec filtres"""
    produits = Produit.objects.filter(active=True)
    
    # Filtres
    categorie_id = request.GET.get('categorie')
    marque_id = request.GET.get('marque')
    prix_min = request.GET.get('prix_min')
    prix_max = request.GET.get('prix_max')
    recherche = request.GET.get('q')
    
    if categorie_id:
        produits = produits.filter(categorie_id=categorie_id)
    if marque_id:
        produits = produits.filter(marque_id=marque_id)
    if prix_min:
        produits = produits.filter(prix__gte=prix_min)
    if prix_max:
        produits = produits.filter(prix__lte=prix_max)
    if recherche:
        produits = produits.filter(
            Q(nom__icontains=recherche) | 
            Q(description__icontains=recherche)
        )
    
    # Pagination
    paginator = Paginator(produits, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': Categorie.objects.filter(active=True, parent__isnull=True),
        'marques': Marque.objects.filter(active=True),
        'filtres_actifs': {
            'categorie': categorie_id,
            'marque': marque_id,
            'prix_min': prix_min,
            'prix_max': prix_max,
            'recherche': recherche,
        }
    }
    return render(request, 'boutique/liste_produits.html', context)

def detail_produit(request, pk):
    """Détail d'un produit"""
    produit = get_object_or_404(Produit, pk=pk, active=True)
    images = produit.images.all()
    produits_similaires = Produit.objects.filter(
        categorie=produit.categorie, 
        active=True
    ).exclude(pk=pk)[:4]
    
    # Avis clients
    avis = produit.avis.filter(approuve=True).order_by('-date_creation')[:5]
    
    context = {
        'produit': produit,
        'images': images,
        'produits_similaires': produits_similaires,
        'avis': avis,
    }
    return render(request, 'boutique/detail_produit.html', context)

def recherche(request):
    """Page de recherche"""
    query = request.GET.get('q')
    results = []
    
    if query:
        results = Produit.objects.filter(
            Q(nom__icontains=query) | 
            Q(description__icontains=query) |
            Q(reference__icontains=query),
            active=True
        )
    
    paginator = Paginator(results, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'query': query,
        'page_obj': page_obj,
        'total_results': results.count() if query else 0,
    }
    return render(request, 'boutique/recherche.html', context)




def get_categories_tree(request):
    """API pour récupérer l'arbre des catégories"""
    categories_principales = Categorie.objects.filter(
        active=True, 
        parent__isnull=True
    ).prefetch_related(
        'sous_categories__sous_categories'
    ).order_by('ordre', 'nom')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Retour JSON pour AJAX
        def build_tree(categories):
            tree = []
            for cat in categories:
                item = {
                    'id': cat.id,
                    'nom': cat.nom,
                    'slug': cat.slug,
                    'icone': cat.icone,
                    'url': f"/produits/?categorie={cat.id}",
                    'children': build_tree(cat.sous_categories.filter(active=True))
                }
                tree.append(item)
            return tree
        
        return JsonResponse({
            'categories': build_tree(categories_principales)
        })
    
    # Retour HTML classique
    html = render_to_string('boutique/includes/categories_dropdown.html', {
        'categories': categories_principales
    })
    return JsonResponse({'html': html})

def recherche_avancee(request):
    """Page de recherche avancée"""
    categories = Categorie.objects.filter(active=True, parent__isnull=True)
    marques = Marque.objects.filter(active=True)
    
    # Récupération des filtres
    query = request.GET.get('q', '')
    categorie_id = request.GET.get('categorie')
    sous_categorie_id = request.GET.get('sous_categorie')
    marque_id = request.GET.get('marque')
    prix_min = request.GET.get('prix_min')
    prix_max = request.GET.get('prix_max')
    en_stock = request.GET.get('en_stock')
    promotion = request.GET.get('promotion')
    
    # Construction de la requête
    produits = Produit.objects.filter(active=True)
    
    if query:
        produits = produits.filter(
            Q(nom__icontains=query) | 
            Q(description__icontains=query) |
            Q(reference__icontains=query)
        )
    
    if categorie_id:
        # Inclure les sous-catégories
        categorie = get_object_or_404(Categorie, id=categorie_id)
        categories_ids = [categorie.id]
        categories_ids.extend([cat.id for cat in categorie.get_all_children])
        produits = produits.filter(categorie_id__in=categories_ids)
    
    if sous_categorie_id:
        produits = produits.filter(categorie_id=sous_categorie_id)
    
    if marque_id:
        produits = produits.filter(marque_id=marque_id)
    
    if prix_min:
        produits = produits.filter(prix__gte=prix_min)
    
    if prix_max:
        produits = produits.filter(prix__lte=prix_max)
    
    if en_stock:
        produits = produits.filter(stock__gt=0)
    
    if promotion:
        produits = produits.filter(prix_promo__isnull=False)
    
    # Pagination
    paginator = Paginator(produits, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'marques': marques,
        'filtres_actifs': {
            'query': query,
            'categorie': categorie_id,
            'sous_categorie': sous_categorie_id,
            'marque': marque_id,
            'prix_min': prix_min,
            'prix_max': prix_max,
            'en_stock': en_stock,
            'promotion': promotion,
        },
        'total_results': produits.count(),
    }
    
    return render(request, 'boutique/recherche_avancee.html', context)