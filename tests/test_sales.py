"""Tests for sales route — stock check, invoice number format."""
import re
from routes.sales import generate_invoice_no


class TestGenerateInvoiceNo:
    def test_format(self):
        no = generate_invoice_no()
        assert no.startswith("SOL-")
        assert len(no) == 16          # SOL- + 12 hex chars

    def test_uniqueness(self):
        nos = {generate_invoice_no() for _ in range(100)}
        assert len(nos) == 100        # all 100 must be unique


class TestSaleValidation:
    def test_sale_requires_login(self, client):
        r = client.get("/sales/", follow_redirects=False)
        assert r.status_code == 302
