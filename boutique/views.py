from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Produit, Categorie, Marque, ImageProduit


def accueil(request):
    # Récupérer les produits vedettes
    produits_vedettes = Produit.objects.filter(
        featured=True, 
        active=True
    ).select_related('categorie', 'marque')[:4]
    
    # Récupérer les nouveautés
    produits_nouveaux = Produit.objects.filter(
        nouveau=True, 
        active=True
    ).select_related('categorie', 'marque')[:4]
    
    # Récupérer les catégories principales avec le nombre de produits
    # CORRECTION : changer 'produit' par 'produits' (ligne 32 et 33)
    categories = Categorie.objects.filter(
        parent__isnull=True,  # Catégories principales seulement
        active=True
    ).annotate(
        produits_count=Count('produits', filter=Q(produits__active=True))
    ).order_by('nom')[:6]  # Limiter à 6 catégories pour l'affichage
    
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

# Dans boutique/views.py, ajoutez cette vue
from django.http import JsonResponse
from django.template.loader import render_to_string

def categories_dropdown(request):
    """Vue AJAX pour charger la liste simple des catégories"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Récupérer seulement les catégories principales (sans parent)
        categories_principales = Categorie.objects.filter(parent=None, active=True).order_by('ordre', 'nom')
        
        html = ""
        for categorie in categories_principales:
            html += f'<li><a class="dropdown-item" href="/produits/?categorie={categorie.id}">'
            html += f'<i class="{categorie.icone}"></i> {categorie.nom}</a></li>'
            
            # Ajouter les sous-catégories avec indentation
            sous_categories = categorie.sous_categories.filter(active=True).order_by('ordre', 'nom')
            for sous_cat in sous_categories:
                html += f'<li><a class="dropdown-item ps-4" href="/produits/?categorie={sous_cat.id}">'
                html += f'&nbsp;&nbsp;→ {sous_cat.nom}</a></li>'
        
        return JsonResponse({'html': html})
    
    return JsonResponse({'error': 'Requête invalide'}, status=400)

# ...existing code...

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json

def ajouter_au_panier(request, produit_id):
    """Ajouter un produit au panier (session)"""
    if request.method == 'POST':
        produit = get_object_or_404(Produit, id=produit_id)
        
        # Vérifier le stock et la disponibilité
        if not produit.disponible:
            return JsonResponse({
                'success': False,
                'message': 'Produit non disponible'
            })
        
        # Récupérer le panier de la session
        panier = request.session.get('panier', {})
        
        # Ajouter ou incrémenter la quantité
        if str(produit_id) in panier:
            # Vérifier si on peut ajouter encore (stock disponible)
            nouvelle_quantite = panier[str(produit_id)]['quantite'] + 1
            if nouvelle_quantite > produit.stock:
                return JsonResponse({
                    'success': False,
                    'message': f'Stock insuffisant. Seulement {produit.stock} disponible(s)'
                })
            panier[str(produit_id)]['quantite'] = nouvelle_quantite
        else:
            panier[str(produit_id)] = {
                'nom': produit.nom,
                'prix': float(produit.prix_final),
                'quantite': 1,
                'image': produit.image_principale.url if produit.image_principale else '',
                'reference': produit.reference or '',
                'max_stock': produit.stock
            }
        
        # Sauvegarder le panier en session
        request.session['panier'] = panier
        request.session.modified = True
        
        # Calculer le nombre total d'articles
        nb_articles = sum(item['quantite'] for item in panier.values())
        
        return JsonResponse({
            'success': True,
            'message': f'{produit.nom} ajouté au panier',
            'nb_articles': nb_articles
        })
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

def voir_panier(request):
    """Afficher le contenu du panier"""
    panier = request.session.get('panier', {})
    
    # Enrichir les données du panier avec les infos produits
    panier_detaille = []
    sous_total = 0
    
    for produit_id, item in panier.items():
        try:
            produit = Produit.objects.get(id=produit_id)
            item_total = item['prix'] * item['quantite']
            sous_total += item_total
            
            panier_detaille.append({
                'produit': produit,
                'quantite': item['quantite'],
                'prix_unitaire': item['prix'],
                'total': item_total,
                'image': item.get('image', ''),
            })
        except Produit.DoesNotExist:
            # Supprimer les produits qui n'existent plus
            del request.session['panier'][produit_id]
            request.session.modified = True
    
    # Calculer les totaux
    nb_articles = sum(item['quantite'] for item in panier.values())
    frais_livraison = 15.00 if sous_total < 100 else 0  # Livraison gratuite au-dessus de 100 TND
    total = sous_total + frais_livraison
    
    context = {
        'panier_detaille': panier_detaille,
        'sous_total': sous_total,
        'frais_livraison': frais_livraison,
        'total': total,
        'nb_articles': nb_articles,
    }
    
    return render(request, 'boutique/panier.html', context)

def modifier_quantite_panier(request, produit_id):
    """Modifier la quantité d'un produit dans le panier"""
    if request.method == 'POST':
        data = json.loads(request.body)
        nouvelle_quantite = int(data.get('quantite', 1))
        
        produit = get_object_or_404(Produit, id=produit_id)
        panier = request.session.get('panier', {})
        
        if str(produit_id) in panier:
            if nouvelle_quantite <= 0:
                # Supprimer l'article
                del panier[str(produit_id)]
                message = f'{produit.nom} retiré du panier'
            elif nouvelle_quantite > produit.stock:
                return JsonResponse({
                    'success': False,
                    'message': f'Stock insuffisant. Seulement {produit.stock} disponible(s)'
                })
            else:
                # Mettre à jour la quantité
                panier[str(produit_id)]['quantite'] = nouvelle_quantite
                message = f'Quantité mise à jour pour {produit.nom}'
            
            request.session['panier'] = panier
            request.session.modified = True
            
            # Recalculer les totaux
            nb_articles = sum(item['quantite'] for item in panier.values())
            sous_total = sum(item['prix'] * item['quantite'] for item in panier.values())
            
            return JsonResponse({
                'success': True,
                'message': message,
                'nb_articles': nb_articles,
                'sous_total': sous_total
            })
    
    return JsonResponse({'success': False, 'message': 'Erreur'})

