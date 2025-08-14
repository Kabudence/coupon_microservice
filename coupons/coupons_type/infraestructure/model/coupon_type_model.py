from peewee import Model, AutoField, CharField, TextField, TimestampField
import datetime
from shared.infrastructure.database import db


class CouponTypeModel(Model):
    id = AutoField(primary_key=True)
    name = CharField(max_length=50, unique=True, null=False)
    description = CharField(max_length=150, null=True)
    created_at = TimestampField(default=datetime.datetime.now, null=False)

    class Meta:
        database = db
        table_name = 'coupon_type'
