from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CheckoutSessionData:
    """
    Sesión de checkout hosted (p. ej., Mercado Pago Checkout Pro)
    - Se ata a una order_id.
    - Guarda el provider_session_id (preference_id en MP) y URLs.
    - 'expires_at' sirve para marcar expiración de la sesión.
    """
    id: Optional[int] = None
    order_id: int = None

    provider_session_id: str = ""   # p. ej., MP preference_id
    init_url: Optional[str] = None  # init_point
    sandbox_url: Optional[str] = None
    expires_at: Optional[datetime] = None

    created_at: Optional[datetime] = None

    def __post_init__(self):
        if self.order_id is None:
            raise ValueError("order_id es requerido")
        if not self.provider_session_id or not str(self.provider_session_id).strip():
            raise ValueError("provider_session_id es requerido")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "order_id": self.order_id,
            "provider_session_id": self.provider_session_id,
            "init_url": self.init_url,
            "sandbox_url": self.sandbox_url,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
