import datetime
import json
from peewee import (
    Model, AutoField, BigIntegerField, CharField, DateTimeField, TextField
)

# Si usas MySQL con JSON nativo y tienes playhouse:
try:
    from playhouse.mysql_ext import JSONField  # type: ignore
    HasJSON = True
except Exception:
    JSONField = TextField  # fallback a TEXT
    HasJSON = False

from shared.infrastructure.database import db  # igual que en tu ejemplo


class ProviderAccountModel(Model):
    id = AutoField(primary_key=True)

    party_id = BigIntegerField(null=False)

    provider = CharField(
        max_length=32,
        null=False,
        choices=[
            ("mercadopago", "mercadopago"),
            ("stripe", "stripe"),
            ("paypal", "paypal"),
            ("other", "other"),
        ],
    )

    env = CharField(
        max_length=8,
        null=False,
        choices=[("test", "test"), ("prod", "prod")],
        default="test",
    )

    provider_account_id = CharField(max_length=128, null=False)
    public_key = CharField(max_length=255, null=True)

    # JSON de credenciales (cifrado a nivel app o KMS). Si no tienes JSONField,
    # se serializa en TEXT.
    secret_json_enc = JSONField(null=True)

    status = CharField(
        max_length=16,
        null=False,
        choices=[("active", "active"), ("disabled", "disabled")],
        default="active",
    )

    created_at = DateTimeField(default=datetime.datetime.now, null=False)
    updated_at = DateTimeField(default=datetime.datetime.now, null=False)

    class Meta:
        database = db
        table_name = "provider_account"
        indexes = (
            # uq_provider_account (provider, env, provider_account_id)
            (("provider", "env", "provider_account_id"), True),
            # idx_pa_party (party_id)
            (("party_id",), False),
        )

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        # Si no hay JSONField real, asegura string JSON
        if not HasJSON and self.secret_json_enc is not None:
            if isinstance(self.secret_json_enc, (dict, list)):
                self.secret_json_enc = json.dumps(self.secret_json_enc, ensure_ascii=False)
            else:
                # intenta validar que sea JSON válido
                try:
                    json.loads(self.secret_json_enc)
                except Exception:
                    # como fallback, lo empaco como string JSON
                    self.secret_json_enc = json.dumps({"raw": str(self.secret_json_enc)})
        return super().save(*args, **kwargs)
