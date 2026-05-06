FROM python:3.10-slim

WORKDIR /app

# Installation des dépendances minimales
COPY frontend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie uniquement du dossier frontend
COPY frontend/ ./frontend/

EXPOSE 8501

ENV PYTHONUNBUFFERED=1

# Commande pour lancer Streamlit
CMD ["streamlit", "run", "frontend/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]