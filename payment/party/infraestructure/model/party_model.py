import datetime
from peewee import (
    Model, AutoField, BigIntegerField, CharField, DateTimeField
)
from shared.infrastructure.database import db


class PartyModel(Model):
    id = AutoField(primary_key=True)

    app_name     = CharField(max_length=32, null=False,
                             choices=[("emprende", "emprende"), ("fullventas", "fullventas")])
    subject_type = CharField(max_length=16, null=False,
                             choices=[("user", "user"), ("client", "client")])
    subject_id   = BigIntegerField(null=False)
    display_name = CharField(max_length=255, null=True)

    created_at = DateTimeField(default=datetime.datetime.now, null=False)
    updated_at = DateTimeField(default=datetime.datetime.now, null=False)

    class Meta:
        database = db
        table_name = "parties"
        indexes = (
            (("app_name", "subject_type", "subject_id"), True),  # UNIQUE
        )

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super().save(*args, **kwargs)
