from typing import Optional, List, Iterable
from peewee import IntegrityError, fn

from payment.party.domain.entities.party import PartyData, PartyAppName, PartySubjectType
from payment.party.infraestructure.model.party_model import PartyModel


class PartyRepository:
    def _to_entity(self, rec: PartyModel) -> PartyData:
        return PartyData(
            id=rec.id,
            app_name=PartyAppName(rec.app_name),
            subject_type=PartySubjectType(rec.subject_type),
            subject_id=int(rec.subject_id),
            display_name=rec.display_name,
            created_at=rec.created_at,
            updated_at=rec.updated_at,
        )

    def get_by_id(self, id_: int) -> Optional[PartyData]:
        try:
            rec = PartyModel.get(PartyModel.id == id_)
            return self._to_entity(rec)
        except PartyModel.DoesNotExist:
            return None

    def get_by_subject(
        self,
        app_name: PartyAppName | str,
        subject_type: PartySubjectType | str,
        subject_id: int
    ) -> Optional[PartyData]:
        an = app_name.value if isinstance(app_name, PartyAppName) else str(app_name)
        st = subject_type.value if isinstance(subject_type, PartySubjectType) else str(subject_type)
        try:
            rec = PartyModel.get(
                (PartyModel.app_name == an) &
                (PartyModel.subject_type == st) &
                (PartyModel.subject_id == int(subject_id))
            )
            return self._to_entity(rec)
        except PartyModel.DoesNotExist:
            return None

    def list_all(self) -> List[PartyData]:
        return [self._to_entity(r) for r in PartyModel.select()]

    def search_by_name(self, text: str, limit: int = 50) -> List[PartyData]:
        q = (PartyModel
             .select()
             .where(PartyModel.display_name.contains(text))
             .limit(limit))
        return [self._to_entity(r) for r in q]

    def list_by_app_subjects(self, triples: Iterable[tuple[str, str, int]]) -> List[PartyData]:
        # triples = [(app_name, subject_type, subject_id), ...]
        triples = list(triples)
        if not triples:
            return []
        query = None
        for an, st, sid in triples:
            cond = ((PartyModel.app_name == an) &
                    (PartyModel.subject_type == st) &
                    (PartyModel.subject_id == int(sid)))
            query = cond if query is None else (query | cond)
        q = PartyModel.select().where(query)
        return [self._to_entity(r) for r in q]

    def create(self, entity: PartyData) -> PartyData:
        try:
            rec = PartyModel.create(
                app_name=entity.app_name.value,
                subject_type=entity.subject_type.value,
                subject_id=entity.subject_id,
                display_name=entity.display_name,
            )
            return self._to_entity(rec)
        except IntegrityError as e:
            raise ValueError("Party already exists for (app_name, subject_type, subject_id)") from e

    def update(self, entity: PartyData) -> Optional[PartyData]:
        try:
            rec = PartyModel.get(PartyModel.id == entity.id)
        except PartyModel.DoesNotExist:
            return None
        # No permitimos cambiar la clave lógica (app_name, subject_type, subject_id)
        rec.display_name = entity.display_name
        rec.save()
        return self._to_entity(rec)

    def delete(self, id_: int) -> bool:
        try:
            rec = PartyModel.get(PartyModel.id == id_)
        except PartyModel.DoesNotExist:
            return False
        rec.delete_instance()
        return True

    def upsert_by_subject(
        self,
        app_name: PartyAppName | str,
        subject_type: PartySubjectType | str,
        subject_id: int,
        display_name: Optional[str] = None,
    ) -> PartyData:
        an = app_name.value if isinstance(app_name, PartyAppName) else str(app_name)
        st = subject_type.value if isinstance(subject_type, PartySubjectType) else str(subject_type)

        # Insert … ON CONFLICT (app_name, subject_type, subject_id) DO UPDATE display_name
        PartyModel.insert(
            app_name=an,
            subject_type=st,
            subject_id=int(subject_id),
            display_name=(display_name.strip() if display_name else None),
        ).on_conflict(
            conflict_target=[PartyModel.app_name, PartyModel.subject_type, PartyModel.subject_id],
            update={PartyModel.display_name: (display_name.strip() if display_name else None)}
        ).execute()

        rec = PartyModel.get(
            (PartyModel.app_name == an) &
            (PartyModel.subject_type == st) &
            (PartyModel.subject_id == int(subject_id))
        )
        return self._to_entity(rec)
