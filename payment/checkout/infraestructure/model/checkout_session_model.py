import datetime
from peewee import (
    Model, AutoField, BigIntegerField, CharField, TextField, DateTimeField
)

from shared.infrastructure.database import db


class CheckoutSessionModel(Model):
    id = AutoField(primary_key=True)

    # FK real existe en el DDL (orders.id). Aquí usamos BigInteger por simetría
    # con tu OrderModel. Si prefieres, puedes sustituir por ForeignKeyField.
    order_id = BigIntegerField(null=False)

    provider_session_id = CharField(max_length=128, null=False, unique=True)
    init_url = TextField(null=True)
    sandbox_url = TextField(null=True)
    expires_at = DateTimeField(null=True)

    created_at = DateTimeField(default=datetime.datetime.now, null=False)

    class Meta:
        database = db
        table_name = "checkout_sessions"
        indexes = (
            (("provider_session_id",), True),  # uq_session
            (("order_id",), False),            # idx_session_order
        )
