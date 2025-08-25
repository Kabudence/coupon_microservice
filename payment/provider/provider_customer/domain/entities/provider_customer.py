from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from payment.provider.provider_customer.domain.value_objects.enums import ProviderCustomerStatus, ProviderEnum, EnvEnum


@dataclass
class ProviderCustomerData:
    """
    Representa el 'customer' del COMPRADOR en un proveedor externo (p. ej. Mercado Pago).
    1 fila por (party_id, provider, env). Guarda el ID externo del customer.
    """
    id: Optional[int] = None
    party_id: int = None
    provider: ProviderEnum | str = ProviderEnum.MERCADOPAGO
    env: EnvEnum | str = EnvEnum.TEST
    provider_customer_id: str = ""
    status: ProviderCustomerStatus | str = ProviderCustomerStatus.ACTIVE
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.party_id is None:
            raise ValueError("party_id es requerido")

        # Normalizar value_objects si vienen como string
        if not isinstance(self.provider, ProviderEnum):
            self.provider = ProviderEnum(str(self.provider))
        if not isinstance(self.env, EnvEnum):
            self.env = EnvEnum(str(self.env))
        if not isinstance(self.status, ProviderCustomerStatus):
            self.status = ProviderCustomerStatus(str(self.status))

        # Validaciones básicas
        if not self.provider_customer_id or not str(self.provider_customer_id).strip():
            raise ValueError("provider_customer_id es requerido")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "party_id": self.party_id,
            "provider": self.provider.value if isinstance(self.provider, ProviderEnum) else str(self.provider),
            "env": self.env.value if isinstance(self.env, EnvEnum) else str(self.env),
            "provider_customer_id": self.provider_customer_id,
            "status": self.status.value if isinstance(self.status, ProviderCustomerStatus) else str(self.status),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
