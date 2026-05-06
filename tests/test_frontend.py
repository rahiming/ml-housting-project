from unittest.mock import MagicMock, patch

from streamlit.testing.v1 import AppTest


def test_streamlit_app_loads():
    """Vérifie que l'application Streamlit se lance sans erreur."""
    at = AppTest.from_file("frontend/streamlit_app.py").run(timeout=15)
    assert not at.exception
    assert "Prédiction du prix immobilier" in at.title[0].value


@patch("requests.post")
def test_streamlit_prediction_flow(mock_post):
    """Vérifie que le clic sur le bouton affiche le résultat de l'API."""
    # Mock d'une réponse réussie de FastAPI
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"prediction": 4.12}
    mock_post.return_value = mock_response

    at = AppTest.from_file("frontend/streamlit_app.py").run(timeout=15)

    # On simule le clic sur le bouton "Calculer l'estimation"
    # (index 0 car c'est le seul bouton type primary)
    at.button[0].click().run()

    # On vérifie qu'un message de succès contenant la valeur prédite est affiché
    success_messages = [s.value for s in at.success]
    assert any("4.12" in msg for msg in success_messages)
    assert not at.exception
