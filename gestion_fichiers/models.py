from django.db import models

# Create your models here.
from django.db import models

class Document(models.Model):
    STATUT_CHOICES = [
        ('VALIDE', 'Validé et enregistré'),
        ('DOUBLON', 'Rejeté (Doublon exact)'),
        ('ATTENTE_VALIDATION', 'En attente de validation supérieur'),
    ]

    nom = models.CharField(max_length=255)
    fichier = models.FileField(upload_to='uploads/')
    # db_index=True permet des recherches instantanées dans la base de données
    hash_sha256 = models.CharField(max_length=64, blank=True, null=True, db_index=True) 
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='VALIDE')
    
    # Pour gérer le Cas 3 (Forte similarité)
    fichier_similaire = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    score_similarite = models.FloatField(null=True, blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} - {self.statut}"