def supprimer_du_panier(request, produit_id):
    """Supprimer un produit du panier"""
    if request.method == 'POST':
        panier = request.session.get('panier', {})
        
        if str(produit_id) in panier:
            produit_nom = panier[str(produit_id)]['nom']
            del panier[str(produit_id)]
            request.session['panier'] = panier
            request.session.modified = True
            
            nb_articles = sum(item['quantite'] for item in panier.values())
            
            return JsonResponse({
                'success': True,
                'message': f'{produit_nom} retiré du panier',
                'nb_articles': nb_articles
            })
    
    return JsonResponse({'success': False, 'message': 'Erreur'})

def count_panier(request):
    """Retourner le nombre d'articles dans le panier"""
    panier = request.session.get('panier', {})
    count = sum(item['quantite'] for item in panier.values())
    return JsonResponse({'count': count})

def vider_panier(request):
    """Vider complètement le panier"""
    if request.method == 'POST':
        request.session['panier'] = {}
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'message': 'Panier vidé',
            'nb_articles': 0
        })
    
    return JsonResponse({'success': False, 'message': 'Erreur'})


def detail_produit(request, pk):
    """Afficher les détails d'un produit"""
    produit = get_object_or_404(Produit, pk=pk, active=True)
    
    # Récupérer les images supplémentaires
    images_supplementaires = ImageProduit.objects.filter(produit=produit).order_by('ordre')
    
    # Produits similaires (même catégorie, excluant le produit actuel)
    produits_similaires = Produit.objects.filter(
        categorie=produit.categorie,
        active=True
    ).exclude(pk=pk)[:4]
    
    # Vérifier si le produit est dans le panier
    panier = request.session.get('panier', {})
    quantite_panier = panier.get(str(pk), {}).get('quantite', 0)
    
    context = {
        'produit': produit,
        'images_supplementaires': images_supplementaires,
        'produits_similaires': produits_similaires,
        'quantite_panier': quantite_panier,
    }
    
    return render(request, 'boutique/detail_produit.html', context)

