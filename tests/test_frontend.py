from unittest.mock import MagicMock, patch

from streamlit.testing.v1 import AppTest


def test_streamlit_app_loads():
    """Verifie que l'application Streamlit se lance sans erreur."""
    at = AppTest.from_file("frontend/streamlit_app.py").run(timeout=15)
    assert not at.exception
    assert "A/B Testing - Prediction immobiliere" in at.title[0].value


@patch("requests.post")
def test_streamlit_prediction_flow(mock_post):
    """Verifie que le clic sur le bouton affiche le resultat de l'API."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "prediction": 4.12,
        "variant": "B",
        "model_version": "model_v2",
        "execution_mode": "ab_registry",
        "latency_ms": 12.5,
        "request_id": "req-123",
    }
    mock_post.return_value = mock_response

    at = AppTest.from_file("frontend/streamlit_app.py").run(timeout=15)
    at.button[0].click().run()

    metric_values = [metric.value for metric in at.metric]
    text_values = [text.value for text in at.markdown] + [
        text.value for text in at.text
    ]

    assert any("4.12" in str(value) for value in metric_values)
    assert any("Variante utilisee" in text for text in text_values)
    assert any("model_v2" in text for text in text_values)
    assert not at.exception
