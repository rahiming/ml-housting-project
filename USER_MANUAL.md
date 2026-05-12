# Manuel d'utilisation

## Public visé

Ce manuel est destiné à un étudiant ou développeur qui doit :

- installer et démarrer l'application en local
- entraîner les modèles et les publier sur HuggingFace Hub
- lancer des prédictions via le frontend ou l'API
- déployer l'application en production sur Render.com
- comprendre le workflow MLFlow (tracking → registry → déploiement)

---

## Vue d'ensemble

L'application estime un prix immobilier à partir de caractéristiques de quartier.
Elle embarque un mécanisme d'expérimentation A/B : chaque requête est routée
de façon déterministe vers le modèle A (RandomForest, champion) ou le modèle B
(GradientBoosting, challenger) selon l'identifiant utilisateur.

Cycle normal d'utilisation :

1. Entraîner les modèles (pipeline ou notebook)
2. Valider les métriques dans MLFlow UI
3. Promouvoir les meilleurs modèles en stage Production dans le Registry
4. Uploader vers HuggingFace Hub via `upload_model_to_hf.py`
5. Le backend Render charge les modèles depuis HF Hub au démarrage

---

## Prérequis

Créer les comptes suivants (tous gratuits) :

| Service | Usage | Lien |
|---------|-------|------|
| HuggingFace | Stockage des modèles | huggingface.co |
| Render | Hébergement backend + frontend | render.com |
| Neon | Logs PostgreSQL A/B (optionnel) | neon.tech |

---

## Installation locale pas à pas

### Préparer Python

```powershell
python -m venv mon_env
.\mon_env\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
pip install -e ".[dev]"
```

### Configurer l'environnement

```powershell
Copy-Item .env.example .env
```

Ouvrir `.env` et renseigner :

```
HF_TOKEN=<token depuis huggingface.co/settings/tokens>
HF_REPO_ID=<votre-username>/<nom-du-repo>
DATABASE_URL=<url neon — laisser vide si non utilisé>
```

---

## Entraîner les modèles

### Option A — Pipeline principal (modèle de production)

```powershell
python main.py
```

Crée `artifacts/models/model_vX.joblib` et `artifacts/metrics/metrics_vX.json`.
Chaque exécution crée un run dans MLFlow sous l'expérience `housing_price_prediction`.

### Option B — Notebook A/B (modèles champion et challenger)

Ouvrir et exécuter `notebooks/02_train_ab_models.ipynb` en entier.

Ce notebook entraîne deux modèles :
- **Modèle A** — RandomForestRegressor (champion)
- **Modèle B** — GradientBoostingRegressor (challenger)

Les modèles sont enregistrés dans MLFlow (`housing_model_A`, `housing_model_B`)
et sauvegardés en `artifacts/models/model_v1.joblib` et `model_v2.joblib`.

---

## Workflow MLFlow

### 1. Comparer les runs dans l'UI

```powershell
mlflow ui
# Ouvrir http://127.0.0.1:5000
```

- Expérience `housing_ab_models` : runs model_A et model_B côte à côte
- Expérience `housing_price_prediction` : historique du pipeline principal
- Onglet **Models** : registre de tous les modèles versionnés

### 2. Promouvoir les modèles en Production

```powershell
python -c "
from mlflow.tracking import MlflowClient
import warnings; warnings.filterwarnings('ignore')
client = MlflowClient()
for name in ['housing_model_A', 'housing_model_B']:
    versions = client.search_model_versions(f\"name='{name}'\")
    latest = max(versions, key=lambda v: int(v.version))
    client.transition_model_version_stage(
        name, latest.version, 'Production', archive_existing_versions=True
    )
    print(f'{name} v{latest.version} => Production')
"
```

Ou depuis l'UI : onglet **Models** → choisir une version → **Stage → Transition to Production**.

### 3. Uploader vers HuggingFace Hub

```powershell
python scripts/upload_model_to_hf.py
```

Le script refuse d'uploader si aucun modèle n'est en stage Production.
Il charge automatiquement :
- `housing_model_A @ Production` → `model_v1.joblib`
- `housing_model_B @ Production` → `model_v2.joblib`
- Meilleur R² dans `housing_price_prediction` → `model_latest.joblib`

---

## Faire une prédiction depuis le frontend

1. Démarrer le backend : `uvicorn backend.app:app --reload --port 8000`
2. Démarrer le frontend : `streamlit run frontend/streamlit_app.py`
3. Ouvrir `http://localhost:8501`
4. Renseigner optionnellement un `user_id` (détermine le routage A/B)
5. Remplir les caractéristiques du logement et cliquer sur **Prédire**

---

## Faire une prédiction via l'API

### PowerShell

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

