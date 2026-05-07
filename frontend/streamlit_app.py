import logging
import os

import requests
import streamlit as st

# L'interface utilisateur peut aussi produire des logs Python lisibles dans
# Docker. Cela facilite le diagnostic d'un echec de requete ou d'un mauvais
# parametrage du frontend.
logger = logging.getLogger(__name__)

# Le frontend pointe par defaut vers un backend local, mais cette URL peut etre
# surchargee dans Docker Compose ou dans un shell local.
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

logger.info("Demarrage de Streamlit. BACKEND_URL=%s", BACKEND_URL)

st.title("Prédiction du prix immobilier")
st.write("Saisissez les caracteristiques du quartier pour obtenir une estimation.")

# La mise en page en deux colonnes evite un formulaire trop vertical.
col1, col2 = st.columns(2)

with col1:
    med_inc = st.number_input("Revenu median (en 10k$)", value=3.5, step=0.1)
    house_age = st.number_input("Age median des maisons", value=20.0, step=1.0)
    ave_rooms = st.number_input("Nombre moyen de pieces", value=5.0, step=0.1)
    ave_bedrms = st.number_input("Nombre moyen de chambres", value=1.0, step=0.1)

with col2:
    population = st.number_input("Population du quartier", value=1000.0, step=50.0)
    ave_occup = st.number_input("Occupation moyenne", value=3.0, step=0.1)
    latitude = st.number_input("Latitude", value=34.0, format="%.2f")
    longitude = st.number_input("Longitude", value=-118.0, format="%.2f")

if st.button("Calculer l'estimation", type="primary"):
    logger.info("Soumission du formulaire de prediction par l'utilisateur.")

    # Le payload reprend exactement le schema public de l'API FastAPI.
    payload = {
        "median_income": med_inc,
        "housing_median_age": house_age,
        "average_rooms": ave_rooms,
        "average_bedrooms": ave_bedrms,
        "population": population,
        "average_occupancy": ave_occup,
        "latitude": latitude,
        "longitude": longitude,
    }

    try:
        logger.info(
            "Envoi de la requete HTTP de prediction vers %s/predict",
            BACKEND_URL,
        )
        response = requests.post(f"{BACKEND_URL}/predict", json=payload, timeout=20)
        response.raise_for_status()
        prediction = response.json()["prediction"]
        logger.info("Prediction recue depuis le backend : %s", prediction)

        st.success(f"### Prix estime : {prediction:.2f} $100k")
        st.metric("Estimation", f"{prediction * 100_000:,.0f} $")
    except requests.exceptions.ConnectionError:
        logger.exception("Connexion impossible entre le frontend et le backend.")
        st.error("Erreur : impossible de contacter le serveur backend FastAPI.")
    except Exception as exc:
        logger.exception("Erreur inattendue lors de la prediction.")
        st.error(f"Une erreur est survenue : {exc}")
