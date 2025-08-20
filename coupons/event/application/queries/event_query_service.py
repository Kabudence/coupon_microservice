from __future__ import annotations
from typing import Optional, List

from coupons.event.domain.entities.event import EventData
from coupons.event.infraestructure.repositories.event_repository import EventRepository


class EventQueryService:
    def __init__(self, repo: EventRepository):
        self.repo = repo

    def get_by_id(self, id_: int) -> Optional[EventData]:
        return self.repo.get_by_id(id_)

    def get_by_nombre(self, nombre: str) -> Optional[EventData]:
        return self.repo.get_by_nombre(nombre)

    def list_all(self) -> List[EventData]:
        return self.repo.list_all()
