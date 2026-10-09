"""Main API v1 router consolidating all domain endpoints."""

from fastapi import APIRouter
from backend.app.api.v1.endpoints import (
    auth,
    operators,
    orders,
    payments,
    plans,
    recipients,
    transactions,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(operators.router)
api_router.include_router(plans.router)
api_router.include_router(orders.router)
api_router.include_router(payments.router)
api_router.include_router(transactions.router)
api_router.include_router(recipients.router)
