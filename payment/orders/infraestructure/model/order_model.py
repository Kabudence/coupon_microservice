import datetime
import json
from peewee import (
    Model, AutoField, BigIntegerField, CharField, DecimalField, DateTimeField, TextField
)

from payment.orders.domain.value_objects.enums import OrderStatus, PaymentFlow
from payment.provider.provider_customer.domain.value_objects.enums import ProviderEnum, EnvEnum
from shared.infrastructure.database import db



class OrderModel(Model):
    id = AutoField(primary_key=True)

    # relación negocio
    buyer_party_id = BigIntegerField(null=False)
    seller_party_id = BigIntegerField(null=False)

    # monto
    amount = DecimalField(max_digits=18, decimal_places=2, auto_round=True, null=False)
    currency = CharField(max_length=3, null=False, default="PEN")

    # estado
    status = CharField(
        max_length=16,
        null=False,
        choices=[(e.value, e.value) for e in OrderStatus],
        default=OrderStatus.PENDING.value
    )

    # metadata negocio
    description = CharField(max_length=255, null=True)
    metadata = TextField(null=True)  # JSON en texto

    # integración con pasarela
    flow = CharField(max_length=16, null=True, choices=[(e.value, e.value) for e in PaymentFlow])
    provider = CharField(max_length=32, null=True, choices=[(e.value, e.value) for e in ProviderEnum])
    env = CharField(max_length=8, null=True, choices=[(e.value, e.value) for e in EnvEnum], default=EnvEnum.TEST.value)

    provider_account_id = BigIntegerField(null=True)
    provider_payment_id = CharField(max_length=128, null=True)
    idempotency_key = CharField(max_length=191, null=True)

    # resumen del método de pago
    payment_type = CharField(max_length=32, null=True)
    method_brand = CharField(max_length=32, null=True)
    method_last_four = CharField(max_length=4, null=True)

    # timestamps
    paid_at = DateTimeField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now, null=False)
    updated_at = DateTimeField(default=datetime.datetime.now, null=False)

    class Meta:
        database = db
        table_name = "orders"
        indexes = (
            (("buyer_party_id",), False),
            (("seller_party_id",), False),
            (("status", "created_at"), False),
            (("provider", "env"), False),
            (("created_at",), False),
            # únicas (coinciden con el DDL)
            (("provider", "env", "provider_payment_id"), True),
            (("provider", "env", "idempotency_key"), True),
        )

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super().save(*args, **kwargs)

    # helpers JSON
    @staticmethod
    def dumps_metadata(meta_dict):
        if meta_dict is None:
            return None
        return json.dumps(meta_dict, ensure_ascii=False)

    @staticmethod
    def loads_metadata(meta_txt):
        if not meta_txt:
            return {}
        try:
            return json.loads(meta_txt)
        except Exception:
            return {}
