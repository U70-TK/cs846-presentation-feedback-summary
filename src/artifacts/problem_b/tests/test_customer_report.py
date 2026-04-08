import os
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app
from customer_report import build_customer_summary


def test_build_customer_summary_calls_store_helpers(monkeypatch):
    calls = {"get_customer": 0, "list_invoices_for_customer": 0}

    def fake_get_customer(customer_id):
        calls["get_customer"] += 1
        return {"id": customer_id, "name": "Acme Co"}

    def fake_list_invoices_for_customer(customer_id):
        calls["list_invoices_for_customer"] += 1
        return [
            {"id": 1, "status": "open", "total_cents": 2000, "created_at": "a"},
            {"id": 2, "status": "paid", "total_cents": 5000, "created_at": "b"},
        ]

    monkeypatch.setattr("customer_report.get_customer", fake_get_customer)
    monkeypatch.setattr(
        "customer_report.list_invoices_for_customer",
        fake_list_invoices_for_customer,
    )

    summary = build_customer_summary(1)

    assert calls["get_customer"] == 1
    assert calls["list_invoices_for_customer"] == 1
    assert summary["customer_id"] == 1


def test_build_customer_summary_returns_expected_top_level_keys():
    summary = build_customer_summary(1)

    assert set(summary.keys()) == {
        "customer_id",
        "name",
        "open_invoice_total_cents",
        "recent_invoice_ids",
        "has_overdue_invoice",
    }
    assert summary["customer_id"] == 1
    assert summary["name"] == "Acme Co"


def test_summary_endpoint_returns_200_with_expected_shape():
    client = TestClient(app)

    response = client.get(
        "/customers/1/summary",
        headers={"Authorization": "Bearer demo-token"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "customer_id" in body
    assert "name" in body
    assert "open_invoice_total_cents" in body
    assert "recent_invoice_ids" in body
    assert "has_overdue_invoice" in body
