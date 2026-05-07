# Manuel d'utilisation

## Public vise

Ce manuel est destine a un futur utilisateur qui doit :

- installer l'application
- la demarrer localement
- publier un modele
- lancer des predictions
- comprendre les incidents les plus frequents

## Vue d'ensemble

L'application estime un prix immobilier a partir de caracteristiques de quartier.

Le cycle normal d'utilisation est :

1. entrainer ou recuperer un modele
2. stocker ce modele dans MinIO
3. demarrer le backend FastAPI
4. utiliser soit l'interface Streamlit soit l'API `/predict`

## Installation pas a pas

### Recuperer le projet

```powershell
git clone https://github.com/rahiming/ml-housting-project.git
cd ml-housing-project
```

### Preparer Python

```powershell
python -m venv mon_env
.\mon_env\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
pip install -e ".[dev]"
```

### Preparer l'environnement

```powershell
Copy-Item .env.example .env
```

## Utilisation avec Docker Compose

### Demarrer

```powershell
docker compose up -d --build
```

### Verifier l'etat

```powershell
docker compose ps
```

Services attendus :

- `backend`
- `frontend`
- `minio`

### Ouvrir les interfaces

- frontend : `http://localhost:8501`
- API : `http://localhost:8000/docs`
- MinIO : `http://localhost:9001`

## Entrainer un modele

```powershell
python main.py
```

Sorties attendues :

- `artifacts/models/model_vX.joblib`
- `artifacts/models/model_latest.joblib`
- `artifacts/metrics/metrics_vX.json`

## Publier le modele dans MinIO

```powershell
python scripts/upload_model_to_minio.py
```

## Faire une prediction depuis le frontend

1. ouvrir `http://localhost:8501`
2. remplir le formulaire
3. cliquer sur `Calculer l'estimation`
4. lire le resultat affiche

## Faire une prediction via l'API

```powershell
$body = @{
  median_income = 3.5
  housing_median_age = 20.0
  average_rooms = 5.0
  average_bedrooms = 1.0
  population = 1000.0
  average_occupancy = 3.0
  latitude = 34.0
  longitude = -118.0
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8000/predict -Method Post -ContentType "application/json" -Body $body
```

Exemple de reponse :

```json
{
  "prediction": 1.9648099999999993
}
```

## Verification rapide

### Sante du backend

```powershell
Invoke-RestMethod -Uri http://localhost:8000/health
```

### Logs backend

```powershell
docker compose logs -f backend
```

### Verification du modele dans MinIO

1. ouvrir `http://localhost:9001`
2. se connecter avec `admin / password123`
3. ouvrir le bucket `ml-models`
4. verifier `model_latest.joblib`

## Commandes utiles

### Relancer seulement le backend

```powershell
docker compose up -d --build backend
```

### Relancer seulement le frontend

```powershell
docker compose up -d --build frontend
```

### Arreter l'ensemble

```powershell
docker compose down
```

### Arreter et supprimer les volumes

```powershell
docker compose down -v
```

## Pannes courantes

### Le backend ne demarre pas

Verifier :

- les variables `MINIO_*`
- la disponibilite de MinIO
- la presence du modele dans le bucket

### Le frontend ne joint pas le backend

Verifier :

- `BACKEND_URL`
- le port `8000`
- `docker compose ps`

### Les predictions echouent

Verifier :

- que `model_latest.joblib` est bien le bon modele
- qu'il a bien ete upload dans MinIO
- que le backend a ete redemarre apres mise a jour du modele

## Maintenance recommandee

- executer `pytest`, `ruff`, `black` et `bandit` avant toute livraison
- lire les logs du backend apres tout redeploiement
- documenter toute evolution du schema d'entree
