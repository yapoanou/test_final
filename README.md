# Test Technique - API de Gestion de Fichiers et Détection de Doublons

Ce projet contient l'API développée pour évaluer la capacité à gérer des fichiers, détecter les doublons et implémenter une logique de validation métier avec seuil de similarité.

## Règles Métier Implémentées
1. **Upload de fichier :** Point d'entrée pour l'enregistrement de nouveaux fichiers.
2. **Vérification d'existence et similarité :** Algorithme de détection basé sur le nom du fichier, son contenu et le calcul de son empreinte (Hash).
3. **Gestion des cas d'usage :**
   * **Cas 1 (Fichier totalement différent) :** Le fichier est enregistré normalement.
   * **Cas 2 (Fichier identique) :** L'upload est refusé et le système signale que le fichier existe déjà pour éviter la redondance de stockage.

## Installation et Lancement du Projet

### 1. Cloner le projet
```bash
git clone [https://github.com/yapoanou/test_final.git](https://github.com/yapoanou/test_final.git)
cd test_final