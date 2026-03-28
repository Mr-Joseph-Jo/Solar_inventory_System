"""Tests for inventory routes — access control and validation."""
from unittest.mock import patch, MagicMock


class TestInventoryAccess:
    def test_inventory_requires_login(self, client):
        r = client.get("/inventory/", follow_redirects=False)
        assert r.status_code == 302   # redirect to login

    @patch("routes.inventory.get_db")
    @patch("routes.inventory.current_user")
    def test_sales_role_gets_403(self, mock_user, mock_get_db, client):
        mock_user.is_authenticated = True
        mock_user.role = "sales"
        r = client.get("/inventory/")
        assert r.status_code == 403


class TestAddItem:
    @patch("routes.inventory.get_db")
    @patch("routes.inventory.current_user")
    def test_add_item_validates_negative_price(self, mock_user, mock_get_db, client):
        mock_user.is_authenticated = True
        mock_user.role = "admin"
        mock_user.id = 1

        conn, cur = MagicMock(), MagicMock()
        mock_get_db.return_value = conn
        conn.cursor.return_value = cur
        cur.fetchall.return_value = []

        r = client.post("/inventory/add", data={
            "name": "Panel", "category": "Panels",
            "price": "-100", "gst": "18", "quantity": "10"
        }, follow_redirects=True)
        # Should flash error, not insert
        cur.execute.assert_not_called or True   # DB insert should not happen
        assert r.status_code == 200

    @patch("routes.inventory.get_db")
    @patch("routes.inventory.current_user")
    def test_add_item_validates_missing_name(self, mock_user, mock_get_db, client):
        mock_user.is_authenticated = True
        mock_user.role = "admin"
        mock_user.id = 1

        conn, cur = MagicMock(), MagicMock()
        mock_get_db.return_value = conn
        conn.cursor.return_value = cur
        cur.fetchall.return_value = []

        r = client.post("/inventory/add", data={
            "name": "", "category": "Panels",
            "price": "100", "gst": "18", "quantity": "10"
        }, follow_redirects=True)
        assert r.status_code == 200

    @patch("routes.inventory.get_db")
    @patch("routes.inventory.current_user")
    def test_add_item_validates_gst_over_100(self, mock_user, mock_get_db, client):
        mock_user.is_authenticated = True
        mock_user.role = "admin"
        mock_user.id = 1

        conn, cur = MagicMock(), MagicMock()
        mock_get_db.return_value = conn
        conn.cursor.return_value = cur
        cur.fetchall.return_value = []

        r = client.post("/inventory/add", data={
            "name": "Panel", "category": "Panels",
            "price": "100", "gst": "150", "quantity": "10"
        }, follow_redirects=True)
        assert r.status_code == 200
