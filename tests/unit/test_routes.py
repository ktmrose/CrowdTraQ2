import pytest
from flask import Flask
from unittest.mock import patch
from app.routes.routes import register_routes, spotify_bp

@pytest.fixture
def app():
    app = Flask(__name__)
    register_routes(app)
    return app

def test_register_routes_adds_blueprint(app):
    assert 'spotify' in app.blueprints
    assert app.blueprints['spotify'] is spotify_bp

def test_callback_missing_code(app):
    client = app.test_client()
    response = client.get("/callback")  # no ?code= param
    assert response.status_code == 400
    assert b"Missing authorization code" in response.data

@patch("app.routes.routes.SpotifyConnectionManager")
def test_callback_with_code_calls_exchange(mock_mgr, app):
    mock_instance = mock_mgr.get_instance.return_value
    client = app.test_client()

    response = client.get("/callback?code=fakecode")

    # Ensure the SpotifyConnectionManager was used
    mock_instance.exchange_code_for_token.assert_called_once_with("fakecode")

    # Response should be success
    assert response.status_code == 200
    assert b"Authorization successful" in response.data
    # Header injection should be present
    assert response.headers["Connection"] == "close"