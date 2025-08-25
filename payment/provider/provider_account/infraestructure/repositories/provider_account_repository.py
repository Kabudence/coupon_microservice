from __future__ import annotations

import json
from typing import Optional, List, Dict, Any, Union

from peewee import fn
from playhouse.shortcuts import model_to_dict

from payments.provider_accounts.domain.entities.provider_account import (
    ProviderAccountData, ProviderKind, EnvKind, ProviderAccountStatus
)
from payments.provider_accounts.infraestructure.model.provider_account_model import ProviderAccountModel


class ProviderAccountRepository:
    # -------------------------
    # Mappers
    # -------------------------
    def _row_to_entity(self, m: ProviderAccountModel) -> ProviderAccountData:
        # Normaliza JSON; puede venir como dict si JSONField real, o como str si TEXT
        raw_secret = m.secret_json_enc
        if isinstance(raw_secret, (dict, list)):
            secret_str = json.dumps(raw_secret, ensure_ascii=False)
        else:
            secret_str = raw_secret

        return ProviderAccountData(
            id=m.id,
            party_id=m.party_id,
            provider=ProviderKind(m.provider),
            env=EnvKind(m.env),
            provider_account_id=m.provider_account_id,
            public_key=m.public_key,
            secret_json_enc=secret_str,
            status=ProviderAccountStatus(m.status),
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    # -------------------------
    # Queries
    # -------------------------
    def get_by_id(self, id_: int) -> Optional[ProviderAccountData]:
        try:
            rec = ProviderAccountModel.get(ProviderAccountModel.id == id_)
            return self._row_to_entity(rec)
        except ProviderAccountModel.DoesNotExist:
            return None

    def get_by_unique(self, provider: ProviderKind, env: EnvKind, provider_account_id: str) -> Optional[ProviderAccountData]:
        try:
            rec = (ProviderAccountModel
                   .select()
                   .where(
                       (ProviderAccountModel.provider == provider.value) &
                       (ProviderAccountModel.env == env.value) &
                       (ProviderAccountModel.provider_account_id == provider_account_id)
                   )
                   .get())
            return self._row_to_entity(rec)
        except ProviderAccountModel.DoesNotExist:
            return None

    def list_by_party(self, party_id: int, only_active: bool = False) -> List[ProviderAccountData]:
        q = ProviderAccountModel.select().where(ProviderAccountModel.party_id == party_id)
        if only_active:
            q = q.where(ProviderAccountModel.status == ProviderAccountStatus.ACTIVE.value)
        q = q.order_by(ProviderAccountModel.provider, ProviderAccountModel.env)
        return [self._row_to_entity(r) for r in q]

    def list_by_party_env(
        self,
        party_id: int,
        env: EnvKind,
        provider: Optional[ProviderKind] = None,
        only_active: bool = False
    ) -> List[ProviderAccountData]:
        q = (ProviderAccountModel
             .select()
             .where(
                 (ProviderAccountModel.party_id == party_id) &
                 (ProviderAccountModel.env == env.value)
             ))
        if provider:
            q = q.where(ProviderAccountModel.provider == provider.value)
        if only_active:
            q = q.where(ProviderAccountModel.status == ProviderAccountStatus.ACTIVE.value)
        q = q.order_by(ProviderAccountModel.provider)
        return [self._row_to_entity(r) for r in q]

    def find_active_account_for_party(self, party_id: int, provider: ProviderKind, env: EnvKind) -> Optional[ProviderAccountData]:
        q = (ProviderAccountModel
             .select()
             .where(
                 (ProviderAccountModel.party_id == party_id) &
                 (ProviderAccountModel.provider == provider.value) &
                 (ProviderAccountModel.env == env.value) &
                 (ProviderAccountModel.status == ProviderAccountStatus.ACTIVE.value)
             )
             .limit(1))
        rec = q.first()
        return self._row_to_entity(rec) if rec else None

    # -------------------------
    # Commands
    # -------------------------
    def create(self, data: ProviderAccountData) -> ProviderAccountData:
        rec = ProviderAccountModel.create(
            party_id=data.party_id,
            provider=data.provider.value,
            env=data.env.value,
            provider_account_id=data.provider_account_id,
            public_key=data.public_key,
            secret_json_enc=data.secret_json_enc,   # string JSON o dict (si JSONField)
            status=data.status.value,
        )
        return self._row_to_entity(rec)

    def update(self, data: ProviderAccountData) -> Optional[ProviderAccountData]:
        if not data.id:
            raise ValueError("id is required for update")
        try:
            rec = ProviderAccountModel.get(ProviderAccountModel.id == data.id)
            rec.party_id = data.party_id
            rec.provider = data.provider.value
            rec.env = data.env.value
            rec.provider_account_id = data.provider_account_id
            rec.public_key = data.public_key
            rec.secret_json_enc = data.secret_json_enc
            rec.status = data.status.value
            rec.save()
            return self._row_to_entity(rec)
        except ProviderAccountModel.DoesNotExist:
            return None

    def delete(self, id_: int) -> bool:
        try:
            rec = ProviderAccountModel.get(ProviderAccountModel.id == id_)
            rec.delete_instance()
            return True
        except ProviderAccountModel.DoesNotExist:
            return False

    def enable(self, id_: int) -> bool:
        return self._set_status(id_, ProviderAccountStatus.ACTIVE)

    def disable(self, id_: int) -> bool:
        return self._set_status(id_, ProviderAccountStatus.DISABLED)

    def _set_status(self, id_: int, status: ProviderAccountStatus) -> bool:
        rows = (ProviderAccountModel
                .update(status=status.value)
                .where(ProviderAccountModel.id == id_)
                .execute())
        return rows > 0

    def rotate_secrets(self, id_: int, new_secret_json_enc: Union[str, Dict[str, Any]]) -> bool:
        # Acá normalmente querrías cifrar antes de guardar
        if isinstance(new_secret_json_enc, dict):
            new_secret_json_enc = json.dumps(new_secret_json_enc, ensure_ascii=False)
        rows = (ProviderAccountModel
                .update(secret_json_enc=new_secret_json_enc)
                .where(ProviderAccountModel.id == id_)
                .execute())
        return rows > 0

    def upsert_by_unique(self, data: ProviderAccountData) -> ProviderAccountData:
        """
        Garantiza unicidad por (provider, env, provider_account_id).
        Si existe: update; si no: create.
        """
        existing = self.get_by_unique(data.provider, data.env, data.provider_account_id)
        if existing:
            data.id = existing.id
            return self.update(data) or existing
        return self.create(data)

    # -------------------------
    # Búsquedas útiles / analytics
    # -------------------------
    def count_by_provider_env(self) -> List[Dict[str, Any]]:
        q = (ProviderAccountModel
             .select(
                 ProviderAccountModel.provider,
                 ProviderAccountModel.env,
                 fn.COUNT(ProviderAccountModel.id).alias("total")
             )
             .group_by(ProviderAccountModel.provider, ProviderAccountModel.env))
        out = []
        for r in q:
            out.append({
                "provider": r.provider,
                "env": r.env,
                "total": r.total
            })
        return out

    def dump_model(self, id_: int) -> Optional[Dict[str, Any]]:
        """Devuelve el registro crudo (útil para debug)."""
        try:
            rec = ProviderAccountModel.get(ProviderAccountModel.id == id_)
            d = model_to_dict(rec)
            return d
        except ProviderAccountModel.DoesNotExist:
            return None
