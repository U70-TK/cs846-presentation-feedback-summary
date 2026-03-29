from fastapi import Depends, FastAPI, HTTPException

import auth
from store import get_customer

app = FastAPI(title="Customer Service")


@app.get("/customers/{customer_id}")
def get_customer_profile(
    customer_id: int,
    _: dict = Depends(auth.get_current_user),
) -> dict:
    customer = get_customer(customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer
