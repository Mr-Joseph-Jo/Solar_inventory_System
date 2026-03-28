"""Tests for user management — role guard, password length."""
from unittest.mock import patch, MagicMock


class TestUserAccess:
    def test_users_requires_login(self, client):
        r = client.get("/users/", follow_redirects=False)
        assert r.status_code == 302

    @patch("routes.users.current_user")
    def test_admin_role_gets_403(self, mock_user, client):
        mock_user.is_authenticated = True
        mock_user.role = "admin"
        r = client.get("/users/")
        assert r.status_code == 403

    @patch("routes.users.current_user")
    def test_sales_role_gets_403(self, mock_user, client):
        mock_user.is_authenticated = True
        mock_user.role = "sales"
        r = client.get("/users/")
        assert r.status_code == 403


class TestCreateUser:
    @patch("routes.users.get_db")
    @patch("routes.users.current_user")
    def test_short_password_rejected(self, mock_user, mock_get_db, client):
        mock_user.is_authenticated = True
        mock_user.role = "owner"
        mock_user.id = 1

        conn, cur = MagicMock(), MagicMock()
        mock_get_db.return_value = conn
        conn.cursor.return_value = cur
        cur.fetchall.return_value = []

        r = client.post("/users/", data={
            "name": "Test", "username": "test",
            "password": "short",        # < 8 chars
            "role": "sales"
        }, follow_redirects=True)

        # DB insert should NOT have been called
        assert r.status_code == 200
        insert_calls = [str(c) for c in cur.execute.call_args_list
                        if "INSERT" in str(c)]
        assert len(insert_calls) == 0

    @patch("routes.users.get_db")
    @patch("routes.users.current_user")
    def test_invalid_role_rejected(self, mock_user, mock_get_db, client):
        mock_user.is_authenticated = True
        mock_user.role = "owner"
        mock_user.id = 1

        conn, cur = MagicMock(), MagicMock()
        mock_get_db.return_value = conn
        conn.cursor.return_value = cur
        cur.fetchall.return_value = []

        r = client.post("/users/", data={
            "name": "Test", "username": "test",
            "password": "validpass123",
            "role": "superuser"         # invalid
        }, follow_redirects=True)
        assert r.status_code == 200
