from enum import Enum


class ProviderEnum(Enum):
    MERCADOPAGO = "mercadopago"
    STRIPE = "stripe"
    PAYPAL = "paypal"
    OTHER = "other"


class EnvEnum(Enum):
    TEST = "test"
    PROD = "prod"


class ProviderCustomerStatus(Enum):
    ACTIVE = "active"
    DISABLED = "disabled"
