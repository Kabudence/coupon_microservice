from __future__ import annotations

from typing import Optional, List

from peewee import IntegrityError

from payment.provider.customer_sources.domain.entities.payment_source import PaymentSourceData
from payment.provider.customer_sources.domain.valueobjects.enums import PaymentSourceStatus, PaymentSourceType
from payment.provider.customer_sources.infraestructure.model.payment_source_model import PaymentSourceModel
from payment.provider.provider_customer.domain.value_objects.enums import EnvEnum, ProviderEnum
from payment.provider.provider_customer.infraestructure.model.provider_customer_model import ProviderCustomerModel


class PaymentSourceRepository:
    # -----------------------
    # Mappers
    # -----------------------
    def _to_entity(self, rec: PaymentSourceModel) -> PaymentSourceData:
        return PaymentSourceData(
            id=rec.id,
            provider_customer_pk=rec.provider_customer_pk,
            provider=ProviderEnum(rec.provider),
            env=EnvEnum(rec.env),
            provider_source_id=rec.provider_source_id,
            source_type=PaymentSourceType(rec.source_type),
            brand=rec.brand,
            last_four=rec.last_four,
            exp_month=rec.exp_month,
            exp_year=rec.exp_year,
            holder_name=rec.holder_name,
            status=PaymentSourceStatus(rec.status),
            created_at=rec.created_at,
            updated_at=rec.updated_at,
        )

    # -----------------------
    # Helpers internos
    # -----------------------
    def _get_provider_of_customer(self, provider_customer_pk: int) -> tuple[str, str]:
        """
        Obtiene (provider, env) desde provider_customers para sincronizar columnas redundantes.
        """
        pc = ProviderCustomerModel.get(ProviderCustomerModel.id == provider_customer_pk)
        return pc.provider, pc.env

    # -----------------------
    # Queries
    # -----------------------
    def get_by_id(self, id_: int) -> Optional[PaymentSourceData]:
        try:
            rec = PaymentSourceModel.get(PaymentSourceModel.id == id_)
            return self._to_entity(rec)
        except PaymentSourceModel.DoesNotExist:
            return None

    def get_by_customer_and_source_id(
        self, provider_customer_pk: int, provider_source_id: str
    ) -> Optional[PaymentSourceData]:
        try:
            rec = (PaymentSourceModel
                   .select()
                   .where(
                       (PaymentSourceModel.provider_customer_pk == provider_customer_pk) &
                       (PaymentSourceModel.provider_source_id == provider_source_id)
                   )).get()
            return self._to_entity(rec)
        except PaymentSourceModel.DoesNotExist:
            return None

    def list_by_customer(self, provider_customer_pk: int, only_active: bool = True) -> List[PaymentSourceData]:
        q = (PaymentSourceModel
             .select()
             .where(PaymentSourceModel.provider_customer_pk == provider_customer_pk)
             .order_by(PaymentSourceModel.id.desc()))
        if only_active:
            q = q.where(PaymentSourceModel.status == PaymentSourceStatus.ACTIVE.value)
        return [self._to_entity(r) for r in q]

    def list_active_cards(self, provider_customer_pk: int) -> List[PaymentSourceData]:
        q = (PaymentSourceModel
             .select()
             .where(
                 (PaymentSourceModel.provider_customer_pk == provider_customer_pk) &
                 (PaymentSourceModel.status == PaymentSourceStatus.ACTIVE.value) &
                 (PaymentSourceModel.source_type == PaymentSourceType.CARD.value)
             )
             .order_by(PaymentSourceModel.id.desc()))
        return [self._to_entity(r) for r in q]

    def get_wallet(self, provider_customer_pk: int) -> Optional[PaymentSourceData]:
        """
        Retorna la wallet/account_money activa (si existe).
        """
        try:
            rec = (PaymentSourceModel
                   .select()
                   .where(
                       (PaymentSourceModel.provider_customer_pk == provider_customer_pk) &
                       (PaymentSourceModel.status == PaymentSourceStatus.ACTIVE.value) &
                       (PaymentSourceModel.source_type.in_([
                           PaymentSourceType.WALLET.value,
                           PaymentSourceType.ACCOUNT_MONEY.value,
                       ]))
                   )).get()
            return self._to_entity(rec)
        except PaymentSourceModel.DoesNotExist:
            return None

    # -----------------------
    # Commands (CRUD/Upserts)
    # -----------------------
    def create(self, entity: PaymentSourceData) -> PaymentSourceData:
        try:
            # Sincronizar provider/env desde provider_customers
            prov, env = self._get_provider_of_customer(entity.provider_customer_pk)

            rec = PaymentSourceModel.create(
                provider_customer_pk=entity.provider_customer_pk,
                provider=prov,
                env=env,
                provider_source_id=entity.provider_source_id,
                source_type=entity.source_type.value if hasattr(entity.source_type, "value") else str(entity.source_type),
                brand=(entity.brand.lower().strip() if entity.brand else None),
                last_four=entity.last_four,
                exp_month=entity.exp_month,
                exp_year=entity.exp_year,
                holder_name=entity.holder_name,
                status=entity.status.value if hasattr(entity.status, "value") else str(entity.status),
            )
            return self._to_entity(rec)
        except IntegrityError as e:
            raise ValueError(f"payment_source duplicado (provider_customer, provider_source_id): {e}")

    def update(self, entity: PaymentSourceData) -> Optional[PaymentSourceData]:
        try:
            rec = PaymentSourceModel.get(PaymentSourceModel.id == entity.id)
            # Sincronizar provider/env por si cambió el customer
            prov, env = self._get_provider_of_customer(entity.provider_customer_pk)

            rec.provider_customer_pk = entity.provider_customer_pk
            rec.provider = prov
            rec.env = env
            rec.provider_source_id = entity.provider_source_id
            rec.source_type = entity.source_type.value if hasattr(entity.source_type, "value") else str(entity.source_type)
            rec.brand = (entity.brand.lower().strip() if entity.brand else None)
            rec.last_four = entity.last_four
            rec.exp_month = entity.exp_month
            rec.exp_year = entity.exp_year
            rec.holder_name = entity.holder_name
            rec.status = entity.status.value if hasattr(entity.status, "value") else str(entity.status)
            rec.save()
            return self._to_entity(rec)
        except PaymentSourceModel.DoesNotExist:
            return None
        except IntegrityError as e:
            raise ValueError(f"conflicto de unicidad al actualizar payment_source: {e}")

    def delete(self, id_: int) -> bool:
        try:
            rec = PaymentSourceModel.get(PaymentSourceModel.id == id_)
            rec.delete_instance()
            return True
        except PaymentSourceModel.DoesNotExist:
            return False

    def soft_delete(self, id_: int) -> bool:
        try:
            rec = PaymentSourceModel.get(PaymentSourceModel.id == id_)
            rec.status = PaymentSourceStatus.DELETED.value
            rec.save()
            return True
        except PaymentSourceModel.DoesNotExist:
            return False

    # -----------------------
    # Upserts convenientes
    # -----------------------
    def upsert_card(
        self,
        provider_customer_pk: int,
        provider_source_id: str,
        brand: Optional[str],
        last_four: str,
        exp_month: int,
        exp_year: int,
        holder_name: Optional[str] = None,
        status: PaymentSourceStatus | str = PaymentSourceStatus.ACTIVE,
    ) -> PaymentSourceData:
        """
        Idempotente por (provider_customer_pk, provider_source_id). Actualiza metadatos si cambian.
        """
        existing = self.get_by_customer_and_source_id(provider_customer_pk, provider_source_id)
        if existing:
            changed = False
            for attr, val in [
                ("brand", (brand.lower().strip() if brand else None)),
                ("last_four", last_four),
                ("exp_month", exp_month),
                ("exp_year", exp_year),
                ("holder_name", holder_name),
            ]:
                if getattr(existing, attr) != val:
                    setattr(existing, attr, val)
                    changed = True
            if str(existing.status.value if hasattr(existing.status, "value") else existing.status) != \
               str(status.value if hasattr(status, "value") else status):
                existing.status = status
                changed = True
            return self.update(existing) if changed else existing

        # crear
        entity = PaymentSourceData(
            provider_customer_pk=provider_customer_pk,
            provider_source_id=provider_source_id,
            source_type=PaymentSourceType.CARD,
            brand=brand,
            last_four=last_four,
            exp_month=exp_month,
            exp_year=exp_year,
            holder_name=holder_name,
            status=status,
        )
        return self.create(entity)

    def upsert_wallet(
        self,
        provider_customer_pk: int,
        holder_name: Optional[str] = None,
        status: PaymentSourceStatus | str = PaymentSourceStatus.ACTIVE,
    ) -> PaymentSourceData:
        """
        Garantiza una entrada de wallet/account_money activa por customer.
        Usa source_type=ACCOUNT_MONEY y provider_source_id=NULL.
        """
        existing = self.get_wallet(provider_customer_pk)
        if existing:
            # solo actualiza status/holder si cambian
            changed = False
            if holder_name is not None and existing.holder_name != holder_name:
                existing.holder_name = holder_name
                changed = True
            if str(existing.status.value if hasattr(existing.status, "value") else existing.status) != \
               str(status.value if hasattr(status, "value") else status):
                existing.status = status
                changed = True
            return self.update(existing) if changed else existing

        entity = PaymentSourceData(
            provider_customer_pk=provider_customer_pk,
            provider_source_id=None,
            source_type=PaymentSourceType.ACCOUNT_MONEY,
            holder_name=holder_name,
            status=status,
        )
        return self.create(entity)

    # -----------------------
    # Helpers Mercado Pago
    # -----------------------
    def upsert_from_mp_card_json(
        self,
        provider_customer_pk: int,
        env: EnvEnum | str,
        mp_card: dict,
    ) -> PaymentSourceData:
        """
        Crea/actualiza un payment_source a partir del JSON de tarjeta de MP
        (ej. respuesta de POST /v1/customers/{id}/cards).
        Campos esperados:
          - id, first_six_digits, last_four_digits, expiration_month, expiration_year,
            cardholder: { name }, payment_method: { id } -> (brand)
        """
        card_id = mp_card.get("id")
        if not card_id:
            raise ValueError("mp_card sin 'id'")

        brand = None
        pm = mp_card.get("payment_method") or {}
        if "id" in pm and pm["id"]:
            brand = str(pm["id"]).lower()

        holder_name = None
        ch = mp_card.get("cardholder") or {}
        if "name" in ch:
            holder_name = ch["name"]

        last_four = mp_card.get("last_four_digits") or mp_card.get("last_four")
        exp_month = mp_card.get("expiration_month") or mp_card.get("exp_month")
        exp_year = mp_card.get("expiration_year") or mp_card.get("exp_year")

        return self.upsert_card(
            provider_customer_pk=provider_customer_pk,
            provider_source_id=str(card_id),
            brand=brand,
            last_four=str(last_four) if last_four else None,
            exp_month=int(exp_month) if exp_month is not None else None,
            exp_year=int(exp_year) if exp_year is not None else None,
            holder_name=holder_name,
            status=PaymentSourceStatus.ACTIVE,
        )
