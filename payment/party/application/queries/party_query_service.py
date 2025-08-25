from typing import Optional, List, Iterable

from payment.party.domain.entities.party import PartyData, PartyAppName, PartySubjectType
from payment.party.infraestructure.repositories.party_repository import PartyRepository


class PartyQueryService:
    def __init__(self, repo: PartyRepository):
        self.repo = repo

    def get_by_id(self, party_id: int) -> Optional[PartyData]:
        return self.repo.get_by_id(party_id)

    def get_by_subject(
        self,
        app_name: PartyAppName | str,
        subject_type: PartySubjectType | str,
        subject_id: int
    ) -> Optional[PartyData]:
        return self.repo.get_by_subject(app_name, subject_type, subject_id)

    def list_all(self) -> List[PartyData]:
        return self.repo.list_all()

    def search_by_name(self, text: str, limit: int = 50) -> List[PartyData]:
        return self.repo.search_by_name(text, limit)

    def list_by_app_subjects(self, triples: Iterable[tuple[str, str, int]]) -> List[PartyData]:
        return self.repo.list_by_app_subjects(triples)
