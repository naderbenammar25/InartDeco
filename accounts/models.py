from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class ProfilUtilisateur(models.Model):
    """Profil étendu de l'utilisateur"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    telephone = models.CharField(max_length=20, blank=True)
    date_naissance = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    newsletter = models.BooleanField(default=False, verbose_name="S'abonner à la newsletter")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"
    
    def __str__(self):
        return f"Profil de {self.user.get_full_name() or self.user.username}"

class AdresseUtilisateur(models.Model):
    """Adresses de livraison/facturation de l'utilisateur"""
    TYPE_ADRESSE_CHOICES = [
        ('livraison', 'Livraison'),
        ('facturation', 'Facturation'),
        ('both', 'Livraison et Facturation'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='adresses')
    nom = models.CharField(max_length=100, help_text="Nom pour identifier cette adresse")
    prenom = models.CharField(max_length=100)
    nom_famille = models.CharField(max_length=100)
    adresse_ligne1 = models.CharField(max_length=255)
    adresse_ligne2 = models.CharField(max_length=255, blank=True)
    ville = models.CharField(max_length=100)
    code_postal = models.CharField(max_length=10)
    pays = models.CharField(max_length=100, default='Tunisie')
    telephone = models.CharField(max_length=20)
    type_adresse = models.CharField(max_length=20, choices=TYPE_ADRESSE_CHOICES, default='livraison')
    par_defaut = models.BooleanField(default=False, help_text="Adresse par défaut")
    active = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Adresse utilisateur"
        verbose_name_plural = "Adresses utilisateurs"
        ordering = ['-par_defaut', '-date_creation']
    
    def __str__(self):
        return f"{self.nom} - {self.ville}"
    
    def save(self, *args, **kwargs):
        # S'assurer qu'il n'y a qu'une seule adresse par défaut par utilisateur
        if self.par_defaut:
            AdresseUtilisateur.objects.filter(
                user=self.user, 
                type_adresse=self.type_adresse,
                par_defaut=True
            ).update(par_defaut=False)
        super().save(*args, **kwargs)

class CommandeInvite(models.Model):
    """Informations pour les commandes d'invités (sans compte)"""
    email = models.EmailField()
    prenom = models.CharField(max_length=100)
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    adresse_ligne1 = models.CharField(max_length=255)
    adresse_ligne2 = models.CharField(max_length=255, blank=True)
    ville = models.CharField(max_length=100)
    code_postal = models.CharField(max_length=10)
    pays = models.CharField(max_length=100, default='Tunisie')
    newsletter = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    # Token pour permettre le suivi de commande sans compte
    token_suivi = models.CharField(max_length=32, unique=True, blank=True)
    
    class Meta:
        verbose_name = "Commande invité"
        verbose_name_plural = "Commandes invités"
    
    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.email}"
    
    def save(self, *args, **kwargs):
        if not self.token_suivi:
            import uuid
            self.token_suivi = uuid.uuid4().hex
        super().save(*args, **kwargs)