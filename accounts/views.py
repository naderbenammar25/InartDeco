from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.http import JsonResponse

from .forms import InscriptionForm, ConnexionForm, ProfilForm, AdresseForm
from .models import ProfilUtilisateur, AdresseUtilisateur


from django.contrib.auth import logout
from django.shortcuts import redirect

class ConnexionView(LoginView):
    """Vue de connexion personnalisée"""
    form_class = ConnexionForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        return next_url or reverse_lazy('boutique:accueil')

def inscription_view(request):
    """Vue d'inscription"""
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Compte créé pour {username}! Vous pouvez maintenant vous connecter.')
            
            # Connexion automatique après inscription
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1']
            )
            if user:
                login(request, user)
                return redirect('boutique:accueil')
    else:
        form = InscriptionForm()
    
    return render(request, 'accounts/inscription.html', {'form': form})

@login_required
def profil_view(request):
    """Vue du profil utilisateur"""
    profil, created = ProfilUtilisateur.objects.get_or_create(user=request.user)
    adresses = AdresseUtilisateur.objects.filter(user=request.user, active=True)
    
    context = {
        'profil': profil,
        'adresses': adresses,
    }
    return render(request, 'accounts/profil.html', context)

@login_required
def modifier_profil_view(request):
    """Vue pour modifier le profil"""
    profil, created = ProfilUtilisateur.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfilForm(request.POST, request.FILES, instance=profil, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil mis à jour avec succès!')
            return redirect('accounts:profil')
    else:
        form = ProfilForm(instance=profil, user=request.user)
    
    return render(request, 'accounts/modifier_profil.html', {'form': form})

@login_required
def ajouter_adresse_view(request):
    """Vue pour ajouter une adresse"""
    if request.method == 'POST':
        form = AdresseForm(request.POST)
        if form.is_valid():
            adresse = form.save(commit=False)
            adresse.user = request.user
            adresse.save()
            messages.success(request, 'Adresse ajoutée avec succès!')
            return redirect('accounts:profil')
    else:
        form = AdresseForm()
    
    return render(request, 'accounts/ajouter_adresse.html', {'form': form})

@login_required
def modifier_adresse_view(request, pk):
    """Vue pour modifier une adresse"""
    adresse = get_object_or_404(AdresseUtilisateur, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = AdresseForm(request.POST, instance=adresse)
        if form.is_valid():
            form.save()
            messages.success(request, 'Adresse modifiée avec succès!')
            return redirect('accounts:profil')
    else:
        form = AdresseForm(instance=adresse)
    
    return render(request, 'accounts/modifier_adresse.html', {'form': form, 'adresse': adresse})

@login_required
def supprimer_adresse_view(request, pk):
    """Vue pour supprimer une adresse"""
    adresse = get_object_or_404(AdresseUtilisateur, pk=pk, user=request.user)
    
    if request.method == 'POST':
        adresse.active = False
        adresse.save()
        messages.success(request, 'Adresse supprimée avec succès!')
        return redirect('accounts:profil')
    
    return render(request, 'accounts/supprimer_adresse.html', {'adresse': adresse})

def check_username_disponible(request):
    """API pour vérifier si un nom d'utilisateur est disponible"""
    username = request.GET.get('username')
    if username:
        from django.contrib.auth.models import User
        exists = User.objects.filter(username=username).exists()
        return JsonResponse({'disponible': not exists})
    return JsonResponse({'disponible': False})



def logout_view(request):
    """Vue de déconnexion qui accepte GET et POST"""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('boutique:accueil')