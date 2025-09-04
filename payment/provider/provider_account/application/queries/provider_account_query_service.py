from typing import Optional, List, Dict, Any

from payment.provider.provider_account.domain.entities.provider_account import ProviderAccountData, ProviderKind, \
    EnvKind
from payment.provider.provider_account.infraestructure.repositories.provider_account_repository import \
    ProviderAccountRepository


class ProviderAccountQueryService:
    def __init__(self, repo: ProviderAccountRepository):
        self.repo = repo

    def get_by_id(self, id_: int) -> Optional[ProviderAccountData]:
        return self.repo.get_by_id(id_)

    def get_by_unique(self, provider: ProviderKind, env: EnvKind, provider_account_id: str) -> Optional[ProviderAccountData]:
        return self.repo.get_by_unique(provider, env, provider_account_id)

    def list_by_party(self, party_id: int, only_active: bool = False) -> List[ProviderAccountData]:
        return self.repo.list_by_party(party_id, only_active=only_active)

    def list_by_party_env(
        self,
        party_id: int,
        env: EnvKind,
        provider: Optional[ProviderKind] = None,
        only_active: bool = False
    ) -> List[ProviderAccountData]:
        return self.repo.list_by_party_env(
            party_id=party_id,
            env=env,
            provider=provider,
            only_active=only_active,
        )

    def find_active_account_for_party(self, party_id: int, provider: ProviderKind, env: EnvKind) -> Optional[ProviderAccountData]:
        return self.repo.find_active_account_for_party(party_id, provider, env)

    def stats_count_by_provider_env(self) -> List[Dict[str, Any]]:
        return self.repo.count_by_provider_env()

    def dump_model(self, id_: int):
        return self.repo.dump_model(id_)