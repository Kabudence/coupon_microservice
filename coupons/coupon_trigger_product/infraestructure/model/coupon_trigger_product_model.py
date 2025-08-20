from peewee import (
    Model, ForeignKeyField, BigIntegerField, IntegerField, DecimalField,
    CompositeKey, CharField
)

from coupons.coupon.infraestructure.model.coupon_model import CouponModel
from shared.infrastructure.database import db


class CouponTriggerProductModel(Model):
    # Si tienes ProductModel, cámbialo por FK
    product_trigger_id = BigIntegerField(null=False)

    # PRODUCT | SERVICE (obligatorio)
    product_type = CharField(
        max_length=16,
        null=False,
        default="PRODUCT",
        choices=[("PRODUCT", "PRODUCT"), ("SERVICE", "SERVICE")]
    )

    coupon = ForeignKeyField(
        CouponModel,
        field=CouponModel.id,
        backref='trigger_products',
        on_delete='CASCADE',
        null=False
    )

    min_quantity = IntegerField(null=False, default=1)
    min_amount   = DecimalField(max_digits=12, decimal_places=2, auto_round=True, null=True)

    class Meta:
        database = db
        table_name = 'coupon_trigger_product'
        primary_key = CompositeKey('product_trigger_id', 'coupon')
        indexes = (
            (('coupon',), False),                # idx_ctp_coupon
            (('product_trigger_id',), False),    # idx_ctp_product_trigger
            (('product_type',), False),          # idx_ctp_product_type
        )
