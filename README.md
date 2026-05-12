# ML Housing Project

Projet MLOps de prédiction de prix immobiliers basé sur le dataset California Housing.

L'application embarque un mécanisme d'expérimentation A/B : chaque requête est routée
de façon déterministe vers le modèle A (RandomForest) ou le modèle B (GradientBoosting)
selon l'identifiant utilisateur.

## Architecture

```
ml-housing-project/
├── backend/
│   ├── app.py                      API FastAPI (predict, health, A/B routing)
│   ├── services/
│   │   ├── ab_router.py            Routage déterministe A/B par hash MD5
│   │   ├── experiment_logger.py    Logs vers PostgreSQL (prod) ou JSONL (local)
│   │   └── model_registry.py       Registre des modèles A et B
│   └── storage/
│       └── hf_client.py            Client HuggingFace Hub
├── frontend/
│   └── streamlit_app.py
├── src/
│   ├── common/features.py
│   ├── prediction/
│   │   ├── model_loader.py
│   │   ├── predict.py
│   │   └── schemas.py
│   └── training/
│       ├── data.py
│       ├── pipeline.py             Pipeline ML + tracking MLFlow
│       ├── preprocessing.py
│       ├── train.py
│       └── evaluate.py
├── notebooks/
│   ├── 02_train_ab_models.ipynb    Entraînement des modèles A/B + MLFlow
│   └── 03_ab_analysis.ipynb        Analyse des logs A/B (PostgreSQL ou JSONL)
├── scripts/
│   ├── upload_model_to_hf.py       Upload Registry MLFlow → HuggingFace Hub
│   └── generate_mlflow_guide.py    Génère le guide MLFlow (docs/)
├── tests/
├── artifacts/
│   ├── models/
│   └── metrics/
├── .github/workflows/
│   ├── ci.yml                      Lint, tests, sécurité
│   └── deploy-production.yml       Re-déploiement manuel d'urgence
├── docker-compose.yml
├── main.py
├── USER_MANUAL.md
└── README.md
```

## Pipeline MLOps

```
notebooks/02_train_ab_models.ipynb
        ↓  mlflow.log_model → registered_model_name
MLFlow Model Registry  (mlruns/ local)
        ↓  transition_model_version_stage → Production
scripts/upload_model_to_hf.py
        ↓  charge les modèles Production → HuggingFace Hub
Backend FastAPI (Render)
        ↓  télécharge les .joblib depuis HF Hub au démarrage
Prédictions A/B en production
```

## Prérequis

- Python 3.10+
- Comptes gratuits : [HuggingFace](https://huggingface.co), [Render](https://render.com), [Neon](https://neon.tech) (optionnel pour les logs)

## Installation locale

```powershell
python -m venv mon_env
.\mon_env\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
pip install -e ".[dev]"
Copy-Item .env.example .env
# Remplir .env avec vos propres valeurs
```

## Variables d'environnement

Copier `.env.example` vers `.env` et renseigner :

| Variable | Description |
|----------|-------------|
| `HF_TOKEN` | Token HuggingFace (huggingface.co/settings/tokens) |
| `HF_REPO_ID` | `<votre-username>/<nom-du-repo>` sur HF Hub |
| `DATABASE_URL` | URL PostgreSQL Neon (optionnel — logs A/B durables) |
| `MODEL_OBJECT_NAME` | Nom du fichier latest (défaut : `model_latest.joblib`) |
| `MODEL_A_OBJECT_NAME` | Nom du modèle A (défaut : `model_v1.joblib`) |
| `MODEL_B_OBJECT_NAME` | Nom du modèle B (défaut : `model_v2.joblib`) |
| `AB_TRAFFIC_B_PERCENT` | % de trafic vers le modèle B (défaut : `50`) |
| `BACKEND_URL` | URL du backend pour le frontend |

## Entraîner les modèles

### Pipeline principal (modèle de production)

```powershell
python main.py
```

Sorties : `artifacts/models/model_vX.joblib`, `artifacts/models/model_latest.joblib`

### Modèles A/B (notebook)

Exécuter `notebooks/02_train_ab_models.ipynb` en entier.

Les modèles sont enregistrés dans MLFlow sous les noms `housing_model_A` et `housing_model_B`.

## Workflow MLFlow

```powershell
# 1. Lancer l'UI MLFlow pour comparer les runs
mlflow ui
# Ouvrir http://127.0.0.1:5000

# 2. Promouvoir les modèles A et B en Production
python -c "
from mlflow.tracking import MlflowClient
import warnings; warnings.filterwarnings('ignore')
client = MlflowClient()
for name in ['housing_model_A', 'housing_model_B']:
    versions = client.search_model_versions(f\"name='{name}'\")
    latest = max(versions, key=lambda v: int(v.version))
    client.transition_model_version_stage(name, latest.version, 'Production', archive_existing_versions=True)
    print(f'{name} v{latest.version} => Production')
"

# 3. Uploader vers HuggingFace Hub (nécessite HF_TOKEN et HF_REPO_ID dans .env)
python scripts/upload_model_to_hf.py
```

## API de prédiction

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

### Format de réponse

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
| `prediction` | Prix estimé en centaines de milliers de dollars |
| `variant` | Modèle utilisé : `A` ou `B` |
| `execution_mode` | `ab_registry` si A et B disponibles, `legacy_fallback` sinon |
| `latency_ms` | Temps de traitement serveur en millisecondes |

## Tests et qualité

```powershell
pytest -v --cov=src --cov=backend     # tests et couverture
ruff check .                           # lint
ruff format --check .                  # format
bandit -r src/ backend/                # sécurité
```

Le hook `pre-push` lance ces vérifications automatiquement à chaque push :

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install_git_hook.ps1
```

## Déploiement (Render.com)

Le guide complet est disponible dans `Docs/Guide_Deploiement_Render.docx`.

Architecture de production :

```
Utilisateur → Frontend Streamlit (Render) → Backend FastAPI (Render) → HuggingFace Hub
```

Variables à définir dans le service **backend** Render :
`HF_TOKEN`, `HF_REPO_ID`, `DATABASE_URL` (optionnel), `MODEL_OBJECT_NAME`,
`MODEL_A_OBJECT_NAME`, `MODEL_B_OBJECT_NAME`, `AB_TRAFFIC_B_PERCENT`

## Documentation

| Guide | Contenu |
|-------|---------|
| `Docs/Guide_MLFlow.docx` | Intégration MLFlow + MLOps + Registry |
| `Docs/Guide_Deploiement_Render.docx` | Déploiement sur Render.com |
| `Docs/Guide_AB_Deployment.docx` | Architecture A/B testing |
| `USER_MANUAL.md` | Manuel d'utilisation complet |
