# Manuel d'utilisation

## Public vise

Ce manuel est destine a un utilisateur qui doit :

- installer et demarrer l'application en local
- entrainer un modele et le publier
- lancer des predictions (frontend ou API)
- deployer l'application en production sur Render.com
- comprendre les incidents les plus frequents

---

## Vue d'ensemble

L'application estime un prix immobilier a partir de caracteristiques de quartier.
Elle embarque un mecanisme d'experimentation A/B : chaque requete est routee
de facon deterministe vers le modele A ou B selon l'identifiant utilisateur.

Cycle normal d'utilisation :

1. entrainer ou recuperer les modeles
2. stocker les modeles dans MinIO (local) ou Cloudflare R2 (production)
3. demarrer le backend FastAPI et le frontend Streamlit
4. utiliser l'interface ou l'API `/predict`

---

## Installation locale pas a pas

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

---

## Utilisation avec Docker Compose (local)

### Demarrer

```powershell
docker compose up -d --build
```

### Verifier l'etat

```powershell
docker compose ps
```

Services attendus : `backend`, `frontend`, `minio`

### Ouvrir les interfaces

| Interface | URL |
|-----------|-----|
| Frontend Streamlit | `http://localhost:8501` |
| API (documentation) | `http://localhost:8000/docs` |
| MinIO (console) | `http://localhost:9001` |

### Arreter

```powershell
docker compose down          # arret simple
docker compose down -v       # arret + suppression des volumes
```

---

## Entrainer un modele

```powershell
python main.py
```

Sorties attendues :

- `artifacts/models/model_vX.joblib`
- `artifacts/models/model_latest.joblib`
- `artifacts/metrics/metrics_vX.json`

## Publier le modele dans MinIO (local)

```powershell
python scripts/upload_model_to_minio.py
```

Les trois fichiers `model_latest.joblib`, `model_v1.joblib` et `model_v2.joblib`
doivent etre presents dans le bucket `ml-models` pour activer le mode A/B complet.

---

## Faire une prediction depuis le frontend

1. Ouvrir `http://localhost:8501` (local) ou l'URL Render (production)
2. Renseigner optionnellement un `user_id` (determine le routage A/B)
3. Remplir les caracteristiques du logement
4. Cliquer sur **Predire**
5. Lire le resultat : prediction, variante utilisee (A ou B), version du modele

---

## Faire une prediction via l'API

### PowerShell (local)

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

### curl (production ou local)

```bash
curl -X POST https://ml-housing-backend.onrender.com/predict \
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

### Format de reponse

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
| `prediction` | Prix estime (en centaines de milliers de dollars) |
| `variant` | Modele utilise : `A` ou `B` |
| `model_version` | Identifiant interne du modele (`model_v1`, `model_v2`, `legacy_single_model`) |
| `execution_mode` | `ab_registry` si les deux modeles sont disponibles, `legacy_fallback` sinon |
| `latency_ms` | Temps de traitement cote serveur en millisecondes |
| `request_id` | UUID unique de la requete pour le traçage |

> **Routage A/B** : le champ `user_id` est optionnel (defaut : `"anonymous"`).
> Le routage est deterministe — le meme `user_id` retourne toujours la meme variante.
> Avec 50 % de trafic vers B : `"alice"` → B, `"anonymous"` → A.

---

## Deploiement en production sur Render.com

### Architecture de production

```
Utilisateur
    │
    ▼
Frontend Streamlit (Render, port 8501)
    │  HTTP
    ▼
Backend FastAPI (Render, port 8000)
    │  S3 API
    ▼
Cloudflare R2 (stockage des modeles .joblib)
```

### Prerequis avant le premier deploiement

| Ressource | Ou la creer |
|-----------|-------------|
| Bucket R2 `ml-models` avec les 3 fichiers `.joblib` | dash.cloudflare.com → R2 |
| Registry Credential GHCR dans Render | dashboard.render.com → Account Settings → Registry Credentials |
| Service backend Render (image `ghcr.io/.../backend:latest`, port 8000) | dashboard.render.com → New → Web Service |
| Service frontend Render (image `ghcr.io/.../frontend:latest`, port 8501) | dashboard.render.com → New → Web Service |
| Cle API Render | dashboard.render.com → Account Settings → API Keys |

Variables d'environnement a definir dans le service **backend** Render :

| Variable | Valeur |
|----------|--------|
| `MINIO_ENDPOINT` | `https://<account_id>.r2.cloudflarestorage.com` |
| `MINIO_BUCKET_MODELS` | `ml-models` |
| `MODEL_OBJECT_NAME` | `model_latest.joblib` |
| `MODEL_A_OBJECT_NAME` | `model_v1.joblib` |
| `MODEL_B_OBJECT_NAME` | `model_v2.joblib` |
| `AB_TRAFFIC_B_PERCENT` | `50` |
| `MINIO_ACCESS_KEY` | *(secret — cle R2)* |
| `MINIO_SECRET_KEY` | *(secret — cle R2)* |

