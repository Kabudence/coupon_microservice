from enum import Enum

class Provider(Enum):
    MERCADOPAGO = "mercadopago"
    STRIPE      = "stripe"
    PAYPAL      = "paypal"
    OTHER       = "other"

class Env(Enum):
    TEST = "test"
    PROD = "prod"

class RowStatus(Enum):
    ACTIVE   = "active"
    DISABLED = "disabled"
