import datetime
from peewee import (
    Model, AutoField, CharField, DateTimeField
)
from shared.infrastructure.database import db


class CategoryModel(Model):
    id = AutoField(primary_key=True)

    nombre = CharField(max_length=120, unique=True, null=False)
    description = CharField(max_length=255, null=True)

    created_at = DateTimeField(default=datetime.datetime.now, null=False)
    updated_at = DateTimeField(default=datetime.datetime.now, null=False)

    class Meta:
        database = db
        table_name = 'coupon_category'  # evita choques con "category" genérico

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super().save(*args, **kwargs)
