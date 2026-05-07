[![CI - Python Quality Checks](https://github.com/rahiming/ml-housting-project/actions/workflows/ci.yml/badge.svg)](https://github.com/rahiming/ml-housting-project/actions/workflows/ci.yml)

# ML Housing Project

A machine learning project for housing price prediction.

## 🎯 Présentation du Projet

Ce projet implémente une solution complète de prédiction des prix immobiliers (basée sur le dataset California Housing). L'objectif est de démontrer une approche **MLOps** robuste en séparant clairement le cycle de vie de l'entraînement de celui de l'inférence.

**Points clés :**
- **Modularité** : Séparation stricte entre le code d'entraînement (`src/training`) et de prédiction (`src/prediction`).
- **API de Production** : Backend performant avec FastAPI.
- **Interface Utilisateur** : Frontend intuitif avec Streamlit.
- **CI/CD Moderne** : Pipeline GitHub Actions incluant linting, tests, sécurité (Bandit) et validation Docker.

## 🏗️ Project Structure

```
ml-housing-project/
├── src/
│   ├── training/         # Pipeline d'entraînement (Dev uniquement)
│   │   ├── train.py
│   │   ├── evaluate.py
│   │   ├── data.py
│   │   ├── preprocessing.py
│   │   └── pipeline.py
│   ├── common/           # Utilitaires partagés (Production - OUI)
│   │   └── features.py   # Logique de transformation commune
│   ├── prediction/       # Logique de prédiction (Production - OUI)
│   │   ├── predict.py
│   │   ├── schemas.py
│   │   └── model_loader.py
├── tests/
│   ├── __init__.py
│   ├── test_data.py
│   ├── test_features.py
│   └── test_pipeline.py
├── artifacts/
│   └── .gitkeep
├── requirements.txt
├── pyproject.toml
├── README.md
└── main.py
```

## ⚙️ Installation

1. **Préparer l'environnement** :
```bash
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate sur Windows
```

2. **Installer les dépendances** :
```bash
pip install -r requirements.txt
pip install -e ".[dev]"
```

## Usage

Run the ML pipeline:

```bash
python main.py
```

## Testing

Run tests with pytest:

```bash
pytest
```

## Local environment variables

The repo does not version secrets. For local development, copy `.env.example` to `.env`
and adjust the values if needed.

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Unit tests skip the MinIO startup path through `tests/conftest.py`, so they do not need
a real MinIO service or private environment variables.
