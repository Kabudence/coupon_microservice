from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Union, Dict, Any
import json


class ProviderKind(Enum):
    MERCADOPAGO = "mercadopago"
    STRIPE = "stripe"
    PAYPAL = "paypal"
    OTHER = "other"


class EnvKind(Enum):
    TEST = "test"
    PROD = "prod"


class ProviderAccountStatus(Enum):
    ACTIVE = "active"
    DISABLED = "disabled"


@dataclass
class ProviderAccountData:
    id: Optional[int] = None
    party_id: int = None
    provider: ProviderKind = None
    env: EnvKind = EnvKind.TEST
    provider_account_id: str = ""
    public_key: Optional[str] = None
    secret_json_enc: Optional[Union[str, Dict[str, Any]]] = None
    status: ProviderAccountStatus = ProviderAccountStatus.ACTIVE
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        # Validaciones mínimas
        if self.party_id is None:
            raise ValueError("party_id is required")

        if not isinstance(self.provider, ProviderKind):
            try:
                self.provider = ProviderKind(str(self.provider))
            except Exception:
                raise ValueError("provider must be one of ProviderKind")

        if not isinstance(self.env, EnvKind):
            try:
                self.env = EnvKind(str(self.env))
            except Exception:
                raise ValueError("env must be one of EnvKind")

        if not self.provider_account_id or not str(self.provider_account_id).strip():
            raise ValueError("provider_account_id is required")

        if not isinstance(self.status, ProviderAccountStatus):
            try:
                self.status = ProviderAccountStatus(str(self.status))
            except Exception:
                raise ValueError("status must be one of ProviderAccountStatus")

        # Normaliza el secret_json_enc a string JSON (si vino dict)
        if isinstance(self.secret_json_enc, dict):
            self.secret_json_enc = json.dumps(self.secret_json_enc, ensure_ascii=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "party_id": self.party_id,
            "provider": self.provider.value,
            "env": self.env.value,
            "provider_account_id": self.provider_account_id,
            "public_key": self.public_key,
            "secret_json_enc": self.secret_json_enc,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
