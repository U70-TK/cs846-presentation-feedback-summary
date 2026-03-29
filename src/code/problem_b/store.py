CUSTOMERS = {
    1: {"id": 1, "name": "Acme Co"},
    2: {"id": 2, "name": "Globex"},
}


INVOICES = [
    {
        "id": 101,
        "customer_id": 1,
        "status": "paid",
        "total_cents": 5000,
        "created_at": "2026-02-01T10:00:00Z",
    },
    {
        "id": 102,
        "customer_id": 1,
        "status": "open",
        "total_cents": 2000,
        "created_at": "2026-03-12T10:00:00Z",
    },
    {
        "id": 103,
        "customer_id": 1,
        "status": "overdue",
        "total_cents": 7000,
        "created_at": "2026-03-15T10:00:00Z",
    },
    {
        "id": 201,
        "customer_id": 2,
        "status": "open",
        "total_cents": 1500,
        "created_at": "2026-03-02T10:00:00Z",
    },
]


def get_customer(customer_id: int) -> dict | None:
    return CUSTOMERS.get(customer_id)


def list_invoices_for_customer(customer_id: int) -> list[dict]:
    return [invoice for invoice in INVOICES if invoice["customer_id"] == customer_id]
