import logging
import os
import random

import requests
import streamlit as st

# L'interface utilisateur peut aussi produire des logs Python lisibles dans
# Docker. Cela facilite le diagnostic d'un echec de requete ou d'un mauvais
# parametrage du frontend.
logger = logging.getLogger(__name__)

# Le frontend pointe par defaut vers un backend local, mais cette URL peut etre
# surchargee dans Docker Compose ou dans un shell local.
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
PREDICT_URL = f"{BACKEND_URL}/predict"

logger.info("Demarrage de Streamlit. BACKEND_URL=%s", BACKEND_URL)


def build_payload(
    user_id: str,
    median_income: float,
    housing_median_age: float,
    average_rooms: float,
    average_bedrooms: float,
    population: float,
    average_occupancy: float,
    latitude: float,
    longitude: float,
) -> dict:
    """Build the request body expected by the public FastAPI schema."""
    return {
        "user_id": user_id,
        "median_income": median_income,
        "housing_median_age": housing_median_age,
        "average_rooms": average_rooms,
        "average_bedrooms": average_bedrooms,
        "population": population,
        "average_occupancy": average_occupancy,
        "latitude": latitude,
        "longitude": longitude,
    }


st.title("A/B Testing - Prediction immobiliere")
st.write(
    "Cette interface envoie des donnees brutes a l'API. "
    "Le backend choisit le modele A ou B."
)

st.header("1. Identifiant utilisateur")
user_id = st.text_input("user_id", value="alice")

st.header("2. Caracteristiques du logement")
col1, col2 = st.columns(2)

with col1:
    median_income = st.number_input("median_income - revenu median", value=3.5)
    housing_median_age = st.number_input(
        "housing_median_age - age du logement",
        value=20.0,
    )
    average_rooms = st.number_input(
        "average_rooms - nombre moyen de pieces",
        value=5.0,
    )
    average_bedrooms = st.number_input(
        "average_bedrooms - nombre moyen de chambres",
        value=1.0,
    )

with col2:
    population = st.number_input("population", value=1000.0)
    average_occupancy = st.number_input(
        "average_occupancy - occupation moyenne",
        value=3.0,
    )
    latitude = st.number_input("latitude", value=34.0)
    longitude = st.number_input("longitude", value=-118.0)

payload = build_payload(
    user_id=user_id,
    median_income=median_income,
    housing_median_age=housing_median_age,
    average_rooms=average_rooms,
    average_bedrooms=average_bedrooms,
    population=population,
    average_occupancy=average_occupancy,
    latitude=latitude,
    longitude=longitude,
)

if st.button("Predire", type="primary"):
    logger.info("Soumission du formulaire de prediction pour user_id=%s.", user_id)
    try:
        logger.info("Envoi de la requete HTTP de prediction vers %s", PREDICT_URL)
        response = requests.post(PREDICT_URL, json=payload, timeout=20)
        response.raise_for_status()
        result = response.json()
        logger.info(
            "Prediction recue. request_id=%s variant=%s model_version=%s",
            result.get("request_id"),
            result.get("variant"),
            result.get("model_version"),
        )

        st.subheader("Resultat")
        st.metric("Prediction", round(result["prediction"], 3))
        st.write("Variante utilisee :", result["variant"])
        st.write("Version modele :", result["model_version"])
        st.write("Mode d'execution :", result["execution_mode"])
        st.write("Latence :", result["latency_ms"], "ms")
        st.write("request_id :", result["request_id"])
    except requests.exceptions.ConnectionError:
        logger.exception("Connexion impossible entre le frontend et le backend.")
        st.error("Erreur : impossible de contacter le serveur backend FastAPI.")
    except Exception as exc:
        logger.exception("Erreur inattendue lors de la prediction.")
        st.error(f"Une erreur est survenue : {exc}")

st.header("3. Generer du trafic de test")
if st.button("Simuler 100 utilisateurs"):
    success = 0
    variant_counts = {"A": 0, "B": 0}
    # Le but ici est uniquement de produire du trafic de demonstration pour
    # l'A/B testing, pas de generer des secrets ou des jetons de securite.
    rng = random.Random()  # nosec B311 # noqa: S311

    for i in range(100):
        simulated_payload = build_payload(
            user_id=f"user_{i}",
            median_income=round(rng.uniform(1.0, 8.0), 2),  # noqa: S311
            housing_median_age=float(rng.randint(1, 50)),  # noqa: S311
            average_rooms=round(rng.uniform(2.0, 8.0), 2),  # noqa: S311
            average_bedrooms=round(rng.uniform(1.0, 3.0), 2),  # noqa: S311
            population=float(rng.randint(200, 5000)),  # noqa: S311
            average_occupancy=round(rng.uniform(1.0, 6.0), 2),  # noqa: S311
            latitude=round(rng.uniform(32.0, 42.0), 2),  # noqa: S311
            longitude=round(rng.uniform(-124.0, -114.0), 2),  # noqa: S311
        )
        try:
            response = requests.post(PREDICT_URL, json=simulated_payload, timeout=20)
            response.raise_for_status()
            result = response.json()
            success += 1
            variant_counts[result["variant"]] = (
                variant_counts.get(result["variant"], 0) + 1
            )
        except Exception as exc:
            logger.warning("Echec d'une requete de trafic de test : %s", exc)

    st.success(f"{success} requetes envoyees avec succes")
    st.write("Repartition observee :", variant_counts)
