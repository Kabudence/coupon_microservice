from __future__ import annotations

from typing import Optional

from payment.provider.provider_customer.domain.entities.provider_customer import ProviderCustomerData
from payment.provider.provider_customer.domain.value_objects.enums import ProviderEnum, EnvEnum, ProviderCustomerStatus
from payment.provider.provider_customer.infraestructure.repositories.provider_customer_repository import ProviderCustomerRepository




class ProviderCustomerCommandService:
    """
    Orquesta casos de uso de escritura para provider_customers.
    """
    def __init__(self, repo: ProviderCustomerRepository):
        self.repo = repo

    def create(
        self,
        party_id: int,
        provider: ProviderEnum | str,
        env: EnvEnum | str,
        provider_customer_id: str,
        status: ProviderCustomerStatus | str = ProviderCustomerStatus.ACTIVE,
    ) -> ProviderCustomerData:
        entity = ProviderCustomerData(
            party_id=party_id,
            provider=provider,
            env=env,
            provider_customer_id=provider_customer_id,
            status=status,
        )
        return self.repo.create(entity)

    def update(
        self,
        id_: int,
        party_id: int,
        provider: ProviderEnum | str,
        env: EnvEnum | str,
        provider_customer_id: str,
        status: ProviderCustomerStatus | str = ProviderCustomerStatus.ACTIVE,
    ) -> Optional[ProviderCustomerData]:
        current = self.repo.get_by_id(id_)
        if not current:
            return None
        current.party_id = party_id
        current.provider = provider
        current.env = env
        current.provider_customer_id = provider_customer_id
        current.status = status
        return self.repo.update(current)

    def upsert_by_party(
        self,
        party_id: int,
        provider: ProviderEnum | str,
        env: EnvEnum | str,
        provider_customer_id: str,
        status: ProviderCustomerStatus | str = ProviderCustomerStatus.ACTIVE,
    ) -> ProviderCustomerData:
        return self.repo.upsert_by_party(
            party_id=party_id,
            provider=provider,
            env=env,
            provider_customer_id=provider_customer_id,
            status=status,
        )

    def set_status(
        self,
        party_id: int,
        provider: ProviderEnum | str,
        env: EnvEnum | str,
        status: ProviderCustomerStatus | str,
    ) -> Optional[ProviderCustomerData]:
        return self.repo.set_status(party_id, provider, env, status)

    def delete(self, id_: int) -> bool:
        return self.repo.delete(id_)
