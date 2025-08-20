import datetime
from peewee import (
    Model, AutoField, BigIntegerField, CharField, DateTimeField, Index
)

from shared.infrastructure.database import db

# Opcional: si tienes NegocioModel, podrías usar ForeignKeyField en vez de BigIntegerField.

class AlianzaModel(Model):
    id = AutoField(primary_key=True)

    solicitante_negocio_id = BigIntegerField(null=False)
    receptor_negocio_id    = BigIntegerField(null=False)

    estado = CharField(
        max_length=16,
        null=False,
        default="PENDIENTE",  # PENDIENTE, ACEPTADA, RECHAZADA, CANCELADA, SUSPENDIDA
    )
    motivo = CharField(max_length=200, null=True)

    fecha_solicitud = DateTimeField(null=False, default=datetime.datetime.utcnow)
    fecha_respuesta = DateTimeField(null=True)

    class Meta:
        database = db
        table_name = "alianza"
        indexes = (
            # UNIQUE KEY uk_par (solicitante_negocio_id, receptor_negocio_id)
            (("solicitante_negocio_id", "receptor_negocio_id"), True),
            # INDEX idx_alianza_estado (estado)
            (("estado",), False),
        )

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)
