from django.urls import path
from django.contrib.auth.views import LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentification
    path('connexion/', views.ConnexionView.as_view(), name='login'),
    path('inscription/', views.inscription_view, name='inscription'),
    path('deconnexion/', views.logout_view, name='logout'),    
    # Récupération mot de passe
    path('mot-de-passe/reset/', PasswordResetView.as_view(
        template_name='accounts/password_reset.html',
        email_template_name='accounts/password_reset_email.html',
        success_url='/accounts/mot-de-passe/reset/done/'
    ), name='password_reset'),
    
    path('mot-de-passe/reset/done/', PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    
    path('mot-de-passe/reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url='/accounts/mot-de-passe/reset/complete/'
    ), name='password_reset_confirm'),
    
    path('mot-de-passe/reset/complete/', PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # Profil utilisateur
    path('profil/', views.profil_view, name='profil'),
    path('profil/modifier/', views.modifier_profil_view, name='modifier_profil'),
    
    # Gestion des adresses
    path('adresse/ajouter/', views.ajouter_adresse_view, name='ajouter_adresse'),
    path('adresse/<int:pk>/modifier/', views.modifier_adresse_view, name='modifier_adresse'),
    path('adresse/<int:pk>/supprimer/', views.supprimer_adresse_view, name='supprimer_adresse'),
    
    # API
    path('api/check-username/', views.check_username_disponible, name='check_username'),
]