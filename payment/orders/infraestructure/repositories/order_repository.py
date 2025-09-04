from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any

from peewee import IntegrityError

from payment.orders.domain.entities.order import OrderData
from payment.orders.domain.value_objects.enums import OrderStatus, PaymentFlow
from payment.orders.infraestructure.model.order_model import OrderModel
from payment.provider.provider_customer.domain.value_objects.enums import ProviderEnum, EnvEnum


class OrderRepository:
    # -----------------------
    # Helpers (enums & utils)
    # -----------------------
    @staticmethod
    def _enum_value(val, enum_cls):
        """
        Devuelve el .value si 'val' ya es Enum; acepta strings (value o name) y normaliza case-insensitive.
        Lanza ValueError si no matchea.
        """
        if val is None:
            return None
        if isinstance(val, enum_cls):
            return val.value
        s = str(val)
        # Intento directo por value
        try:
            return enum_cls(s).value
        except Exception:
            pass
        # Intento por name/value en case-insensitive
        s_low = s.lower()
        for e in enum_cls:
            if e.value.lower() == s_low or e.name.lower() == s_low:
                return e.value
        raise ValueError(f"valor inválido para {enum_cls.__name__}: {val}")

    @staticmethod
    def _status_value(val: OrderStatus | str) -> str:
        return OrderRepository._enum_value(val, OrderStatus)

    @staticmethod
    def _flow_value(val: PaymentFlow | str | None) -> Optional[str]:
        return OrderRepository._enum_value(val, PaymentFlow) if val is not None else None

    @staticmethod
    def _provider_value(val: ProviderEnum | str | None) -> Optional[str]:
        return OrderRepository._enum_value(val, ProviderEnum) if val is not None else None

    @staticmethod
    def _env_value(val: EnvEnum | str | None) -> Optional[str]:
        return OrderRepository._enum_value(val, EnvEnum) if val is not None else None

    # -----------------------
    # Mappers
    # -----------------------
    def _to_entity(self, rec: OrderModel) -> OrderData:
        return OrderData(
            id=rec.id,
            buyer_party_id=rec.buyer_party_id,
            seller_party_id=rec.seller_party_id,
            amount=Decimal(str(rec.amount)),
            currency=rec.currency,
            status=OrderStatus(rec.status),
            description=rec.description,
            metadata=OrderModel.loads_metadata(rec.metadata),
            flow=(PaymentFlow(rec.flow) if rec.flow else None),
            provider=(ProviderEnum(rec.provider) if rec.provider else None),
            env=(EnvEnum(rec.env) if rec.env else EnvEnum.TEST),
            provider_account_id=rec.provider_account_id,
            provider_payment_id=rec.provider_payment_id,
            idempotency_key=rec.idempotency_key,
            payment_type=rec.payment_type,
            method_brand=rec.method_brand,
            method_last_four=rec.method_last_four,
            paid_at=rec.paid_at,
            created_at=rec.created_at,
            updated_at=rec.updated_at,
        )

    # -----------------------
    # Queries
    # -----------------------
    def get_by_id(self, id_: int) -> Optional[OrderData]:
        try:
            rec = OrderModel.get(OrderModel.id == id_)
            return self._to_entity(rec)
        except OrderModel.DoesNotExist:
            return None

    def get_by_provider_payment(
        self, provider: ProviderEnum | str, env: EnvEnum | str, provider_payment_id: str
    ) -> Optional[OrderData]:
        provider_v = self._provider_value(provider)
        env_v = self._env_value(env)
        try:
            rec = (
                OrderModel.select()
                .where(
                    (OrderModel.provider == provider_v)
                    & (OrderModel.env == env_v)
                    & (OrderModel.provider_payment_id == provider_payment_id)
                )
            ).get()
            return self._to_entity(rec)
        except OrderModel.DoesNotExist:
            return None

    def get_by_idempotency(
        self, provider: ProviderEnum | str, env: EnvEnum | str, idempotency_key: str
    ) -> Optional[OrderData]:
        provider_v = self._provider_value(provider)
        env_v = self._env_value(env)
        try:
            rec = (
                OrderModel.select()
                .where(
                    (OrderModel.provider == provider_v)
                    & (OrderModel.env == env_v)
                    & (OrderModel.idempotency_key == idempotency_key)
                )
            ).get()
            return self._to_entity(rec)
        except OrderModel.DoesNotExist:
            return None

    def list_by_buyer(
        self, buyer_party_id: int, status: Optional[OrderStatus | str] = None, limit: int = 100, offset: int = 0
    ) -> List[OrderData]:
        q = OrderModel.select().where(OrderModel.buyer_party_id == buyer_party_id)
        if status:
            q = q.where(OrderModel.status == self._status_value(status))
        q = q.order_by(OrderModel.id.desc()).limit(limit).offset(offset)
        return [self._to_entity(r) for r in q]

    def list_by_seller(
        self, seller_party_id: int, status: Optional[OrderStatus | str] = None, limit: int = 100, offset: int = 0
    ) -> List[OrderData]:
        q = OrderModel.select().where(OrderModel.seller_party_id == seller_party_id)
        if status:
            q = q.where(OrderModel.status == self._status_value(status))
        q = q.order_by(OrderModel.id.desc()).limit(limit).offset(offset)
        return [self._to_entity(r) for r in q]

    def list_by_status(self, status: OrderStatus | str, limit: int = 100, offset: int = 0) -> List[OrderData]:
        q = (
            OrderModel.select()
            .where(OrderModel.status == self._status_value(status))
            .order_by(OrderModel.id.desc())
            .limit(limit)
            .offset(offset)
        )
        return [self._to_entity(r) for r in q]

    # -----------------------
    # Commands (mutaciones)
    # -----------------------
    def create(self, entity: OrderData) -> OrderData:
        try:
            rec = OrderModel.create(
                buyer_party_id=entity.buyer_party_id,
                seller_party_id=entity.seller_party_id,
                amount=str(entity.amount),
                currency=entity.currency,
                status=self._status_value(entity.status),
                description=entity.description,
                metadata=OrderModel.dumps_metadata(entity.metadata),
                flow=self._flow_value(entity.flow),
                provider=self._provider_value(entity.provider),
                env=self._env_value(entity.env) or EnvEnum.TEST.value,
                provider_account_id=entity.provider_account_id,
                provider_payment_id=entity.provider_payment_id,
                idempotency_key=entity.idempotency_key,
                payment_type=entity.payment_type,
                method_brand=entity.method_brand,
                method_last_four=entity.method_last_four,
                paid_at=entity.paid_at,
            )
            return self._to_entity(rec)
        except IntegrityError as e:
            # puede chocar con uq_order_provider_payment o uq_order_idem
            raise ValueError(f"conflicto de unicidad al crear order: {e}")

    def update(self, entity: OrderData) -> Optional[OrderData]:
        try:
            rec = OrderModel.get(OrderModel.id == entity.id)
            rec.buyer_party_id = entity.buyer_party_id
            rec.seller_party_id = entity.seller_party_id
            rec.amount = str(entity.amount)
            rec.currency = entity.currency
            rec.status = self._status_value(entity.status)
            rec.description = entity.description
            rec.metadata = OrderModel.dumps_metadata(entity.metadata)
            rec.flow = self._flow_value(entity.flow)
            rec.provider = self._provider_value(entity.provider)
            rec.env = self._env_value(entity.env) or EnvEnum.TEST.value
            rec.provider_account_id = entity.provider_account_id
            rec.provider_payment_id = entity.provider_payment_id
            rec.idempotency_key = entity.idempotency_key
            rec.payment_type = entity.payment_type
            rec.method_brand = entity.method_brand
            rec.method_last_four = entity.method_last_four
            rec.paid_at = entity.paid_at
            rec.save()
            return self._to_entity(rec)
        except OrderModel.DoesNotExist:
            return None
        except IntegrityError as e:
            raise ValueError(f"conflicto de unicidad al actualizar order: {e}")

    def set_checkout_context(
        self,
        order_id: int,
        flow: PaymentFlow | str,
        provider: ProviderEnum | str,
        env: EnvEnum | str,
        provider_account_id: Optional[int] = None,
        idempotency_key: Optional[str] = None,
        mark_processing: bool = True,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[OrderData]:
        """
        Adjunta contexto del proveedor en el arranque del cobro.
        Útil para API (idempotency) y HOSTED (preference previa).
        """
        try:
            rec = OrderModel.get(OrderModel.id == order_id)
        except OrderModel.DoesNotExist:
            return None

        rec.flow = self._flow_value(flow)
        rec.provider = self._provider_value(provider)
        rec.env = self._env_value(env) or EnvEnum.TEST.value
        rec.provider_account_id = provider_account_id
        rec.idempotency_key = idempotency_key

        meta = OrderModel.loads_metadata(rec.metadata)
        if extra_metadata:
            meta.update(extra_metadata)
        rec.metadata = OrderModel.dumps_metadata(meta)

        if mark_processing and rec.status == OrderStatus.PENDING.value:
            rec.status = OrderStatus.PROCESSING.value

        rec.save()
        return self._to_entity(rec)

    def mark_paid(
        self,
        order_id: int,
        provider_payment_id: str,
        payment_type: Optional[str] = None,
        method_brand: Optional[str] = None,
        method_last_four: Optional[str] = None,
        paid_at: Optional[datetime.datetime] = None,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[OrderData]:
        try:
            rec = OrderModel.get(OrderModel.id == order_id)
            rec.provider_payment_id = provider_payment_id
            rec.payment_type = payment_type
            rec.method_brand = method_brand
            rec.method_last_four = method_last_four
            rec.paid_at = paid_at or datetime.datetime.now()
            rec.status = OrderStatus.PAID.value

            meta = OrderModel.loads_metadata(rec.metadata)
            if extra_metadata:
                meta.update(extra_metadata)
            rec.metadata = OrderModel.dumps_metadata(meta)

            rec.save()
            return self._to_entity(rec)
        except OrderModel.DoesNotExist:
            return None
        except IntegrityError as e:
            raise ValueError(f"conflicto de unicidad (provider_payment_id/idempotency) al marcar paid: {e}")

    def mark_failed(
        self,
        order_id: int,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[OrderData]:
        try:
            rec = OrderModel.get(OrderModel.id == order_id)
            rec.status = OrderStatus.FAILED.value

            meta = OrderModel.loads_metadata(rec.metadata)
            if error_code:
                meta["error_code"] = error_code
            if error_message:
                meta["error_message"] = error_message
            if extra_metadata:
                meta.update(extra_metadata)

            rec.metadata = OrderModel.dumps_metadata(meta)
            rec.save()
            return self._to_entity(rec)
        except OrderModel.DoesNotExist:
            return None

    def cancel(self, order_id: int, reason: Optional[str] = None) -> Optional[OrderData]:
        try:
            rec = OrderModel.get(OrderModel.id == order_id)
            if rec.status == OrderStatus.PAID.value:
                # regla de negocio: no cancelar si ya está cobrada
                return self._to_entity(rec)

            rec.status = OrderStatus.CANCELED.value

            meta = OrderModel.loads_metadata(rec.metadata)
            if reason:
                meta["cancel_reason"] = reason
            rec.metadata = OrderModel.dumps_metadata(meta)

            rec.save()
            return self._to_entity(rec)
        except OrderModel.DoesNotExist:
            return None
