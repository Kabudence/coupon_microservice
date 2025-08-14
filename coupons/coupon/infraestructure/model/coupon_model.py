import datetime
from peewee import (
    Model, AutoField, BigIntegerField, CharField, BooleanField, IntegerField,
    DecimalField, DateTimeField, ForeignKeyField, Index
)

from coupons.coupon.domain.entities.coupon import CouponStatus
from coupons.coupons_type.infraestructure.model.coupon_type_model import CouponTypeModel
from coupons.discount_type.infraestructure.model.discount_type_model import DiscountTypeModel
from shared.infrastructure.database import db



class CouponModel(Model):
    id = AutoField(primary_key=True)

    business_id = BigIntegerField(null=False)             # FK -> business.id (use ForeignKeyField if you have BusinessModel)
    coupon_type = ForeignKeyField(CouponTypeModel, field=CouponTypeModel.id, null=True, backref='coupons')

    name = CharField(max_length=100, null=False)
    description = CharField(max_length=255, null=True)

    discount_type = ForeignKeyField(DiscountTypeModel, field=DiscountTypeModel.id, null=False, backref='coupons')
    value = DecimalField(max_digits=12, decimal_places=2, auto_round=True, null=False)
    max_discount = DecimalField(max_digits=12, decimal_places=2, auto_round=True, null=True)

    start_date = DateTimeField(null=False)                # UTC
    end_date = DateTimeField(null=False)                  # UTC

    max_uses = IntegerField(null=True)

    code = CharField(max_length=50, unique=True, null=True)
    event_name = CharField(max_length=100, null=True)

    is_shared_alliances = BooleanField(default=False, null=False)

    status = CharField(
        max_length=16,
        null=False,
        choices=[(e.value, e.value) for e in CouponStatus],
        default=CouponStatus.ACTIVE.value
    )

    created_at = DateTimeField(default=datetime.datetime.now, null=False)
    updated_at = DateTimeField(default=datetime.datetime.now, null=False)

    class Meta:
        database = db
        table_name = 'coupon'
        indexes = (
            (('business_id', 'status'), False),      # idx_coupon_business_status
            (('status', 'start_date', 'end_date'), False),  # idx_coupon_validity
            (('is_shared_alliances', 'status'), False),     # idx_coupon_shared
        )

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super().save(*args, **kwargs)
