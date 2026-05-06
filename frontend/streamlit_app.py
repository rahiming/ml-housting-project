import requests
import streamlit as st

st.title("Prédiction du prix immobilier")
st.write("Saisissez les caractéristiques du quartier pour obtenir une estimation.")

# Organisation en colonnes pour une meilleure interface
col1, col2 = st.columns(2)

with col1:
    med_inc = st.number_input("Revenu médian (en 10k$)", value=3.5, step=0.1)
    house_age = st.number_input("Âge médian des maisons", value=20.0, step=1.0)
    ave_rooms = st.number_input("Nombre moyen de pièces", value=5.0, step=0.1)
    ave_bedrms = st.number_input("Nombre moyen de chambres", value=1.0, step=0.1)

with col2:
    population = st.number_input("Population du quartier", value=1000.0, step=50.0)
    ave_occup = st.number_input("Occupation moyenne", value=3.0, step=0.1)
    latitude = st.number_input("Latitude", value=34.0, format="%.2f")
    longitude = st.number_input("Longitude", value=-118.0, format="%.2f")

if st.button("Calculer l'estimation", type="primary"):
    payload = {
        "MedInc": med_inc,
        "HouseAge": house_age,
        "AveRooms": ave_rooms,
        "AveBedrms": ave_bedrms,
        "Population": population,
        "AveOccup": ave_occup,
        "Latitude": latitude,
        "Longitude": longitude,
    }
    try:
        response = requests.post(
            "http://127.0.0.1:8000/predict", json=payload, timeout=5
        )
        response.raise_for_status()
        prediction = response.json()["prediction"]

        st.success(f"### Prix estimé : {prediction:.2f} $100k")
        st.metric("Estimation", f"{prediction * 100_000:,.0f} $")
    except requests.exceptions.ConnectionError:
        st.error("Erreur : Impossible de contacter le serveur backend (FastAPI).")
    except Exception as e:
        st.error(f"Une erreur est survenue : {e}")
