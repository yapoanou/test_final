from django.shortcuts import render

# Create your views here.
import hashlib
from difflib import SequenceMatcher
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Document

def calculer_ressemblance_texte(texte_a, texte_b):
    """
    Compare deux textes et renvoie un pourcentage de ressemblance.
    Exemple : 95.5 pour deux fichiers presque identiques.
    """
    detecteur = SequenceMatcher(None, texte_a, texte_b)
    pourcentage = detecteur.ratio() * 100
    return pourcentage

class UploadDocumentView(APIView):
    
    def post(self, request, *args, **kwargs):
        # On récupère le fichier envoyé par l'utilisateur
        fichier_recu = request.FILES.get('file')
        
        # Sécurité de base : si le panier est vide, on arrête tout
        if not fichier_recu:
            return Response(
                {"erreur": "Vous devez fournir un fichier."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # --- ÉTAPE 1 : LECTURE SÉCURISÉE (Pour protéger la mémoire) ---
        # On prépare le calcul de l'empreinte unique (le Hash)
        calculateur_empreinte = hashlib.sha256()
        contenu_texte_complet = ""
        
        # Au lieu de charger un gros fichier d'un coup, on le lit petit à petit (par morceaux)
        for morceau in fichier_recu.chunks():
            calculateur_empreinte.update(morceau)
            # On transforme le morceau en texte lisible pour pouvoir le comparer plus tard
            contenu_texte_complet += morceau.decode('utf-8', errors='ignore')
            
        # Voici l'empreinte unique finale du fichier reçu
        empreinte_unique = calculateur_empreinte.hexdigest()
        
        # --- ÉTAPE 2 : CAS DU DOUBLON PARFAIT (100% Identique) ---
        # On regarde dans la base de données si un fichier validé possède EXACTEMENT la même empreinte
        doublon_exact = Document.objects.filter(hash_sha256=empreinte_unique, statut='VALIDE').first()
        
        if doublon_exact:
            return Response({
                "statut": "REJETE",
                "message": f"Refusé : Le fichier '{fichier_recu.name}' est une copie exacte d'un fichier déjà existant."
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # --- ÉTAPE 3 : CAS DE LA FORTE SIMILARITÉ (>= 90%) ---
        # On récupère tous les fichiers sains déjà enregistrés pour comparer leur contenu
        tous_les_fichiers_valides = Document.objects.filter(statut='VALIDE')
        
        for ancien_document in tous_les_fichiers_valides:
            try:
                # On ouvre et on lit le contenu de l'ancien fichier stocké
                with ancien_document.fichier.open('r') as ancien_fichier:
                    contenu_ancien_fichier = ancien_fichier.read().decode('utf-8', errors='ignore')
                
                # On calcule le score de ressemblance entre le nouveau et l'ancien
                score_de_ressemblance = calculer_ressemblance_texte(contenu_texte_complet, contenu_ancien_fichier)
                
                # Si ça ressemble à 90% ou plus, on bloque et on demande l'avis du supérieur
                if score_de_ressemblance >= 90.0:
                    document_bloque = Document.objects.create(
                        nom=fichier_recu.name,
                        fichier=fichier_recu,
                        hash_sha256=empreinte_unique,
                        statut='ATTENTE_VALIDATION',
                        fichier_similaire=ancien_document,
                        score_similarite=round(score_de_ressemblance, 2)
                    )
                    return Response({
                        "statut": "ATTENTE",
                        "message": f"Alerte : Ce fichier ressemble à {round(score_de_ressemblance, 1)}% au fichier '{ancien_document.nom}'. En attente de l'approbation d'un supérieur.",
                        "id_document": document_bloque.id
                    }, status=status.HTTP_202_ACCEPTED)
                    
            except Exception:
                # Si un fichier existant a un problème de lecture, on passe au suivant sans bloquer l'application
                continue

        # --- ÉTAPE 4 : CAS DU FICHIER UNIQUE (Tout est bon) ---
        # Le fichier ne ressemble à aucun autre, on l'enregistre normalement
        nouveau_document = Document.objects.create(
            nom=fichier_recu.name,
            fichier=fichier_recu,
            hash_sha256=empreinte_unique,
            statut='VALIDE'
        )
        
        return Response({
            "statut": "SUCCES",
            "message": "Fichier unique détecté et enregistré avec succès.",
            "id_document": nouveau_document.id
        }, status=status.HTTP_201_CREATED)