[![CI Pipeline](https://github.com/rahiming/ml-housting-project/actions/workflows/ci.yml/badge.svg)](https://github.com/rahiming/ml-housting-project/actions/workflows/ci.yml)

# ML Housing Project

Projet MLOps de prediction de prix immobiliers base sur le dataset California Housing.

L'application embarque un mecanisme d'experimentation A/B : chaque requete est routee
de facon deterministe vers le modele A ou B selon l'identifiant utilisateur.

## Architecture

```
ml-housing-project/
|-- backend/
|   |-- app.py                     API FastAPI (predict, health, A/B routing)
|   |-- services/
|   |   |-- ab_router.py           Routage deterministe A/B par hash MD5
|   |   |-- experiment_logger.py   Journalisation des experiences
|   |   `-- model_registry.py      Registre des modeles A et B
|   `-- storage/
|       `-- s3_client.py           Client MinIO / S3
|-- frontend/
|   `-- streamlit_app.py
|-- src/
|   |-- common/features.py
|   |-- prediction/
|   |   |-- config.py
|   |   |-- model_loader.py
|   |   |-- predict.py
|   |   `-- schemas.py
|   `-- training/
|       |-- data.py
|       |-- pipeline.py
|       |-- preprocessing.py
|       |-- train.py
|       `-- evaluate.py
|-- scripts/
|   `-- upload_model_to_minio.py
|-- tests/
|-- artifacts/
|   |-- models/
|   `-- metrics/
|-- .github/workflows/
|   |-- ci.yml                     Lint, tests, securite, staging + production deploy
|   `-- deploy-production.yml      Re-deploiement manuel d'urgence
|-- docker-compose.yml
|-- main.py
|-- USER_MANUAL.md
`-- README.md
```

## Prerequis

- Python 3.10+
- Docker Desktop (pour le mode Compose)

## Demarrage rapide avec Docker Compose

```powershell
# 1. Entrainer les modeles (une seule fois, ou apres modification)
python main.py

# 2. Demarrer tous les services (build + seed automatique des modeles)
docker compose up -d --build
```

Le service `model-seeder` uploade automatiquement les modeles dans MinIO au
demarrage. Le backend attend sa completion avant de se lancer.

| Interface | URL |
|-----------|-----|
| Frontend Streamlit | `http://localhost:8501` |
| API FastAPI | `http://localhost:8000/docs` |
| Console MinIO | `http://localhost:9001` (admin / password123) |

## Installation locale (sans Docker)

```powershell
python -m venv mon_env
.\mon_env\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
pip install -e ".[dev]"
Copy-Item .env.example .env
```

## Entrainer les modeles

```powershell
python main.py
```

Sorties :

- `artifacts/models/model_vX.joblib`
- `artifacts/models/model_latest.joblib`
- `artifacts/metrics/metrics_vX.json`

Les trois fichiers `model_latest.joblib`, `model_v1.joblib` et `model_v2.joblib`
doivent etre presents dans `artifacts/models/` pour activer le mode A/B complet.

## API de prediction

### Exemple PowerShell

```powershell
$body = @{
  user_id            = "alice"
  median_income      = 3.5
  housing_median_age = 20.0
  average_rooms      = 5.0
  average_bedrooms   = 1.0
  population         = 1000.0
  average_occupancy  = 3.0
  latitude           = 34.0
  longitude          = -118.0
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8000/predict -Method Post `
  -ContentType "application/json" -Body $body
```

### Exemple curl

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"user_id":"alice","median_income":3.5,"housing_median_age":20.0,
       "average_rooms":5.0,"average_bedrooms":1.0,"population":1000.0,
       "average_occupancy":3.0,"latitude":34.0,"longitude":-118.0}'
```

### Format de reponse

```json
{
  "prediction": 1.81,
  "variant": "B",
  "model_version": "model_v2",
  "execution_mode": "ab_registry",
  "latency_ms": 36.1,
  "request_id": "9c0f4d4c-..."
}
```

| Champ | Description |
|-------|-------------|
| `prediction` | Prix estime en centaines de milliers de dollars |
| `variant` | Modele utilise : `A` ou `B` |
| `model_version` | `model_v1`, `model_v2` ou `legacy_single_model` |
| `execution_mode` | `ab_registry` si A et B disponibles, `legacy_fallback` sinon |
| `latency_ms` | Temps de traitement serveur en millisecondes |
| `request_id` | UUID unique pour le tracage |

Le champ `user_id` est optionnel (defaut : `"anonymous"`). Le routage est
deterministe — le meme `user_id` retourne toujours la meme variante.

## Variables d'environnement

Copier `.env.example` vers `.env` et ajuster si necessaire.

| Variable | Description |
|----------|-------------|
| `MINIO_ENDPOINT` | URL MinIO ou endpoint S3-compatible |
| `MINIO_ACCESS_KEY` | Cle d'acces |
| `MINIO_SECRET_KEY` | Cle secrete |
| `MINIO_BUCKET_MODELS` | Nom du bucket (defaut : `ml-models`) |
| `MODEL_OBJECT_NAME` | Modele principal (defaut : `model_latest.joblib`) |
| `MODEL_A_OBJECT_NAME` | Modele variante A (defaut : `model_v1.joblib`) |
| `MODEL_B_OBJECT_NAME` | Modele variante B (defaut : `model_v2.joblib`) |
| `AB_TRAFFIC_B_PERCENT` | Pourcentage de trafic vers B (defaut : `50`) |
| `BACKEND_URL` | URL du backend pour le frontend |

## Tests et qualite

### Workflow local complet (pre-push)

```powershell
# Verification seule
powershell -ExecutionPolicy Bypass -File scripts\workflow_local.ps1

# Correction automatique + verification
powershell -ExecutionPolicy Bypass -File scripts\workflow_local.ps1 -Fix

# Avec build Docker et scans d'images
powershell -ExecutionPolicy Bypass -File scripts\workflow_local.ps1 -Fix -WithDocker
```

Installe le hook `pre-push` pour que le workflow se lance automatiquement a chaque push :

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install_git_hook.ps1
```

### Commandes individuelles

```powershell
pytest -v --cov=src --cov=backend     # tests et couverture
ruff check .                           # lint
ruff format --check .                  # format (ruff)
black --check .                        # format (black)
bandit -r src/ backend/                # securite
pip-audit                              # vulnerabilites dependances
```

## CI/CD

Le pipeline GitHub Actions (`ci.yml`) execute en sequence :

| Job | Declenchement |
|-----|---------------|
| lint, format, tests, security, dependency-vulnerabilities, structure | push + PR sur `develop` et `main` |
| docker-validate (build + smoke tests + Trivy) | idem, apres les jobs precedents |
| deploy-staging (push images GHCR `:staging`) | push sur `develop` uniquement |
| publish-prod-images + deploy-render | push sur `main` uniquement |

Le deploiement en production se declenche automatiquement lors du merge de
`develop` vers `main`. Un workflow de re-deploiement manuel est disponible
dans l'onglet **Actions → Production Deploy**.

## Deploiement en production (Render.com)

L'application est deployee sur Render.com avec Cloudflare R2 comme stockage.

```
Utilisateur → Frontend Streamlit (Render) → Backend FastAPI (Render) → Cloudflare R2
```

Le guide de deploiement pas a pas est disponible dans `docs/Guide_Deploiement_Render.docx`.
Les variables et secrets necessaires sont documentes dans [USER_MANUAL.md](USER_MANUAL.md).

## Logs

```powershell
docker compose logs -f backend
docker compose logs -f frontend
```

## Depannage rapide

| Symptome | Cause probable |
|----------|----------------|
| `execution_mode: legacy_fallback` | `model_v1.joblib` ou `model_v2.joblib` absent dans MinIO |
| Erreur 500 sur `/predict` | Modele non charge — verifier les logs backend |
| Erreur 422 sur `/predict` | Champ manquant ou type incorrect dans le JSON |
| Frontend n'atteint pas le backend | Verifier `BACKEND_URL` et `docker compose ps` |

## Arreter les services

```powershell
docker compose down       # arret simple
docker compose down -v    # arret + suppression des volumes MinIO
```
