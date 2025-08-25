from __future__ import annotations

import datetime
from typing import Optional

from payment.checkout.domain.entities.checkout_session import CheckoutSessionData
from payment.checkout.infraestructure.repositories.checkout_session_repository import CheckoutSessionRepository


class CheckoutSessionCommandService:
    """
    Casos de uso de escritura / orquestación para Checkout Sessions.
    """
    def __init__(self, repo: CheckoutSessionRepository):
        self.repo = repo

    def create(
        self,
        order_id: int,
        provider_session_id: str,
        init_url: Optional[str] = None,
        sandbox_url: Optional[str] = None,
        expires_at: Optional[datetime.datetime] = None,
    ) -> CheckoutSessionData:
        entity = CheckoutSessionData(
            order_id=order_id,
            provider_session_id=provider_session_id,
            init_url=init_url,
            sandbox_url=sandbox_url,
            expires_at=expires_at,
        )
        return self.repo.create(entity)

    def create_or_replace_for_order(
        self,
        order_id: int,
        provider_session_id: str,
        init_url: Optional[str] = None,
        sandbox_url: Optional[str] = None,
        expires_at: Optional[datetime.datetime] = None,
        expire_previous: bool = True
    ) -> CheckoutSessionData:
        return self.repo.create_or_replace_for_order(
            order_id=order_id,
            provider_session_id=provider_session_id,
            init_url=init_url,
            sandbox_url=sandbox_url,
            expires_at=expires_at,
            expire_previous=expire_previous,
        )

    def update_urls_by_provider_session_id(
        self,
        provider_session_id: str,
        init_url: Optional[str] = None,
        sandbox_url: Optional[str] = None,
        expires_at: Optional[datetime.datetime] = None,
    ):
        return self.repo.update_urls_by_provider_session_id(
            provider_session_id=provider_session_id,
            init_url=init_url,
            sandbox_url=sandbox_url,
            expires_at=expires_at,
        )

    def expire_by_provider_session_id(self, provider_session_id: str):
        return self.repo.expire_by_provider_session_id(provider_session_id)

    def delete(self, id_: int) -> bool:
        return self.repo.delete(id_)
