from __future__ import annotations
from typing import Optional

from coupons.event.domain.entities.event import EventData
from coupons.event.infraestructure.repositories.event_repository import EventRepository


class EventCommandService:
    def __init__(self, repo: EventRepository):
        self.repo = repo

    def create(self, nombre: str, description: Optional[str] = None) -> EventData:
        entity = EventData(nombre=nombre, description=description)
        # Unicidad por nombre
        existing = self.repo.get_by_nombre(entity.nombre)
        if existing:
            raise ValueError(f"Event with nombre '{entity.nombre}' already exists.")
        return self.repo.create(entity)

    def update(self, id_: int, nombre: str, description: Optional[str] = None) -> EventData:
        current = self.repo.get_by_id(id_)
        if not current:
            raise ValueError("Event not found.")

        nombre = (nombre or "").strip()
        if not nombre:
            raise ValueError("nombre cannot be empty.")

        other = self.repo.get_by_nombre(nombre)
        if other and other.id != id_:
            raise ValueError(f"Event with nombre '{nombre}' already exists.")

        current.nombre = nombre
        current.description = (description.strip() if isinstance(description, str) else description)

        updated = self.repo.update(current)
        if not updated:
            raise ValueError("Event not found.")
        return updated

    def delete(self, id_: int) -> bool:
        return self.repo.delete(id_)
