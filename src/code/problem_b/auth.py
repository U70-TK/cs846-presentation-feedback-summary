from fastapi import Header, HTTPException, status


def get_current_user(authorization: str | None = Header(default=None)) -> dict:
    if authorization != "Bearer demo-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    return {"id": 1, "role": "support"}
