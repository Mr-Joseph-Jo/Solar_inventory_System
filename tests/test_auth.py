"""Tests for login / logout routes."""
from unittest.mock import patch, MagicMock
from werkzeug.security import generate_password_hash


def _mock_user(username="admin", role="owner", active=1):
    return {
        "id": 1,
        "username": username,
        "password_hash": generate_password_hash("password123"),
        "role": role,
        "active": active,
    }


class TestLogin:
    def test_login_page_loads(self, client):
        r = client.get("/")
        assert r.status_code == 200
        assert b"Solar Inventory" in r.data

    @patch("routes.auth.get_db")
    def test_valid_login_redirects_to_dashboard(self, mock_get_db, client):
        conn, cur = MagicMock(), MagicMock()
        mock_get_db.return_value = conn
        conn.cursor.return_value = cur
        cur.fetchone.return_value = _mock_user()

        r = client.post("/", data={"username": "admin", "password": "password123"},
                        follow_redirects=False)
        assert r.status_code == 302
        assert "/dashboard" in r.headers["Location"]

    @patch("routes.auth.get_db")
    def test_wrong_password_shows_error(self, mock_get_db, client):
        conn, cur = MagicMock(), MagicMock()
        mock_get_db.return_value = conn
        conn.cursor.return_value = cur
        cur.fetchone.return_value = _mock_user()

        r = client.post("/", data={"username": "admin", "password": "wrongpass"},
                        follow_redirects=True)
        assert r.status_code == 200
        assert b"Invalid" in r.data

    @patch("routes.auth.get_db")
    def test_unknown_user_shows_error(self, mock_get_db, client):
        conn, cur = MagicMock(), MagicMock()
        mock_get_db.return_value = conn
        conn.cursor.return_value = cur
        cur.fetchone.return_value = None   # user not found

        r = client.post("/", data={"username": "ghost", "password": "x"},
                        follow_redirects=True)
        assert b"Invalid" in r.data


class TestLogout:
    @patch("routes.auth.get_db")
    def test_logout_redirects_to_login(self, mock_get_db, logged_in_client):
        conn, cur = MagicMock(), MagicMock()
        mock_get_db.return_value = conn
        conn.cursor.return_value = cur

        r = logged_in_client.get("/logout", follow_redirects=False)
        assert r.status_code == 302
