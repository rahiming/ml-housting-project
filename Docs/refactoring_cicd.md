# Stratégie de Refactoring pour la CI/CD

## Objectif
Séparer le cycle de vie de l'entraînement (Training) du cycle de vie de l'application (Inférence) afin d'optimiser les pipelines CI/CD. L'objectif est de ne déployer en production que le strict nécessaire : le backend, le frontend, l'artéfact du modèle, et la logique de prédiction.

## 1. Séparation Structurelle du Code
Actuellement, la logique est regroupée dans `src/ml_housing`. Nous allons diviser cette structure :

- **`src/ml_housing/core/` (Inférence/Production)** :
    - Contient uniquement le code nécessaire à l'exécution : `features.py` (ingénierie de variables) et `preprocessing.py` (définition de la structure du pipeline).
    - Ce module est le seul code "ML" embarqué dans l'image de production.
- **`src/ml_housing/training/` (Entraînement/Recherche)** :
    - Contient `train.py`, `data_loader.py`, et les scripts d'évaluation.
    - Ce dossier est ignoré lors du déploiement applicatif.

## 2. Gestion des Dépendances
Distinction entre les besoins de l'application et ceux de l'entraînement :

- **`requirements.txt`** : Dépendances minimales pour l'inférence (FastAPI, Uvicorn, Pandas, Scikit-Learn, Joblib).
- **`requirements-dev.txt`** : Inclut le précédent + outils d'entraînement et de visualisation (Jupyter, Matplotlib, Seaborn, Pytest).

## 3. Gestion de l'Artéfact (Le Modèle)
Le modèle ne doit pas être traité comme du code source, mais comme une donnée d'entrée.

- **Stockage** : Utilisation des GitHub Actions Artifacts (ou un bucket S3/GCS à terme) pour stocker les fichiers `.joblib`.
- **Versionnement** : Le backend doit pouvoir identifier la version du modèle à charger (via une variable d'environnement ou un nom de fichier standardisé).

## 4. Stratégie GitHub Actions
Mise en place de deux workflows découplés :

### Workflow d'Entraînement (`train.yml`)
- **Déclencheur** : Manuel ou modification dans `src/ml_housing/training/`.
- **Rôle** : Lancer l'entraînement, valider les métriques de performance, et sauvegarder le `.joblib` comme artéfact.

### Workflow de Déploiement (`deploy.yml`)
- **Déclencheur** : Push sur `main` ou modification dans `backend/`, `frontend/`, ou `src/ml_housing/core/`.
- **Rôle** : 
    1. Linter et tester le code (Backend & Logic ML Core).
    2. Récupérer le dernier artéfact de modèle validé.
    3. Construire et déployer l'application sans le code d'entraînement.

## 5. Point de Vigilance Technique : La Sérialisation
Pour que `joblib.load()` fonctionne dans le backend sans la présence du code d'entraînement :

- Le pipeline doit être entraîné en utilisant des imports basés sur le futur module `core` (ex: `from ml_housing.core.features import engineer_features`).
- Le chemin de recherche Python (`PYTHONPATH`) doit être configuré de manière identique lors de l'entraînement et lors de l'inférence pour assurer la désérialisation correcte des fonctions personnalisées.

---
*Document créé le : 24 mai 2024*
*Statut : Proposition en attente d'implémentation*