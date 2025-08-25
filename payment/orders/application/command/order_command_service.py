from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Optional, Dict, Any

from payment.orders.domain.entities.order import OrderData
from payment.orders.domain.value_objects.enums import OrderStatus, PaymentFlow
from payment.orders.infraestructure.repositories.order_repository import OrderRepository
from payment.provider.provider_customer.domain.value_objects.enums import ProviderEnum, EnvEnum


class OrderCommandService:
    """
    Casos de uso de escritura / orquestación para Orders.
    """
    def __init__(self, repo: OrderRepository):
        self.repo = repo

    def create(
        self,
        buyer_party_id: int,
        seller_party_id: int,
        amount: Decimal | float | str,
        currency: str = "PEN",
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> OrderData:
        entity = OrderData(
            buyer_party_id=buyer_party_id,
            seller_party_id=seller_party_id,
            amount=amount,
            currency=currency,
            status=OrderStatus.PENDING,
            description=description,
            metadata=metadata or {},
        )
        return self.repo.create(entity)

    def set_checkout_context(
        self,
        order_id: int,
        flow: PaymentFlow | str,
        provider: ProviderEnum | str,
        env: EnvEnum | str = EnvEnum.TEST,
        provider_account_id: Optional[int] = None,
        idempotency_key: Optional[str] = None,
        mark_processing: bool = True,
        extra_metadata: Optional[Dict[str, Any]] = None
    ):
        return self.repo.set_checkout_context(
            order_id=order_id,
            flow=flow,
            provider=provider,
            env=env,
            provider_account_id=provider_account_id,
            idempotency_key=idempotency_key,
            mark_processing=mark_processing,
            extra_metadata=extra_metadata,
        )

    def mark_paid(
        self,
        order_id: int,
        provider_payment_id: str,
        payment_type: Optional[str] = None,
        method_brand: Optional[str] = None,
        method_last_four: Optional[str] = None,
        paid_at: Optional[datetime.datetime] = None,
        extra_metadata: Optional[Dict[str, Any]] = None
    ):
        return self.repo.mark_paid(
            order_id=order_id,
            provider_payment_id=provider_payment_id,
            payment_type=payment_type,
            method_brand=method_brand,
            method_last_four=method_last_four,
            paid_at=paid_at,
            extra_metadata=extra_metadata,
        )

    def mark_failed(
        self,
        order_id: int,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        extra_metadata: Optional[Dict[str, Any]] = None
    ):
        return self.repo.mark_failed(
            order_id=order_id,
            error_code=error_code,
            error_message=error_message,
            extra_metadata=extra_metadata,
        )

    def cancel(self, order_id: int, reason: Optional[str] = None):
        return self.repo.cancel(order_id, reason=reason)
