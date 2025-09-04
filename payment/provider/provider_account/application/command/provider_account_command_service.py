from __future__ import annotations

from typing import Optional, Union, Dict, Any

from payment.provider.provider_account.domain.entities.provider_account import ProviderKind, EnvKind, \
    ProviderAccountStatus, ProviderAccountData
from payment.provider.provider_account.infraestructure.repositories.provider_account_repository import \
    ProviderAccountRepository


class ProviderAccountCommandService:
    def __init__(self, repo: ProviderAccountRepository):
        self.repo = repo

    def create(
        self,
        party_id: int,
        provider: ProviderKind,
        env: EnvKind,
        provider_account_id: str,
        public_key: Optional[str] = None,
        secret_json_enc: Optional[Union[str, Dict[str, Any]]] = None,
        status: ProviderAccountStatus = ProviderAccountStatus.ACTIVE,
    ) -> ProviderAccountData:
        data = ProviderAccountData(
            party_id=party_id,
            provider=provider,
            env=env,
            provider_account_id=provider_account_id,
            public_key=public_key,
            secret_json_enc=secret_json_enc,
            status=status,
        )
        return self.repo.create(data)

    def update(
        self,
        id_: int,
        party_id: int,
        provider: ProviderKind,
        env: EnvKind,
        provider_account_id: str,
        public_key: Optional[str] = None,
        secret_json_enc: Optional[Union[str, Dict[str, Any]]] = None,
        status: ProviderAccountStatus = ProviderAccountStatus.ACTIVE,
    ) -> Optional[ProviderAccountData]:
        current = self.repo.get_by_id(id_)
        if not current:
            raise ValueError("ProviderAccount not found.")

        current.party_id = party_id
        current.provider = provider
        current.env = env
        current.provider_account_id = provider_account_id
        current.public_key = public_key
        current.secret_json_enc = secret_json_enc
        current.status = status

        return self.repo.update(current)

    def delete(self, id_: int) -> bool:
        return self.repo.delete(id_)

    def enable(self, id_: int) -> bool:
        return self.repo.enable(id_)

    def disable(self, id_: int) -> bool:
        return self.repo.disable(id_)

    def rotate_secrets(self, id_: int, new_secret_json_enc: Union[str, Dict[str, Any]]) -> bool:
        # Aquí normalmente invocarías un KMS/HSM para cifrar
        return self.repo.rotate_secrets(id_, new_secret_json_enc)

    def upsert(
        self,
        party_id: int,
        provider: ProviderKind,
        env: EnvKind,
        provider_account_id: str,
        public_key: Optional[str] = None,
        secret_json_enc: Optional[Union[str, Dict[str, Any]]] = None,
        status: ProviderAccountStatus = ProviderAccountStatus.ACTIVE,
    ) -> ProviderAccountData:
        data = ProviderAccountData(
            party_id=party_id,
            provider=provider,
            env=env,
            provider_account_id=provider_account_id,
            public_key=public_key,
            secret_json_enc=secret_json_enc,
            status=status,
        )
        return self.repo.upsert_by_unique(data)
