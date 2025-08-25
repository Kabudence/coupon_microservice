from enum import Enum


class OrderStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PAID = "paid"
    FAILED = "failed"
    CANCELED = "canceled"


class PaymentFlow(Enum):
    API = "api"
    HOSTED = "hosted"   # Checkout Pro / redirección
