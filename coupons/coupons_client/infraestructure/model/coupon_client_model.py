import datetime
from peewee import (
    Model, AutoField, BigIntegerField, CharField, DateTimeField
)
from shared.infrastructure.database import db

class CouponClientModel(Model):
    id = AutoField(primary_key=True)
    coupon_id = BigIntegerField(null=False)  # FK lógica a coupon.id
    client_id = BigIntegerField(null=False)
    code = CharField(max_length=64, null=False)
    status = CharField(max_length=16, null=False, default="ACTIVE")  # ACTIVE|USED|INACTIVE|EXPIRED
    valid_from = DateTimeField(null=True)
    valid_to = DateTimeField(null=True)
    used_at = DateTimeField(null=True)
    source_trigger_id = BigIntegerField(null=True)
    source_order_id = BigIntegerField(null=True)

    created_at = DateTimeField(default=datetime.datetime.now, null=False)
    updated_at = DateTimeField(default=datetime.datetime.now, null=False)

    class Meta:
        database = db
        table_name = "coupon_client"
        indexes = (
            (("client_id", "coupon_id", "code"), True),  # unique
            (("client_id", "status"), False),
        )

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super().save(*args, **kwargs)
