# Étape 1 : Construction des dépendances
FROM python:3.10-slim as builder

WORKDIR /build

# Installation des outils nécessaires à la compilation de certaines librairies (ex: pandas/scikit-learn)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Installation des dépendances dans un dossier isolé /install
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Étape 2 : Image finale de production (légère)
FROM python:3.10-slim

WORKDIR /app

# On récupère uniquement les dépendances installées à l'étape précédente
COPY --from=builder /install /usr/local

# On ne copie que ce qui est utile pour l'inférence
COPY src/common/ ./src/common/
COPY src/prediction/ ./src/prediction/
COPY backend/ ./backend/
COPY artifacts/ ./artifacts/

# Configuration pour que Python trouve le module 'src' correctement
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]