"""
Shared pytest fixtures.
Uses an in-memory SQLite DB so tests never touch MySQL.
"""
import pytest
from unittest.mock import patch, MagicMock
from app import app as flask_app


@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,   # disable CSRF in tests
        "SECRET_KEY": "test-secret",
    })
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mock_db():
    """Returns a mock DB connection + cursor usable in tests."""
    mock_conn   = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor


@pytest.fixture
def logged_in_client(client):
    """Client with a fake owner session already set."""
    with client.session_transaction() as sess:
        sess["_user_id"] = "1"
    return client
