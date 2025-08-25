from __future__ import annotations

from typing import Optional, List

from payment.checkout.domain.entities.checkout_session import CheckoutSessionData
from payment.checkout.infraestructure.repositories.checkout_session_repository import CheckoutSessionRepository


class CheckoutSessionQueryService:
    """
    Casos de uso de lectura para Checkout Sessions.
    """
    def __init__(self, repo: CheckoutSessionRepository):
        self.repo = repo

    def get_by_id(self, id_: int) -> Optional[CheckoutSessionData]:
        return self.repo.get_by_id(id_)

    def get_by_provider_session_id(self, provider_session_id: str) -> Optional[CheckoutSessionData]:
        return self.repo.get_by_provider_session_id(provider_session_id)

    def list_by_order(self, order_id: int, only_active: bool = False) -> List[CheckoutSessionData]:
        return self.repo.list_by_order(order_id=order_id, only_active=only_active)
