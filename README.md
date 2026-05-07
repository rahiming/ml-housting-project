[![CI - Python Quality Checks](https://github.com/rahiming/ml-housting-project/actions/workflows/ci.yml/badge.svg)](https://github.com/rahiming/ml-housting-project/actions/workflows/ci.yml)

# ML Housing Project

Projet MLOps de prediction de prix immobiliers base sur le dataset California Housing.

L'application est composee de quatre briques :

- un pipeline d'entrainement local
- une couche de prediction reutilisable
- une API FastAPI
- une interface utilisateur Streamlit

Le workflow principal est simple :

1. entrainer un modele en local
2. publier le modele dans MinIO
3. demarrer le backend
4. laisser le backend telecharger le modele depuis MinIO
5. faire des predictions depuis l'API ou depuis Streamlit

## Objectifs

- separer le code d'entrainement du code d'inference
- stocker les modeles dans un stockage objet simple
- proposer un demarrage local reproductible avec Docker Compose
- valider la qualite du projet par tests, lint, formatage et scan securite

## Architecture

```text
ml-housing-project/
|-- backend/
|   |-- app.py
|   `-- storage/s3_client.py
|-- frontend/
|   `-- streamlit_app.py
|-- src/
|   |-- common/
|   |   `-- features.py
|   |-- prediction/
|   |   |-- config.py
|   |   |-- model_loader.py
|   |   |-- predict.py
|   |   `-- schemas.py
|   `-- training/
|       |-- data.py
|       |-- evaluate.py
|       |-- pipeline.py
|       |-- preprocessing.py
|       `-- train.py
|-- scripts/
|   `-- upload_model_to_minio.py
|-- tests/
|-- artifacts/
|   |-- models/
|   `-- metrics/
|-- Docs/
|   `-- user_manual.md
|-- docker-compose.yml
|-- main.py
`-- README.md
```

## Prerequis

### En local sans Docker

- Python 3.10
- pip
- environnement virtuel recommande

### Avec Docker

- Docker Desktop ou Docker Engine
- Docker Compose

## Variables d'environnement

Le projet fournit un modele d'environnement versionnable :

```powershell
Copy-Item .env.example .env
```

Variables importantes :

- `MINIO_ENDPOINT`
- `MINIO_ACCESS_KEY`
- `MINIO_SECRET_KEY`
- `MINIO_BUCKET_MODELS`
- `MODEL_OBJECT_NAME`
- `LOCAL_MODEL_PATH`
- `BACKEND_URL`

## Installation locale

### Windows PowerShell

```powershell
python -m venv mon_env
.\mon_env\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
pip install -e ".[dev]"
Copy-Item .env.example .env
```

### Linux ou macOS

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e ".[dev]"
cp .env.example .env
```

## Entrainer un modele

```powershell
python main.py
```

Effets attendus :

- creation d'un modele versionne dans `artifacts/models`
- mise a jour de `model_latest.joblib`
- creation d'un fichier de metriques dans `artifacts/metrics`

## Publier le modele dans MinIO

```powershell
python scripts/upload_model_to_minio.py
```

Le script :

- attend que MinIO soit pret
- cree le bucket s'il n'existe pas
- envoie `artifacts/models/model_latest.joblib`

## Demarrer l'application avec Docker Compose

```powershell
docker compose up -d --build
```

Services exposes :

- backend FastAPI : `http://localhost:8000`
- documentation API : `http://localhost:8000/docs`
- frontend Streamlit : `http://localhost:8501`
- console MinIO : `http://localhost:9001`

Identifiants MinIO locaux :

- utilisateur : `admin`
- mot de passe : `password123`

## Mise en route recommandee

1. installer les dependances
2. copier `.env.example` vers `.env`
3. entrainer un modele avec `python main.py`
4. demarrer Docker Compose
5. publier le modele avec `python scripts/upload_model_to_minio.py`
6. verifier `http://localhost:8000/health`
7. ouvrir `http://localhost:8501`
8. lancer une prediction

## Faire une prediction via l'API

### Exemple curl

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "median_income": 3.5,
    "housing_median_age": 20.0,
    "average_rooms": 5.0,
    "average_bedrooms": 1.0,
    "population": 1000.0,
    "average_occupancy": 3.0,
    "latitude": 34.0,
    "longitude": -118.0
  }'
```

### Reponse attendue

```json
{
  "prediction": 1.9648099999999993
}
```

La prediction est exprimee en unite de `100 000 $`.

## Lancer le frontend sans Docker

```powershell
streamlit run frontend/streamlit_app.py
```

Si le backend n'est pas sur l'URL par defaut :

```powershell
$env:BACKEND_URL="http://127.0.0.1:8000"
streamlit run frontend/streamlit_app.py
```

## Tests et qualite

### Tests

```powershell
pytest -v --cov=src
```

### Lint

```powershell
ruff check .
```

### Formatage

```powershell
ruff format --check .
black --check .
```

### Securite

```powershell
bandit -r src/prediction/ src/common/ backend/ frontend/
```

## Logs et observabilite

Le code journalise les actions critiques :

- demarrage et arret du backend
- telechargement du modele depuis MinIO
- chargement en memoire du modele
- conversion du schema API vers le schema du modele
- execution du pipeline d'entrainement
- upload vers MinIO
- appels du frontend vers l'API

Avec Docker :

```powershell
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f minio
```

## Depannage

### Erreur 422 sur `/predict`

Verifier :

- les noms de champs du JSON
- le type des valeurs envoyees

### Erreur 500 sur `/predict`

Verifier :

- la presence du modele dans MinIO
- les logs du backend
- la compatibilite entre le schema API et le pipeline charge

### Frontend inaccessible

Verifier :

- `BACKEND_URL`
- `docker compose ps`
- `http://localhost:8000/health`

### Modele absent dans MinIO

Executer :

```powershell
python main.py
python scripts/upload_model_to_minio.py
```

## Documentation complementaire

- manuel utilisateur detaille : [USER_MANUAL.md](/d:/Projects/ml-housing-project/USER_MANUAL.md)
- workflow CI : [.github/workflows/ci.yml](/d:/Projects/ml-housing-project/.github/workflows/ci.yml)

## Arreter les services

```powershell
docker compose down
```

Pour supprimer aussi les volumes :

```powershell
docker compose down -v
```
