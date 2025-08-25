from typing import Optional

from payment.party.domain.entities.party import PartyAppName, PartySubjectType, PartyData
from payment.party.infraestructure.repositories.party_repository import PartyRepository


class PartyCommandService:
    def __init__(self, repo: PartyRepository):
        self.repo = repo

    def create(
        self,
        app_name: PartyAppName | str,
        subject_type: PartySubjectType | str,
        subject_id: int,
        display_name: Optional[str] = None,
    ) -> PartyData:
        entity = PartyData(
            app_name=app_name,
            subject_type=subject_type,
            subject_id=subject_id,
            display_name=display_name,
        )
        return self.repo.create(entity)

    def upsert_by_subject(
        self,
        app_name: PartyAppName | str,
        subject_type: PartySubjectType | str,
        subject_id: int,
        display_name: Optional[str] = None,
    ) -> PartyData:
        return self.repo.upsert_by_subject(app_name, subject_type, subject_id, display_name)

    def update_display_name(self, party_id: int, display_name: Optional[str]) -> Optional[PartyData]:
        current = self.repo.get_by_id(party_id)
        if not current:
            return None
        current.display_name = (display_name.strip() if display_name else None)
        return self.repo.update(current)

    def delete(self, party_id: int) -> bool:
        return self.repo.delete(party_id)
