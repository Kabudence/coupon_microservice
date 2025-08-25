from payment.provider.provider_customer.domain.entities.provider_customer import ProviderCustomerData
from payment.provider.provider_customer.domain.value_objects.enums import ProviderEnum, EnvEnum, ProviderCustomerStatus
from payment.provider.provider_customer.infraestructure.repositories.provider_customer_repository import ProviderCustomerRepository

from typing import Optional, List

class ProviderCustomerQueryService:
    """
    Consultas de lectura para provider_customers.
    """
    def __init__(self, repo: ProviderCustomerRepository):
        self.repo = repo

    def get_by_id(self, id_: int) -> Optional[ProviderCustomerData]:
        return self.repo.get_by_id(id_)

    def get_by_party_provider_env(
        self, party_id: int, provider: ProviderEnum | str, env: EnvEnum | str
    ) -> Optional[ProviderCustomerData]:
        return self.repo.get_by_party_provider_env(party_id, provider, env)

    def get_by_provider_external_id(
        self, provider: ProviderEnum | str, env: EnvEnum | str, provider_customer_id: str
    ) -> Optional[ProviderCustomerData]:
        return self.repo.get_by_provider_external_id(provider, env, provider_customer_id)

    def list_by_party(self, party_id: int) -> List[ProviderCustomerData]:
        return self.repo.list_by_party(party_id)

    def list_all(self, limit: int = 100, offset: int = 0) -> List[ProviderCustomerData]:
        return self.repo.list_all(limit=limit, offset=offset)