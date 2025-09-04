import datetime
import json
from peewee import (
    Model, AutoField, CharField, IntegerField, BooleanField, DateTimeField, TextField
)

from payment.provider.provider_customer.domain.value_objects.enums import EnvEnum, ProviderEnum
from shared.infrastructure.database import db


class WebhookEventModel(Model):
    id = AutoField(primary_key=True)

    provider = CharField(max_length=32, null=False, choices=[(e.value, e.value) for e in ProviderEnum])
    env = CharField(max_length=8, null=False, choices=[(e.value, e.value) for e in EnvEnum])

    topic = CharField(max_length=64, null=True)
    action = CharField(max_length=64, null=True)
    resource_id = CharField(max_length=128, null=True)

    delivery_key = CharField(max_length=191, null=False)

    # Guardamos JSON como TEXT y lo (de)serializamos en el repo
    headers = TextField(null=True)
    body = TextField(null=True)

    signature_valid = BooleanField(null=True)
    http_status_sent = IntegerField(null=True)

    received_at = DateTimeField(default=datetime.datetime.now, null=False)
    processed_at = DateTimeField(null=True)

    class Meta:
        database = db
        table_name = "webhook_events"
        indexes = (
            # UNIQUE (provider, env, delivery_key)
            (("provider", "env", "delivery_key"), True),
            # búsqueda rápida por (provider, env, resource_id)
            (("provider", "env", "resource_id"), False),
        )

    # Helpers para (de)serializar JSON en TEXT automáticamente (opcional)
    @staticmethod
    def _dumps(obj):
        if obj is None:
            return None
        return json.dumps(obj, ensure_ascii=False)

    @staticmethod
    def _loads(txt):
        if not txt:
            return None
        try:
            return json.loads(txt)
        except Exception:
            return None
