from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import ProfilUtilisateur, AdresseUtilisateur, CommandeInvite

class InscriptionForm(UserCreationForm):
    """Formulaire d'inscription personnalisé"""
    email = forms.EmailField(required=True)
    prenom = forms.CharField(max_length=100, required=True)
    nom = forms.CharField(max_length=100, required=True)
    telephone = forms.CharField(max_length=20, required=False)
    newsletter = forms.BooleanField(required=False, initial=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'prenom', 'nom', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = "Nom d'utilisateur unique pour se connecter"
        self.fields['password1'].help_text = "Au moins 8 caractères"
        
        # Ajouter des classes CSS Bootstrap
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'newsletter':
                field.widget.attrs['class'] = 'form-check-input'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['prenom']
        user.last_name = self.cleaned_data['nom']
        
        if commit:
            user.save()
            # Créer le profil utilisateur
            ProfilUtilisateur.objects.create(
                user=user,
                telephone=self.cleaned_data.get('telephone', ''),
                newsletter=self.cleaned_data.get('newsletter', False)
            )
        return user

class ConnexionForm(AuthenticationForm):
    """Formulaire de connexion personnalisé"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'Nom d\'utilisateur'
        self.fields['password'].widget.attrs['placeholder'] = 'Mot de passe'

class ProfilForm(forms.ModelForm):
    """Formulaire pour modifier le profil"""
    prenom = forms.CharField(max_length=100, required=True)
    nom = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = ProfilUtilisateur
        fields = ['telephone', 'date_naissance', 'avatar', 'newsletter']
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'newsletter': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['prenom'].initial = self.user.first_name
            self.fields['nom'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email
            
        self.fields['prenom'].widget.attrs['class'] = 'form-control'
        self.fields['nom'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
    
    def save(self, commit=True):
        profil = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data['prenom']
            self.user.last_name = self.cleaned_data['nom']
            self.user.email = self.cleaned_data['email']
            if commit:
                self.user.save()
        
        if commit:
            profil.save()
        return profil

class AdresseForm(forms.ModelForm):
    """Formulaire pour ajouter/modifier une adresse"""
    class Meta:
        model = AdresseUtilisateur
        fields = [
            'nom', 'prenom', 'nom_famille', 'adresse_ligne1', 'adresse_ligne2',
            'ville', 'code_postal', 'pays', 'telephone', 'type_adresse', 'par_defaut'
        ]
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'nom_famille': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse_ligne1': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse_ligne2': forms.TextInput(attrs={'class': 'form-control'}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'code_postal': forms.TextInput(attrs={'class': 'form-control'}),
            'pays': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'type_adresse': forms.Select(attrs={'class': 'form-select'}),
            'par_defaut': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CommandeInviteForm(forms.ModelForm):
    """Formulaire pour les commandes sans compte"""
    class Meta:
        model = CommandeInvite
        fields = [
            'email', 'prenom', 'nom', 'telephone', 'adresse_ligne1', 'adresse_ligne2',
            'ville', 'code_postal', 'pays', 'newsletter'
        ]
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': True}),
            'prenom': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'nom': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'adresse_ligne1': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'adresse_ligne2': forms.TextInput(attrs={'class': 'form-control'}),
            'ville': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'code_postal': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'pays': forms.TextInput(attrs={'class': 'form-control', 'value': 'Tunisie'}),
            'newsletter': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'email': 'Adresse email',
            'prenom': 'Prénom',
            'nom': 'Nom de famille',
            'telephone': 'Téléphone',
            'adresse_ligne1': 'Adresse (ligne 1)',
            'adresse_ligne2': 'Complément d\'adresse (optionnel)',
            'ville': 'Ville',
            'code_postal': 'Code postal',
            'pays': 'Pays',
            'newsletter': 'Recevoir la newsletter InArtDeco',
        }