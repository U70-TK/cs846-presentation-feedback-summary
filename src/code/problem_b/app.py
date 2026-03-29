from fastapi import Depends, FastAPI

import auth
from customer_report import build_customer_summary
from store import get_customer

app = FastAPI(title="Customer Service")


@app.get("/customers/{customer_id}")
def get_customer_profile(
    customer_id: int,
    _: dict = Depends(auth.get_current_user),
) -> dict:
    customer = get_customer(customer_id)
    if customer is None:
        return {"detail": "Customer not found"}
    return customer


@app.get("/customers/{customer_id}/summary")
def get_customer_summary(
    customer_id: int,
    _: dict = Depends(auth.get_current_user),
) -> dict:
    return build_customer_summary(customer_id)
