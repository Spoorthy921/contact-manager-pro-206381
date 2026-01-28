"""
FastAPI backend for the Contact Manager application.

Provides:
- Authentication (register/login) using email + password.
- JWT bearer token issuance.
- Per-user contact CRUD and search endpoints.

Environment variables (must be set via .env, do not hardcode):
- POSTGRES_URL, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_PORT
- ALLOWED_ORIGINS (comma-separated)
- JWT_SECRET (recommended). If not provided, app will use a temporary dev fallback.
"""

from __future__ import annotations

import os
from typing import List, Optional

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth as auth_router
from .routers import contacts as contacts_router


def _get_allowed_origins() -> List[str]:
    allowed = os.getenv("ALLOWED_ORIGINS", "*").strip()
    if allowed == "*":
        return ["*"]
    return [o.strip() for o in allowed.split(",") if o.strip()]


openapi_tags = [
    {"name": "Health", "description": "Service health checks."},
    {"name": "Auth", "description": "User registration and login."},
    {"name": "Contacts", "description": "Contact CRUD and search operations (JWT required)."},
]

app = FastAPI(
    title="Contact Manager API",
    description="Backend APIs for authentication and contact CRUD/search.",
    version="1.0.0",
    openapi_tags=openapi_tags,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_allowed_origins(),
    allow_credentials=True,
    allow_methods=[m.strip() for m in os.getenv("ALLOWED_METHODS", "*").split(",")],
    allow_headers=[h.strip() for h in os.getenv("ALLOWED_HEADERS", "*").split(",")],
    max_age=int(os.getenv("CORS_MAX_AGE", "3600")),
)


@app.get("/", tags=["Health"], summary="Health check", operation_id="health_check")
def health_check():
    """Basic health check endpoint."""
    return {"message": "Healthy"}


app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
app.include_router(contacts_router.router, prefix="/contacts", tags=["Contacts"])
