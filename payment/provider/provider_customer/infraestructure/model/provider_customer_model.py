import datetime
from peewee import (
    Model, AutoField, BigIntegerField, CharField, DateTimeField
)

from payment.provider.provider_customer.domain.value_objects.enums import ProviderCustomerStatus, EnvEnum, ProviderEnum
from shared.infrastructure.database import db



class ProviderCustomerModel(Model):
    id = AutoField(primary_key=True)

    party_id = BigIntegerField(null=False)  # FK lógico a parties.id (en DB está la FK real)
    provider = CharField(max_length=32, null=False, choices=[(e.value, e.value) for e in ProviderEnum])
    env = CharField(max_length=8, null=False, choices=[(e.value, e.value) for e in EnvEnum], default=EnvEnum.TEST.value)

    provider_customer_id = CharField(max_length=128, null=False)

    status = CharField(
        max_length=16,
        null=False,
        choices=[(e.value, e.value) for e in ProviderCustomerStatus],
        default=ProviderCustomerStatus.ACTIVE.value
    )

    created_at = DateTimeField(default=datetime.datetime.now, null=False)
    updated_at = DateTimeField(default=datetime.datetime.now, null=False)

    class Meta:
        database = db
        table_name = "provider_customers"
        indexes = (
            # UNIQUE (party_id, provider, env)
            (("party_id", "provider", "env"), True),
            # UNIQUE (provider, env, provider_customer_id)
            (("provider", "env", "provider_customer_id"), True),
            # lookup común por party
            (("party_id",), False),
        )

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super().save(*args, **kwargs)
