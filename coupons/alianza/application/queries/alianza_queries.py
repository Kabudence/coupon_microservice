from __future__ import annotations

from typing import Optional, List

from coupons.alianza.domain.entities.alianza import AlianzaData, AlianzaEstado
from coupons.alianza.infraestructure.repositories.alianza_repository import AlianzaRepository


class AlianzaQueryService:
    def __init__(self, repo: AlianzaRepository):
        self.repo = repo

    def get_by_id(self, id_: int) -> Optional[AlianzaData]:
        return self.repo.get_by_id(id_)

    def list_all(self) -> List[AlianzaData]:
        return self.repo.get_all()

    def list_by_negocio(self, negocio_id: int) -> List[AlianzaData]:
        return self.repo.find_by_negocio(negocio_id)

    def pendientes_recibidas(self, negocio_id: int) -> List[AlianzaData]:
        return self.repo.find_pendientes_recibidas(negocio_id)

    def pendientes_enviadas(self, negocio_id: int) -> List[AlianzaData]:
        return self.repo.find_pendientes_enviadas(negocio_id)

    def activas(self, negocio_id: int) -> List[AlianzaData]:
        return self.repo.find_activas(negocio_id)

    def exists_between(self, a: int, b: int) -> Optional[AlianzaData]:
        return self.repo.exists_between(a, b)
