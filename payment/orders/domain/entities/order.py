from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any

from payment.orders.domain.value_objects.enums import OrderStatus, PaymentFlow
from payment.provider.provider_customer.domain.value_objects.enums import ProviderEnum, EnvEnum


@dataclass
class OrderData:
    """
    Fuente de verdad del pago. Integra negocio + datos del proveedor.
    """
    id: Optional[int] = None

    # relación negocio
    buyer_party_id: int = None
    seller_party_id: int = None

    # pago
    amount: Decimal | float | str = 0
    currency: str = "PEN"

    # estado
    status: OrderStatus | str = OrderStatus.PENDING

    # metadata negocio
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    # integración con pasarela (unificados)
    flow: Optional[PaymentFlow | str] = None
    provider: Optional[ProviderEnum | str] = None
    env: Optional[EnvEnum | str] = EnvEnum.TEST

    provider_account_id: Optional[int] = None  # FK lógica a provider_accounts.id
    provider_payment_id: Optional[str] = None
    idempotency_key: Optional[str] = None

    # resumen del método de pago
    payment_type: Optional[str] = None          # 'credit_card','account_money',...
    method_brand: Optional[str] = None          # 'visa','master','amex',...
    method_last_four: Optional[str] = None

    # timestamps
    paid_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        # normalizaciones de enums si vinieron como string
        if not isinstance(self.status, OrderStatus):
            self.status = OrderStatus(str(self.status))

        if self.flow is not None and not isinstance(self.flow, PaymentFlow):
            self.flow = PaymentFlow(str(self.flow))

        if self.provider is not None and not isinstance(self.provider, ProviderEnum):
            self.provider = ProviderEnum(str(self.provider))

        if not isinstance(self.env, EnvEnum):
            self.env = EnvEnum(str(self.env))

        # normalizar amount
        self.amount = Decimal(str(self.amount))
        if self.amount <= 0:
            raise ValueError("amount must be > 0")

        if not self.currency or len(self.currency) != 3:
            raise ValueError("currency must be a 3-letter code")

        if self.buyer_party_id is None or self.seller_party_id is None:
            raise ValueError("buyer_party_id and seller_party_id are required")

        # metadata por defecto dict
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "buyer_party_id": self.buyer_party_id,
            "seller_party_id": self.seller_party_id,
            "amount": str(self.amount),
            "currency": self.currency,
            "status": self.status.value,
            "description": self.description,
            "metadata": self.metadata or {},
            "flow": (self.flow.value if isinstance(self.flow, PaymentFlow) else self.flow),
            "provider": (self.provider.value if isinstance(self.provider, ProviderEnum) else self.provider),
            "env": self.env.value,
            "provider_account_id": self.provider_account_id,
            "provider_payment_id": self.provider_payment_id,
            "idempotency_key": self.idempotency_key,
            "payment_type": self.payment_type,
            "method_brand": self.method_brand,
            "method_last_four": self.method_last_four,
            "paid_at": self.paid_at.isoformat() if self.paid_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
