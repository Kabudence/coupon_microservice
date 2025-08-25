import datetime
from peewee import (
    Model, AutoField, BigIntegerField, CharField, IntegerField, SmallIntegerField,
    DateTimeField, TextField
)

from payment.provider.customer_sources.domain.valueobjects.enums import PaymentSourceType, PaymentSourceStatus
from payment.provider.provider_customer.domain.value_objects.enums import ProviderEnum, EnvEnum
from shared.infrastructure.database import db



class PaymentSourceModel(Model):
    id = AutoField(primary_key=True)

    # FK real existe en MySQL; aquí mantenemos BigIntegerField para simetría (como en ProviderCustomerModel)
    provider_customer_pk = BigIntegerField(null=False)

    provider = CharField(max_length=32, null=False, choices=[(e.value, e.value) for e in ProviderEnum])
    env = CharField(max_length=8, null=False, choices=[(e.value, e.value) for e in EnvEnum], default=EnvEnum.TEST.value)

    provider_source_id = CharField(max_length=128, null=True)  # puede ser NULL para wallet/account_money
    source_type = CharField(max_length=32, null=False, choices=[(e.value, e.value) for e in PaymentSourceType])

    brand = CharField(max_length=32, null=True)
    last_four = CharField(max_length=4, null=True)
    exp_month = IntegerField(null=True)
    exp_year = SmallIntegerField(null=True)
    holder_name = CharField(max_length=128, null=True)

    status = CharField(
        max_length=16,
        null=False,
        choices=[(e.value, e.value) for e in PaymentSourceStatus],
        default=PaymentSourceStatus.ACTIVE.value
    )

    created_at = DateTimeField(default=datetime.datetime.now, null=False)
    updated_at = DateTimeField(default=datetime.datetime.now, null=False)

    class Meta:
        database = db
        table_name = "payment_sources"
        indexes = (
            # lookup por customer
            (("provider_customer_pk",), False),
            # único por (customer, provider_source_id) — en MySQL, NULLs no chocan
            (("provider_customer_pk", "provider_source_id"), True),
        )

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super().save(*args, **kwargs)
