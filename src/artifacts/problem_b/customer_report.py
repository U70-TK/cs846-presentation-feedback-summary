from store import get_customer, list_invoices_for_customer


def build_customer_summary(customer_id: int) -> dict:
    customer = get_customer(customer_id)
    if customer is None:
        return {
            "customer_id": customer_id,
            "name": None,
            "open_invoice_total_cents": 0,
            "recent_invoice_ids": [],
            "has_overdue_invoice": False,
        }

    invoices = list_invoices_for_customer(customer_id)

    open_invoice_total_cents = sum(invoice["total_cents"] for invoice in invoices)
    recent_invoice_ids = [invoice["id"] for invoice in invoices[:3]]
    has_overdue_invoice = any(
        invoice["status"] == "overdue" for invoice in invoices
    )

    return {
        "customer_id": customer["id"],
        "name": customer["name"],
        "open_invoice_total_cents": open_invoice_total_cents,
        "recent_invoice_ids": recent_invoice_ids,
        "has_overdue_invoice": has_overdue_invoice,
    }
