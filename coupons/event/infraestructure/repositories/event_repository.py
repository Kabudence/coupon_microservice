from __future__ import annotations
from typing import Optional, List

from coupons.event.domain.entities.event import EventData
from coupons.event.infraestructure.model.event_model import EventModel


class EventRepository:
    def _to_entity(self, rec: EventModel) -> EventData:
        return EventData(
            id=rec.id,
            nombre=rec.nombre,
            description=rec.description,
            created_at=rec.created_at,
        )

    def get_by_id(self, id_: int) -> Optional[EventData]:
        try:
            rec = EventModel.get(EventModel.id == id_)
            return self._to_entity(rec)
        except EventModel.DoesNotExist:
            return None

    def get_by_nombre(self, nombre: str) -> Optional[EventData]:
        if not nombre:
            return None
        try:
            rec = EventModel.get(EventModel.nombre == nombre.strip())
            return self._to_entity(rec)
        except EventModel.DoesNotExist:
            return None

    def list_all(self) -> List[EventData]:
        return [self._to_entity(r) for r in EventModel.select().order_by(EventModel.nombre.asc())]

    def create(self, ev: EventData) -> EventData:
        rec = EventModel.create(
            nombre=ev.nombre,
            description=ev.description,
        )
        return self._to_entity(rec)

    def update(self, ev: EventData) -> Optional[EventData]:
        try:
            rec = EventModel.get(EventModel.id == ev.id)
            rec.nombre = ev.nombre
            rec.description = ev.description
            rec.save()
            return self._to_entity(rec)
        except EventModel.DoesNotExist:
            return None

    def delete(self, id_: int) -> bool:
        try:
            rec = EventModel.get(EventModel.id == id_)
            rec.delete_instance()
            return True
        except EventModel.DoesNotExist:
            return False
