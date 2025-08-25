from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from payment.provider.customer_sources.domain.valueobjects.enums import PaymentSourceType, PaymentSourceStatus
from payment.provider.provider_customer.domain.value_objects.enums import ProviderEnum, EnvEnum


@dataclass
class PaymentSourceData:
    """
    Método guardado del COMPRADOR en un proveedor (ej: tarjeta o wallet en Mercado Pago).
    - Se cuelga de un 'provider_customer' (del comprador) mediante provider_customer_pk.
    - Para tarjetas: provider_source_id es el id de la tarjeta en el proveedor (ej: MP card_id).
    - Para wallet/account_money: provider_source_id puede ser None.
    """
    id: Optional[int] = None
    provider_customer_pk: int = None

    provider: ProviderEnum | str = ProviderEnum.MERCADOPAGO
    env: EnvEnum | str = EnvEnum.TEST

    provider_source_id: Optional[str] = None
    source_type: PaymentSourceType | str = PaymentSourceType.CARD

    brand: Optional[str] = None
    last_four: Optional[str] = None
    exp_month: Optional[int] = None
    exp_year: Optional[int] = None
    holder_name: Optional[str] = None

    status: PaymentSourceStatus | str = PaymentSourceStatus.ACTIVE

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.provider_customer_pk is None:
            raise ValueError("provider_customer_pk es requerido")

        # Normalizar enums.py si vienen como string
        if not isinstance(self.provider, ProviderEnum):
            self.provider = ProviderEnum(str(self.provider))
        if not isinstance(self.env, EnvEnum):
            self.env = EnvEnum(str(self.env))
        if not isinstance(self.source_type, PaymentSourceType):
            self.source_type = PaymentSourceType(str(self.source_type))
        if not isinstance(self.status, PaymentSourceStatus):
            self.status = PaymentSourceStatus(str(self.status))

        # Validaciones según el tipo
        if self.source_type in (PaymentSourceType.CARD,):
            if not self.provider_source_id or not str(self.provider_source_id).strip():
                raise ValueError("provider_source_id es requerido para source_type=CARD")
            if not self.last_four or len(str(self.last_four)) != 4:
                raise ValueError("last_four inválido para tarjeta")
            if self.exp_month is None or self.exp_year is None:
                raise ValueError("exp_month y exp_year requeridos para tarjeta")
            if self.brand:
                self.brand = str(self.brand).strip().lower()

        if self.source_type in (PaymentSourceType.WALLET, PaymentSourceType.ACCOUNT_MONEY):
            # En wallet/account_money permitimos provider_source_id = None
            pass

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "provider_customer_pk": self.provider_customer_pk,
            "provider": self.provider.value if isinstance(self.provider, ProviderEnum) else str(self.provider),
            "env": self.env.value if isinstance(self.env, EnvEnum) else str(self.env),
            "provider_source_id": self.provider_source_id,
            "source_type": self.source_type.value if isinstance(self.source_type, PaymentSourceType) else str(self.source_type),
            "brand": self.brand,
            "last_four": self.last_four,
            "exp_month": self.exp_month,
            "exp_year": self.exp_year,
            "holder_name": self.holder_name,
            "status": self.status.value if isinstance(self.status, PaymentSourceStatus) else str(self.status),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