Invoke-RestMethod `
  -Uri http://localhost:8000/predict `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

### curl

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "alice",
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

### Format de réponse

```json
{
  "prediction": 2.45,
  "variant": "B",
  "model_version": "model_v2",
  "execution_mode": "ab_registry",
  "latency_ms": 38.7,
  "request_id": "3f4a1b2c-8d9e-..."
}
```

| Champ | Description |
|-------|-------------|
| `prediction` | Prix estimé (en centaines de milliers de dollars) |
| `variant` | Modèle utilisé : `A` ou `B` |
| `execution_mode` | `ab_registry` si les deux modèles sont disponibles, `legacy_fallback` sinon |
| `latency_ms` | Temps de traitement côté serveur en millisecondes |
| `request_id` | UUID unique de la requête pour le traçage |

> **Routage A/B** : le champ `user_id` est optionnel (défaut : `"anonymous"`).
> Le routage est déterministe — le même `user_id` retourne toujours la même variante.

---

## Déploiement en production sur Render.com

### Architecture de production

```
Utilisateur
    │
    ▼
Frontend Streamlit (Render, port 8501)
    │  HTTP
    ▼
Backend FastAPI (Render, port 8000)
    │  HTTPS
    ▼
HuggingFace Hub (stockage des modèles .joblib)
```

### Prérequis avant le premier déploiement

| Ressource | Où la créer |
|-----------|-------------|
| Repo HF avec les 3 fichiers `.joblib` | huggingface.co → New Model |
| Token HF avec permission write | huggingface.co/settings/tokens |
| Service backend Render (Docker ou Python) | dashboard.render.com → New → Web Service |
| Service frontend Render | dashboard.render.com → New → Web Service |

### Variables à définir dans le service **backend** Render

| Variable | Valeur |
|----------|--------|
| `HF_TOKEN` | Token HuggingFace (secret) |
| `HF_REPO_ID` | `<username>/<repo>` |
| `MODEL_OBJECT_NAME` | `model_latest.joblib` |
| `MODEL_A_OBJECT_NAME` | `model_v1.joblib` |
| `MODEL_B_OBJECT_NAME` | `model_v2.joblib` |
| `AB_TRAFFIC_B_PERCENT` | `50` |
| `DATABASE_URL` | URL PostgreSQL Neon (optionnel) |

### Variable à définir dans le service **frontend** Render

| Variable | Valeur |
|----------|--------|
| `BACKEND_URL` | URL du backend (ex : `https://votre-backend.onrender.com`) |

> Le guide complet pas à pas est disponible dans `Docs/Guide_Deploiement_Render.docx`

---

## Tests et qualité

```powershell
pytest -v --cov=src --cov=backend     # tests et couverture
ruff check .                           # lint PEP8
ruff format --check .                  # format
bandit -r src/ backend/                # sécurité
```

Le hook `pre-push` lance ces vérifications automatiquement à chaque push :

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install_git_hook.ps1
```

---

## Analyse des logs A/B

Les prédictions en production sont loguées dans PostgreSQL (si `DATABASE_URL` est défini)
ou en local dans `logs/ab_predictions.jsonl`.

Pour analyser les résultats, exécuter `notebooks/03_ab_analysis.ipynb`.
Le notebook lit automatiquement PostgreSQL si `DATABASE_URL` est défini, sinon le fichier JSONL.

---

## Pannes courantes

| Symptôme | Cause probable | Solution |
|----------|----------------|----------|
| `execution_mode: legacy_fallback` | `model_v1.joblib` ou `model_v2.joblib` absent sur HF Hub | Relancer `upload_model_to_hf.py` après promotion MLFlow |
| Erreur 500 sur `/predict` | Modèle non chargé | Vérifier les logs backend et la présence des `.joblib` sur HF Hub |
| Erreur 422 sur `/predict` | Champ manquant ou type incorrect | Vérifier le format JSON de la requête |
| `RuntimeError: Aucune version en Production` | Modèle non promu dans MLFlow | Lancer l'étape de promotion (voir Workflow MLFlow) |
| Backend Render : 502 au démarrage | Cold start (plan Free) | Attendre 30-60 secondes et réessayer |
| Frontend ne joint pas le backend | `BACKEND_URL` incorrect | Vérifier l'URL sans slash final dans les variables Render |

---

## Maintenance recommandée

- Exécuter `pytest`, `ruff` et `bandit` avant toute livraison
- Consulter `mlflow ui` pour comparer les métriques avant tout upload
- Ne jamais bypasser la promotion MLFlow pour uploader directement un `.joblib`
- Mettre à jour `requirements.txt` avec `pip freeze > requirements.txt`
  puis nettoyer les lignes `-e git+...` générées automatiquement
