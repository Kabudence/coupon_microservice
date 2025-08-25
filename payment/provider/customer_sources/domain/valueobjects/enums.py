from enum import Enum

class PaymentSourceType(Enum):
    CARD = "card"
    WALLET = "wallet"
    ACCOUNT_MONEY = "account_money"   # alias explícito para MP wallet
    BANK_TRANSFER = "bank_transfer"


class PaymentSourceStatus(Enum):
    ACTIVE = "active"
    DELETED = "deleted"