Variable d'environnement a definir dans le service **frontend** Render :

| Variable | Valeur |
|----------|--------|
| `BACKEND_URL` | `https://ml-housing-backend.onrender.com` |

Secrets et variables a configurer dans **GitHub**
(Settings → Secrets and variables → Actions) :

| Type | Nom | Valeur |
|------|-----|--------|
| Secret | `RENDER_API_KEY` | Cle API Render |
| Secret | `MINIO_ACCESS_KEY` | Access Key ID Cloudflare R2 |
| Secret | `MINIO_SECRET_KEY` | Secret Access Key Cloudflare R2 |
| Variable | `RENDER_BACKEND_SERVICE_ID` | `srv-xxxx` (Settings du service Render) |
| Variable | `RENDER_FRONTEND_SERVICE_ID` | `srv-yyyy` |

> Le guide complet pas a pas est disponible dans `Guide_Deploiement_Render.docx`
> a la racine du projet.

### Lancer un deploiement en production

Le deploiement est **manuel** et ne peut s'effectuer que depuis la branche `main`.

1. Merger `develop` dans `main` via une Pull Request
2. Sur GitHub, aller dans **Actions → Production Deploy → Run workflow**
3. Verifier que la branche selectionnee est `main`
4. Cliquer sur **Run workflow**

Le workflow execute deux jobs :

| Job | Duree estimee | Ce qu'il fait |
|-----|---------------|---------------|
| `publish-images` | 5-10 min | Build et push des images Docker vers GHCR |
| `deploy-render` | 3-15 min | Deploiement via l'API Render + attente du statut `live` |

A la fin, l'onglet **Summary** du run affiche les URLs de production.

---

## Verification rapide

### Sante du backend

```powershell
# Local
Invoke-RestMethod -Uri http://localhost:8000/health

# Production
Invoke-RestMethod -Uri https://ml-housing-backend.onrender.com/health
```

Reponse attendue : `{ "status": "ok" }`

### Logs

```powershell
# Local
docker compose logs -f backend
docker compose logs -f frontend

# Production : onglet Logs de chaque service dans dashboard.render.com
```

### Verification du modele dans MinIO (local)

1. Ouvrir `http://localhost:9001`
2. Se connecter avec `admin / password123`
3. Ouvrir le bucket `ml-models`
4. Verifier la presence de `model_latest.joblib`, `model_v1.joblib`, `model_v2.joblib`

---

## Commandes utiles (local)

```powershell
# Relancer un service specifique
docker compose up -d --build backend
docker compose up -d --build frontend

# Relancer apres mise a jour du modele
python scripts/upload_model_to_minio.py
docker compose restart backend

# Tests et qualite
pytest -v --cov=src --cov=backend
ruff check .
ruff format --check .
black --check .
bandit -r src/ backend/
```

---

## Pannes courantes

### Le backend ne demarre pas (local)

Verifier :
- les variables `MINIO_*` dans `.env`
- que MinIO est bien demarre (`docker compose ps`)
- que les fichiers `.joblib` sont presents dans le bucket `ml-models`

### Le backend ne demarre pas (production Render)

Verifier dans les logs Render :
- `MINIO_ENDPOINT` : format exact `https://<account_id>.r2.cloudflarestorage.com`
- `MINIO_ACCESS_KEY` et `MINIO_SECRET_KEY` : valeurs copiees depuis Cloudflare R2
- Presence de `model_latest.joblib` dans le bucket R2

### Le frontend ne joint pas le backend

Local : verifier `BACKEND_URL`, le port `8000` et `docker compose ps`

Production : verifier que `BACKEND_URL` dans le service frontend Render
contient bien l'URL exacte du backend (sans slash final).
Si le backend est sur le plan Free, il peut etre en veille — attendre 60 s.

### Les predictions retournent `legacy_fallback`

Le mode `legacy_fallback` s'active quand les modeles A/B ne sont pas trouves.
Verifier que `model_v1.joblib` et `model_v2.joblib` sont presents dans le stockage
et que `MODEL_A_OBJECT_NAME` / `MODEL_B_OBJECT_NAME` sont definis.

### Le deploiement CI/CD echoue

| Erreur | Cause probable |
|--------|----------------|
| 401 sur l'API Render | `RENDER_API_KEY` expire ou incorrect |
| 404 sur l'API Render | `RENDER_BACKEND_SERVICE_ID` ou `RENDER_FRONTEND_SERVICE_ID` incorrect |
| `build_failed` dans Render | Image GHCR inaccessible — verifier le Registry Credential |
| Timeout de polling | Build Render trop long — relancer le workflow |

---

## Maintenance recommandee

- Executer `pytest`, `ruff`, `black` et `bandit` avant toute livraison
- Lire les logs du backend apres tout redeploiement
- Documenter toute evolution du schema d'entree dans `src/prediction/schemas.py`
- Mettre a jour `requirements.txt` via `pip freeze > requirements.txt`
  puis supprimer les lignes `-e git+...` generees automatiquement
